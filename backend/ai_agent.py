import os
import pandas as pd
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

def explain_discrepancies():
    print("🤖 Starting AI Anomaly Explanation...")
    
    try:
        df = pd.read_csv("data/discrepancies_for_ai.csv")
    except FileNotFoundError:
        print("❌ ERROR: data/discrepancies_for_ai.csv not found. Run reconcile.py first.")
        return
        
    if df.empty:
        print("✅ No discrepancies to analyze!")
        return

    print(f"📄 Found {len(df)} discrepancies to analyze.")
    explanations = []
    
    # We will process a small batch of 10 rows for the demo
    demo_df = df.head(10).copy()
    
    if API_KEY and API_KEY != "your_api_key_here":
        print("✅ Gemini API Key found! Using real AI...")
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_instruction = (
            "You are an expert Financial Operations Analyst. "
            "I will give you a discrepancy from a payment reconciliation process. "
            "The standard payment gateway fee is 2.9% + $0.30. "
            "Analyze the provided row and give a concise, one-sentence explanation of what likely went wrong."
        )
        
        for index, row in demo_df.iterrows():
            print(f"Analyzing Order {row['order_id']}...")
            prompt = f"{system_instruction}\n\nRow Data:\nOrder ID: {row['order_id']}\nInternal Expected Amount: ${row['amount']}\nGateway Gross Amount: ${row['gross_amount']}\nGateway Fee: ${row['fee_amount']}\nGateway Net Settled: ${row['net_settled']}\nSystem Matched Status: {row['match_status']}\n\nProvide a concise, 1-sentence explanation for this discrepancy."
            
            try:
                response = model.generate_content(prompt)
                explanation = response.text.strip()
                print(f"  -> AI: {explanation}")
                explanations.append(explanation)
            except Exception as e:
                print(f"  -> Error calling Gemini: {e}")
                explanations.append("Failed to generate explanation due to API error.")
    else:
        print("⚠️ No Gemini API Key found. Using MOCK AI explanations so we can proceed to the dashboard UI...")
        
        # Fallback to mock explanations based on the match status
        for index, row in demo_df.iterrows():
            print(f"Mocking Analysis for Order {row['order_id']}...")
            if row['match_status'] == "MISSING_IN_GATEWAY":
                exps = [
                    "This transaction exists in our DB but was never processed by the gateway, likely a failed webhook or abandoned checkout.",
                    "The user initiated the order but closed the gateway tab before completing the payment."
                ]
                explanation = random.choice(exps)
            elif row['match_status'] == "ORPHAN_GATEWAY_TXN":
                explanation = "This transaction was settled by the gateway but the corresponding order cannot be found in our internal database."
            elif row['match_status'] == "FUZZY_MATCH_FEE_ERROR":
                explanation = "The discrepancy is exactly equal to the standard gateway fee, meaning the gross amount was recorded incorrectly."
            elif row['match_status'] == "AMOUNT_MISMATCH":
                explanation = f"The gateway settled ${row['gross_amount']} instead of ${row['amount']}, which usually indicates a partial refund was issued."
            else:
                explanation = "The AI identified an unknown anomaly requiring manual review."
                
            print(f"  -> Mock AI: {explanation}")
            explanations.append(explanation)
            
    demo_df["ai_explanation"] = explanations
    
    # Save the output
    demo_df.to_csv("data/ai_explained_discrepancies.csv", index=False)
    print("✅ AI Analysis complete! Saved to data/ai_explained_discrepancies.csv")

if __name__ == "__main__":
    explain_discrepancies()
