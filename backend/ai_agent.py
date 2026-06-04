import os
import pandas as pd
import random
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def explain_discrepancies():
    print("🤖 Starting AI Anomaly Explanation (V2 Postgres Mode)...")
    
    try:
        engine = create_engine("postgresql://postgres:password@localhost:5432/reconciler")
        df = pd.read_sql('SELECT * FROM "ReconciliationResult" WHERE "aiExplanation" = \'\' LIMIT 15', engine)
    except Exception as e:
        print(f"❌ ERROR: Failed to read from Postgres: {e}")
        return
        
    if df.empty:
        print("✅ No discrepancies to analyze!")
        return

    print(f"📄 Found {len(df)} discrepancies to analyze.")
    
    with engine.begin() as conn:
        for index, row in df.iterrows():
            print(f"Mocking Analysis for Order {row['orderId']}...")
            if row['matchStatus'] == "MISSING_IN_GATEWAY":
                explanation = "The user initiated the order but closed the gateway tab before completing the payment."
            elif row['matchStatus'] == "ORPHAN_GATEWAY_TXN":
                explanation = "This transaction was settled by the gateway but the corresponding order cannot be found in our internal database."
            elif row['matchStatus'] == "FUZZY_MATCH_FEE_ERROR":
                explanation = "The discrepancy is exactly equal to the standard gateway fee, meaning the gross amount was recorded incorrectly."
            elif row['matchStatus'] == "AMOUNT_MISMATCH":
                explanation = f"The gateway settled ${row['grossAmount']} instead of ${row['amount']}, which usually indicates a partial refund was issued."
            else:
                explanation = "The AI identified an unknown anomaly requiring manual review."
                
            print(f"  -> AI: {explanation}")
            stmt = text('UPDATE "ReconciliationResult" SET "aiExplanation" = :exp WHERE "id" = :rid')
            conn.execute(stmt, {"exp": explanation, "rid": row['id']})
            
    print("✅ AI Analysis complete! Saved to PostgreSQL.")

if __name__ == "__main__":
    explain_discrepancies()
