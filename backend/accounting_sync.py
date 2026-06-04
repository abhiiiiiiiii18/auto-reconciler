import sys
import time
from sqlalchemy import create_engine, text

def push_to_accounting(order_id):
    print(f"🔄 Preparing Journal Entry for Order ID: {order_id}")
    time.sleep(1) # Simulate API latency
    
    # Normally we'd use OAuth2 here to hit https://api.xero.com or https://quickbooks.api.intuit.com
    # with a payload resolving the variance to an expense account.
    
    print("📡 Sending Journal Entry to Accounting API (Mock)...")
    time.sleep(1.5)
    
    # 1. Update the PostgreSQL record to mark it as RESOLVED
    try:
        engine = create_engine("postgresql://postgres:password@localhost:5432/reconciler")
        with engine.begin() as conn:
            stmt = text("UPDATE \"ReconciliationResult\" SET \"matchStatus\" = 'RESOLVED_IN_ACCOUNTING' WHERE \"orderId\" = :order_id")
            result = conn.execute(stmt, {"order_id": order_id})
            
            if result.rowcount > 0:
                print("✅ Successfully posted to Accounting Ledger and updated local DB.")
            else:
                print(f"⚠️ Warning: Could not find order ID {order_id} in Database to update.")
    except Exception as e:
        print(f"❌ ERROR: Database update failed - {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 accounting_sync.py <order_id>")
        sys.exit(1)
        
    push_to_accounting(sys.argv[1])
