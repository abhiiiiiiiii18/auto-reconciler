import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from openai import OpenAI

load_dotenv()

# Connect to the local Ollama instance using the OpenAI-compatible endpoint
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'  # required but unused by Ollama
)

def explain_discrepancies():
    print("🤖 Starting AI Anomaly Explanation (Local Ollama Mode)...")

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
            print(f"Analyzing Order {row['orderId']} with Local Qwen...")
            
            prompt = f"""
            Analyze the following financial reconciliation discrepancy and provide a short, 1-sentence explanation of what likely happened.
            
            Order ID: {row['orderId']}
            Internal System Amount: {row['amount']}
            Gateway Settled Amount: {row['grossAmount']}
            Match Status: {row['matchStatus']}
            
            Explanation:
            """
            
            try:
                response = client.chat.completions.create(
                    model='qwen2.5:7b',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                explanation = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"  -> Error calling local model: {e}")
                explanation = "AI analysis failed due to local API error."

            print(f"  -> AI: {explanation}")
            stmt = text('UPDATE "ReconciliationResult" SET "aiExplanation" = :exp WHERE "id" = :rid')
            conn.execute(stmt, {"exp": explanation, "rid": row['id']})
            
    print("✅ Local AI Analysis complete! Saved to PostgreSQL.")

if __name__ == "__main__":
    explain_discrepancies()

