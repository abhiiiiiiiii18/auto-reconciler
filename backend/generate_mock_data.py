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
    
    # Internal DB Record
    orders.append({
        "order_id": order_id,
        "amount": amount,
        "currency": "USD",
        "status": "PAID",
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Simulate Gateway Record (Razorpay)
    # 95% perfect match, 5% anomalies
    rand_val = random.random()
    
    if rand_val > 0.05:
        # Perfect Match
        fee = round(amount * 0.029 + 0.30, 2)
        net = round(amount - fee, 2)
        gateway_txns.append({
            "gateway_txn_id": f"txn_{uuid.uuid4().hex[:12]}",
            "order_ref_id": order_id,
            "gross_amount": amount,
            "fee_amount": fee,
            "net_settled": net,
            "settlement_date": (created_at + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "SETTLED"
        })
    elif rand_val > 0.03:
        # Amount mismatch anomaly (e.g. partial refund, bad fee calc)
        fee = round(amount * 0.029 + 0.30, 2)
        gateway_txns.append({
            "gateway_txn_id": f"txn_{uuid.uuid4().hex[:12]}",
            "order_ref_id": order_id,
            "gross_amount": round(amount - 5.00, 2), # Missing $5
            "fee_amount": fee,
            "net_settled": round(amount - 5.00 - fee, 2),
            "settlement_date": (created_at + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "SETTLED"
        })
    elif rand_val > 0.01:
        # Missing order ID in gateway (orphan row from gateway side)
        fee = round(amount * 0.029 + 0.30, 2)
        gateway_txns.append({
            "gateway_txn_id": f"txn_{uuid.uuid4().hex[:12]}",
            "order_ref_id": "", # Missing ID
            "gross_amount": amount,
            "fee_amount": fee,
            "net_settled": round(amount - fee, 2),
            "settlement_date": (created_at + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "SETTLED"
        })
    else:
        # Missing entirely from gateway (didn't settle)
        pass

# Add an orphan row in gateway that doesn't exist in internal DB
gateway_txns.append({
    "gateway_txn_id": f"txn_{uuid.uuid4().hex[:12]}",
    "order_ref_id": "ORD-UNKNOWN",
    "gross_amount": 99.99,
    "fee_amount": 3.20,
    "net_settled": 96.79,
    "settlement_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "status": "SETTLED"
})

# Save to CSVs
os.makedirs("data", exist_ok=True)

df_orders = pd.DataFrame(orders)
df_orders.to_csv("data/internal_orders.csv", index=False)

df_gateway = pd.DataFrame(gateway_txns)
df_gateway.to_csv("data/razorpay_settlement_report.csv", index=False)

print(f"✅ Generated {len(orders)} internal orders")
print(f"✅ Generated {len(gateway_txns)} gateway transactions")
print(f"✅ Intentionally created {(len(orders) - len(gateway_txns)) + 2} anomalies for testing.")
print("📁 Saved to: backend/data/internal_orders.csv and razorpay_settlement_report.csv")
