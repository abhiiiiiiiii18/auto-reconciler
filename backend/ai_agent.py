import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: GEMINI_API_KEY is not set in the environment or .env file.")
    print("Please create a .env file in the backend folder and add your GEMINI_API_KEY.")
    exit(1)

genai.configure(api_key=API_KEY)

# Use Gemini 1.5 Flash - extremely fast and perfect for tabular reasoning
model = genai.GenerativeModel('gemini-1.5-flash')

def explain_discrepancies():
    print("🤖 Starting Gemini AI Anomaly Explanation...")
    
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

    # System prompt describing the domain
    system_instruction = (
        "You are an expert Financial Operations Analyst. "
        "I will give you a discrepancy from a payment reconciliation process. "
        "The standard payment gateway fee is 2.9% + $0.30. "
        "Analyze the provided row and give a concise, one-sentence explanation of what likely went wrong "
        "(e.g., 'The $5.00 discrepancy is likely due to a partial refund.', "
        "'This transaction is missing entirely from the gateway, indicating a potential webhook failure.')"
    )
    
    # We will process a small batch of 10 rows for the demo to avoid waiting too long
    # In production, we would use Gemini's batch API or larger prompts with JSON output.
    demo_df = df.head(10).copy()
    
    for index, row in demo_df.iterrows():
        print(f"Analyzing Order {row['order_id']}...")
        
        prompt = f"""
        {system_instruction}
        
        Row Data:
        Order ID: {row['order_id']}
        Internal Expected Amount: ${row['amount']}
        Gateway Gross Amount: ${row['gross_amount']}
        Gateway Fee: ${row['fee_amount']}
        Gateway Net Settled: ${row['net_settled']}
        System Matched Status: {row['match_status']}
        
        Provide a concise, 1-sentence explanation for this discrepancy.
        """
        
        try:
            response = model.generate_content(prompt)
            explanation = response.text.strip()
            print(f"  -> AI: {explanation}")
            explanations.append(explanation)
        except Exception as e:
            print(f"  -> Error calling Gemini: {e}")
            explanations.append("Failed to generate explanation due to API error.")
            
    demo_df["ai_explanation"] = explanations
    
    # Save the output
    demo_df.to_csv("data/ai_explained_discrepancies.csv", index=False)
    print("✅ AI Analysis complete! Saved to data/ai_explained_discrepancies.csv")

if __name__ == "__main__":
    explain_discrepancies()
