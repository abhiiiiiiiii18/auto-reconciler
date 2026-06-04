import pandas as pd
import sys
from sqlalchemy import create_engine
import uuid
import datetime

def run_reconciliation():
    print("🚀 Starting Reconciliation Engine (V2 Postgres Mode)...")
    
    # 1. Ingestion from Postgres
    try:
        engine = create_engine("postgresql://postgres:password@localhost:5432/reconciler")
        
        print("Connecting to PostgreSQL...")
        df_internal = pd.read_sql("SELECT * FROM \"InternalOrder\"", engine)
        df_gateway = pd.read_sql("SELECT * FROM \"GatewayTransaction\"", engine)
        
    except Exception as e:
        print(f"❌ ERROR: Failed to connect or read from PostgreSQL - {e}")
        print("Falling back to V1 CSV mode...")
        # Fallback for UI if DB isn't seeded
        df_internal = pd.read_csv("data/internal_orders.csv")
        df_gateway = pd.read_csv("data/razorpay_settlement_report.csv")
        df_internal = df_internal.rename(columns={"order_id": "orderId", "currency": "currency", "status": "status", "created_at": "createdAt"})
        df_gateway = df_gateway.rename(columns={"txn_id": "gatewayTxnId", "order_id": "orderRefId", "amount": "grossAmount", "fee": "feeAmount", "settled_amount": "netSettled"})
        
    print(f"📊 Ingested {len(df_internal)} Internal Orders and {len(df_gateway)} Gateway Transactions.")
    
    if len(df_internal) == 0:
        print("⚠️ No data in Database. Please run 'python3 generate_mock_data.py' to seed PostgreSQL.")
        return
    
    # 2. Exact Match
    df_merged = pd.merge(
        df_internal, 
        df_gateway, 
        left_on="orderId", 
        right_on="orderRefId", 
        how="outer", 
        indicator=True
    )
    
    exact_matches = df_merged[
        (df_merged["_merge"] == "both") & 
        (df_merged["amount"] == df_merged["grossAmount"])
    ].copy()
    exact_matches["matchStatus"] = "EXACT_MATCH"
    
    # 3. Fuzzy Match & Discrepancy Detection
    discrepancies = df_merged[~df_merged.index.isin(exact_matches.index)].copy()
    
    def categorize_discrepancy(row):
        if row["_merge"] == "left_only":
            return "MISSING_IN_GATEWAY"
        elif row["_merge"] == "right_only":
            return "ORPHAN_GATEWAY_TXN"
        elif pd.notna(row["amount"]) and pd.notna(row["grossAmount"]):
            if abs((row["amount"] - row["feeAmount"]) - row["grossAmount"]) < 0.01:
                return "FUZZY_MATCH_FEE_ERROR"
            return "AMOUNT_MISMATCH"
        return "UNKNOWN_ERROR"

    discrepancies["matchStatus"] = discrepancies.apply(categorize_discrepancy, axis=1)
    
    columns_to_keep = [
        "orderId", "gatewayTxnId", "amount", "grossAmount", 
        "feeAmount", "netSettled", "matchStatus"
    ]
    final_discrepancies = discrepancies[columns_to_keep].copy()
    
    # Rename columns back to snake_case for the legacy AI script & Next.js UI
    final_discrepancies = final_discrepancies.rename(columns={
        "orderId": "order_id",
        "gatewayTxnId": "gateway_txn_id",
        "grossAmount": "gross_amount",
        "feeAmount": "fee_amount",
        "netSettled": "net_settled",
        "matchStatus": "match_status"
    })
    
    print(f"✅ Exact Matches: {len(exact_matches)}")
    print(f"⚠️ Discrepancies Found: {len(final_discrepancies)}")
    
    # Save the discrepancies for the AI to review
    final_discrepancies.to_csv("data/discrepancies_for_ai.csv", index=False)
    print("📁 Discrepancies saved to data/discrepancies_for_ai.csv for AI analysis.")
    
    return final_discrepancies

if __name__ == "__main__":
    run_reconciliation()
