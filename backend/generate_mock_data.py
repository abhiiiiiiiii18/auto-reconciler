import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid
import os

# 1. Generate Internal Orders
NUM_ORDERS = 1000
start_date = datetime.now() - timedelta(days=30)

orders = []
gateway_txns = []

for i in range(NUM_ORDERS):
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    amount = round(random.uniform(10.0, 500.0), 2)
    created_at = start_date + timedelta(days=random.randint(0, 29), hours=random.randint(0, 23))
    
    orders.append({
        "order_id": order_id,
        "amount": amount,
        "currency": "USD",
        "status": "PAID",
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Simulate Gateway Record Base
    rand_val = random.random()
    fee = round(amount * 0.029 + 0.30, 2)
    
    base_txn = {
        "gateway_txn_id": f"txn_{uuid.uuid4().hex[:12]}",
        "order_ref_id": order_id,
        "gross_amount": amount,
        "fee_amount": fee,
        "net_settled": round(amount - fee, 2),
        "settlement_date": (created_at + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "SETTLED"
    }
    
    if rand_val > 0.05:
        # Perfect Match
        gateway_txns.append(base_txn)
    elif rand_val > 0.03:
        # Amount mismatch anomaly
        base_txn["gross_amount"] = round(amount - 5.00, 2)
        base_txn["net_settled"] = round(amount - 5.00 - fee, 2)
        gateway_txns.append(base_txn)
    elif rand_val > 0.01:
        # Missing order ID in gateway
        base_txn["order_ref_id"] = ""
        gateway_txns.append(base_txn)
    else:
        # Missing entirely from gateway
        pass

# Orphan row
gateway_txns.append({
    "gateway_txn_id": f"txn_{uuid.uuid4().hex[:12]}",
    "order_ref_id": "ORD-UNKNOWN",
    "gross_amount": 99.99,
    "fee_amount": 3.20,
    "net_settled": 96.79,
    "settlement_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "status": "SETTLED"
})

os.makedirs("data", exist_ok=True)
df_orders = pd.DataFrame(orders)
df_orders.to_csv("data/internal_orders.csv", index=False)

df_base = pd.DataFrame(gateway_txns)

# Format for Razorpay
df_razorpay = pd.DataFrame({
    "txn_id": df_base["gateway_txn_id"],
    "order_id": df_base["order_ref_id"],
    "amount": df_base["gross_amount"],
    "fee": df_base["fee_amount"],
    "tax": 0,
    "settled_amount": df_base["net_settled"],
    "status": df_base["status"]
})
df_razorpay.to_csv("data/razorpay_settlement_report.csv", index=False)

# Format for Stripe
df_stripe = pd.DataFrame({
    "id": df_base["gateway_txn_id"],
    "description": df_base["order_ref_id"],
    "Amount": df_base["gross_amount"],
    "Fee": df_base["fee_amount"],
    "Net": df_base["net_settled"],
    "Status": df_base["status"]
})
df_stripe.to_csv("data/stripe_settlement_report.csv", index=False)

# Format for PayPal
df_paypal = pd.DataFrame({
    "Transaction ID": df_base["gateway_txn_id"],
    "Invoice ID": df_base["order_ref_id"],
    "Gross": df_base["gross_amount"],
    "Fee": df_base["fee_amount"],
    "Net": df_base["net_settled"],
    "Type": df_base["status"]
})
df_paypal.to_csv("data/paypal_settlement_report.csv", index=False)

print(f"✅ Generated {len(orders)} internal orders")
print(f"✅ Generated {len(gateway_txns)} gateway transactions for Razorpay, Stripe, and PayPal.")
print("📁 Saved to: backend/data/")

print("\n🚀 Pushing Mock Data to PostgreSQL Database for V2 Feature...")
try:
    from sqlalchemy import create_engine
    engine = create_engine("postgresql://postgres:password@localhost:5432/reconciler")
    
    # Push Internal Orders
    db_orders = []
    for o in orders:
        db_orders.append({
            "id": str(uuid.uuid4()),
            "orderId": o["order_id"],
            "amount": o["amount"],
            "currency": o["currency"],
            "status": o["status"],
            "createdAt": o["created_at"]
        })
    pd.DataFrame(db_orders).to_sql("InternalOrder", engine, if_exists="append", index=False)
    
    # Push Gateway Transactions (Simulating Webhooks)
    db_txns = []
    for g in gateway_txns:
        db_txns.append({
            "id": str(uuid.uuid4()),
            "gatewayTxnId": g["gateway_txn_id"],
            "gateway": "stripe", # Mocking everything as stripe in DB
            "orderRefId": g["order_ref_id"],
            "grossAmount": g["gross_amount"],
            "feeAmount": g["fee_amount"],
            "netSettled": g["net_settled"],
            "settlementDate": g["settlement_date"],
            "status": g["status"],
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    pd.DataFrame(db_txns).to_sql("GatewayTransaction", engine, if_exists="append", index=False)
    print("✅ Successfully pushed mock data to PostgreSQL!")
except Exception as e:
    print(f"⚠️ Could not push to Postgres (is it running?): {e}")
