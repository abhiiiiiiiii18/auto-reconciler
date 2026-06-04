import pandas as pd

class GatewayParser:
    def parse(self, filepath: str) -> pd.DataFrame:
        raise NotImplementedError("Subclasses must implement parse()")

class RazorpayParser(GatewayParser):
    def parse(self, filepath: str) -> pd.DataFrame:
        # Razorpay format: txn_id, order_id, amount, fee, tax, settled_amount, status
        df = pd.read_csv(filepath)
        df = df.rename(columns={
            "txn_id": "gateway_txn_id",
            "order_id": "internal_order_id",
            "amount": "gross_amount",
            "fee": "fee_amount",
            "settled_amount": "net_settled"
        })
        return df

class StripeParser(GatewayParser):
    def parse(self, filepath: str) -> pd.DataFrame:
        # Stripe format: id, description (holds order ID), Amount, Fee, Net, Status
        df = pd.read_csv(filepath)
        df = df.rename(columns={
            "id": "gateway_txn_id",
            "description": "internal_order_id",
            "Amount": "gross_amount",
            "Fee": "fee_amount",
            "Net": "net_settled"
        })
        return df

class PayPalParser(GatewayParser):
    def parse(self, filepath: str) -> pd.DataFrame:
        # PayPal format: Transaction ID, Invoice ID, Gross, Fee, Net, Type
        df = pd.read_csv(filepath)
        df = df.rename(columns={
            "Transaction ID": "gateway_txn_id",
            "Invoice ID": "internal_order_id",
            "Gross": "gross_amount",
            "Fee": "fee_amount",
            "Net": "net_settled"
        })
        return df

def get_parser(gateway_name: str) -> GatewayParser:
    gateway_name = gateway_name.lower()
    if gateway_name == "razorpay":
        return RazorpayParser()
    elif gateway_name == "stripe":
        return StripeParser()
    elif gateway_name == "paypal":
        return PayPalParser()
    else:
        raise ValueError(f"Unknown gateway: {gateway_name}")
