import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from google import genai

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None

def explain_discrepancies():
    print("🤖 Starting AI Anomaly Explanation (V2 Postgres Mode)...")
    
    if not model:
        print("❌ ERROR: GEMINI_API_KEY is missing. Please set it in .env")
        return

    try:
        engine = create_engine("postgresql://postgres:password@localhost:5432/reconciler")
        df = pd.read_sql('SELECT * FROM "ReconciliationResult" WHERE "aiExplanation" = \'\'', engine)
    except Exception as e:
        print(f"❌ ERROR: Failed to read from Postgres: {e}")
        return
        
    if df.empty:
        print("✅ No discrepancies to analyze!")
        return

    print(f"📄 Found {len(df)} discrepancies to analyze.")
    
    with engine.begin() as conn:
        for index, row in df.iterrows():
            print(f"Analyzing Order {row['orderId']} with Gemini...")
            
            prompt = f"""
            Analyze the following financial reconciliation discrepancy and provide a short, 1-sentence explanation of what likely happened.
            
            Order ID: {row['orderId']}
            Internal System Amount: {row['amount']}
            Gateway Settled Amount: {row['grossAmount']}
            Match Status: {row['matchStatus']}
            
            Explanation:
            """
            
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                explanation = response.text.strip()
            except Exception as e:
                print(f"  -> Error calling Gemini: {e}")
                explanation = "AI analysis failed due to API error."

            print(f"  -> AI: {explanation}")
            stmt = text('UPDATE "ReconciliationResult" SET "aiExplanation" = :exp WHERE "id" = :rid')
            conn.execute(stmt, {"exp": explanation, "rid": row['id']})
            
    print("✅ AI Analysis complete! Saved to PostgreSQL.")

if __name__ == "__main__":
    explain_discrepancies()
