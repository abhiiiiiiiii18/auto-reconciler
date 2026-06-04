import { NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function POST(request: Request, { params }: { params: { gateway: string } }) {
    try {
        const gateway = params.gateway.toLowerCase();
        const body = await request.json();
        
        console.log(`[WEBHOOK] Received ${gateway} event:`, body);

        // Normalize depending on the gateway
        let txnData = null;
        
        if (gateway === "razorpay") {
            txnData = {
                gatewayTxnId: body.txn_id,
                gateway: "razorpay",
                orderRefId: body.order_id,
                grossAmount: parseFloat(body.amount),
                feeAmount: parseFloat(body.fee),
                netSettled: parseFloat(body.settled_amount),
                settlementDate: new Date(),
                status: body.status || "SETTLED"
            };
        } else if (gateway === "stripe") {
            txnData = {
                gatewayTxnId: body.id,
                gateway: "stripe",
                orderRefId: body.description,
                grossAmount: parseFloat(body.Amount),
                feeAmount: parseFloat(body.Fee),
                netSettled: parseFloat(body.Net),
                settlementDate: new Date(),
                status: body.Status || "SETTLED"
            };
        } else if (gateway === "paypal") {
            txnData = {
                gatewayTxnId: body["Transaction ID"],
                gateway: "paypal",
                orderRefId: body["Invoice ID"],
                grossAmount: parseFloat(body.Gross),
                feeAmount: parseFloat(body.Fee),
                netSettled: parseFloat(body.Net),
                settlementDate: new Date(),
                status: body.Type || "SETTLED"
            };
        }

        if (!txnData || !txnData.gatewayTxnId) {
            return NextResponse.json({ error: "Unsupported gateway or missing Txn ID" }, { status: 400 });
        }

        // Upsert into Postgres via Prisma
        await prisma.gatewayTransaction.upsert({
            where: { gatewayTxnId: txnData.gatewayTxnId },
            update: txnData,
            create: txnData
        });
        
        return NextResponse.json({ success: true, message: "Transaction stored successfully" });
    } catch (e: any) {
        console.error("Webhook processing error:", e);
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
