import pandas as pd
import numpy as np
import sys
from gateway_parsers import get_parser

def run_reconciliation(gateway_name="razorpay"):
    print(f"🚀 Starting Reconciliation Engine for gateway: {gateway_name.upper()}...")
    
    # 1. Ingestion
    df_internal = pd.read_csv("data/internal_orders.csv")
    
    # Select parser and file
    filepath = f"data/{gateway_name.lower()}_settlement_report.csv"
    try:
        parser = get_parser(gateway_name)
        df_gateway = parser.parse(filepath)
    except Exception as e:
        print(f"❌ ERROR: Failed to parse gateway file - {e}")
        return
    
    print(f"📊 Ingested {len(df_internal)} Internal Orders and {len(df_gateway)} Gateway Transactions.")
    
    # 2. Exact Match (on Order ID and Amount)
    # Note: Gateway parsers map the id to 'internal_order_id'
    df_merged = pd.merge(
        df_internal, 
        df_gateway, 
        left_on="order_id", 
        right_on="internal_order_id", 
        how="outer", 
        indicator=True
    )
    
    exact_matches = df_merged[
        (df_merged["_merge"] == "both") & 
        (df_merged["amount"] == df_merged["gross_amount"])
    ].copy()
    exact_matches["match_status"] = "EXACT_MATCH"
    
    # 3. Fuzzy Match & Discrepancy Detection
    discrepancies = df_merged[~df_merged.index.isin(exact_matches.index)].copy()
    
    def categorize_discrepancy(row):
        if row["_merge"] == "left_only":
            return "MISSING_IN_GATEWAY"
        elif row["_merge"] == "right_only":
            return "ORPHAN_GATEWAY_TXN"
        elif row["amount"] != row["gross_amount"]:
            # Fuzzy check: If the difference is exactly the fee amount, it's a net/gross mismatch error
            if abs((row["amount"] - row["fee_amount"]) - row["gross_amount"]) < 0.01:
                return "FUZZY_MATCH_FEE_ERROR"
            return "AMOUNT_MISMATCH"
        return "UNKNOWN_ERROR"

    discrepancies["match_status"] = discrepancies.apply(categorize_discrepancy, axis=1)
    
    columns_to_keep = [
        "order_id", "gateway_txn_id", "amount", "gross_amount", 
        "fee_amount", "net_settled", "match_status"
    ]
    final_discrepancies = discrepancies[columns_to_keep]
    
    print(f"✅ Exact Matches: {len(exact_matches)}")
    print(f"⚠️ Discrepancies Found: {len(final_discrepancies)}")
    
    final_discrepancies.to_csv("data/discrepancies_for_ai.csv", index=False)
    print("📁 Discrepancies saved to data/discrepancies_for_ai.csv for AI analysis.")
    
    return final_discrepancies

if __name__ == "__main__":
    gw = sys.argv[1] if len(sys.argv) > 1 else "razorpay"
    run_reconciliation(gw)
