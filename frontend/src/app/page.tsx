import { PrismaClient } from '@prisma/client';
import Dashboard from '@/components/Dashboard';

export const dynamic = 'force-dynamic';
const prisma = new PrismaClient();

export default async function Home() {
  let records = [];

  try {
    const dbRecords = await prisma.reconciliationResult.findMany({
      orderBy: { createdAt: 'desc' }
    });
    
    records = dbRecords.map(r => ({
      order_id: r.orderId || 'UNKNOWN',
      gateway_txn_id: r.gatewayTxnId || 'UNKNOWN',
      amount: r.amount?.toString() || '0',
      gross_amount: r.grossAmount?.toString() || '0',
      fee_amount: r.feeAmount?.toString() || '0',
      net_settled: r.netSettled?.toString() || '0',
      match_status: r.matchStatus,
      ai_explanation: r.aiExplanation || ''
    }));
  } catch (err) {
    console.error("Could not load discrepancies from DB:", err);
  }

  return (
    <main className="min-h-screen bg-[#0a0a0a]">
      <Dashboard data={records} />
    </main>
  );
}
