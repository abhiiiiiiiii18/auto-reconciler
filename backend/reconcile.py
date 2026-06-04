import pandas as pd
import numpy as np

def run_reconciliation():
    print("🚀 Starting Reconciliation Engine...")
    
    # 1. Ingestion
    df_internal = pd.read_csv("data/internal_orders.csv")
    df_gateway = pd.read_csv("data/razorpay_settlement_report.csv")
    
    print(f"📊 Ingested {len(df_internal)} Internal Orders and {len(df_gateway)} Gateway Transactions.")
    
    # 2. Exact Match (on Order ID and Amount)
    # Merge on the common key
    df_merged = pd.merge(
        df_internal, 
        df_gateway, 
        left_on="order_id", 
        right_on="order_ref_id", 
        how="outer", 
        indicator=True
    )
    
    # Analyze the merge
    exact_matches = df_merged[
        (df_merged["_merge"] == "both") & 
        (df_merged["amount"] == df_merged["gross_amount"])
    ].copy()
    exact_matches["match_status"] = "EXACT_MATCH"
    
    # 3. Fuzzy Match & Discrepancy Detection
    discrepancies = df_merged[~df_merged.index.isin(exact_matches.index)].copy()
    
    # Categorize discrepancies
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
    
    # Clean up output
    columns_to_keep = [
        "order_id", "gateway_txn_id", "amount", "gross_amount", 
        "fee_amount", "net_settled", "match_status"
    ]
    
    final_discrepancies = discrepancies[columns_to_keep]
    
    print(f"✅ Exact Matches: {len(exact_matches)}")
    print(f"⚠️ Discrepancies Found: {len(final_discrepancies)}")
    
    # Save the discrepancies for the AI to review
    final_discrepancies.to_csv("data/discrepancies_for_ai.csv", index=False)
    print("📁 Discrepancies saved to data/discrepancies_for_ai.csv for Gemini analysis.")
    
    return final_discrepancies

if __name__ == "__main__":
    run_reconciliation()
