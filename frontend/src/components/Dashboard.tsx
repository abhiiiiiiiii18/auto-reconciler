"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle2, DollarSign, Activity, FileSearch, ArrowRightLeft } from 'lucide-react';

type Discrepancy = {
    order_id: string;
    gateway_txn_id: string;
    amount: string;
    gross_amount: string;
    fee_amount: string;
    net_settled: string;
    match_status: string;
    ai_explanation: string;
};

export default function Dashboard({ data }: { data: Discrepancy[] }) {
    const [selectedRow, setSelectedRow] = useState<string | null>(null);

    const getStatusColor = (status: string) => {
        switch(status) {
            case 'MISSING_IN_GATEWAY': return 'bg-red-500/20 text-red-400 border-red-500/30';
            case 'ORPHAN_GATEWAY_TXN': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
            case 'AMOUNT_MISMATCH': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            case 'FUZZY_MATCH_FEE_ERROR': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
            default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
        }
    };

    const getStatusIcon = (status: string) => {
        switch(status) {
            case 'MISSING_IN_GATEWAY': return <AlertCircle className="w-4 h-4 mr-2" />;
            case 'ORPHAN_GATEWAY_TXN': return <FileSearch className="w-4 h-4 mr-2" />;
            case 'AMOUNT_MISMATCH': return <ArrowRightLeft className="w-4 h-4 mr-2" />;
            case 'FUZZY_MATCH_FEE_ERROR': return <DollarSign className="w-4 h-4 mr-2" />;
            default: return <Activity className="w-4 h-4 mr-2" />;
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans selection:bg-indigo-500/30">
            {/* Header */}
            <header className="mb-12 flex justify-between items-end border-b border-white/10 pb-6">
                <div>
                    <h1 className="text-4xl font-semibold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white to-white/60 mb-2">
                        Reconciliation Engine
                    </h1>
                    <p className="text-white/40">AI-Powered Payment Discrepancy Analysis</p>
                </div>
                <div className="flex gap-4">
                    <div className="px-4 py-2 rounded-full bg-white/5 border border-white/10 flex items-center shadow-lg backdrop-blur-md">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 mr-3 animate-pulse"></div>
                        <span className="text-sm text-white/70">Engine Active</span>
                    </div>
                </div>
            </header>

            {/* Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <motion.div 
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                    className="p-6 rounded-2xl bg-gradient-to-b from-white/[0.08] to-transparent border border-white/[0.05] relative overflow-hidden group"
                >
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><Activity size={64}/></div>
                    <p className="text-sm text-white/50 mb-1">Total Processed</p>
                    <p className="text-3xl font-light">1,000<span className="text-lg text-white/30 ml-2">orders</span></p>
                </motion.div>
                
                <motion.div 
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                    className="p-6 rounded-2xl bg-gradient-to-b from-emerald-500/[0.08] to-transparent border border-emerald-500/[0.1] relative overflow-hidden group"
                >
                    <div className="absolute top-0 right-0 p-4 text-emerald-500 opacity-10 group-hover:opacity-20 transition-opacity"><CheckCircle2 size={64}/></div>
                    <p className="text-sm text-emerald-500/70 mb-1">Perfect Matches</p>
                    <p className="text-3xl font-light text-emerald-400">943<span className="text-lg text-emerald-400/50 ml-2">94.3%</span></p>
                </motion.div>

                <motion.div 
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                    className="p-6 rounded-2xl bg-gradient-to-b from-rose-500/[0.08] to-transparent border border-rose-500/[0.1] relative overflow-hidden group"
                >
                    <div className="absolute top-0 right-0 p-4 text-rose-500 opacity-10 group-hover:opacity-20 transition-opacity"><AlertCircle size={64}/></div>
                    <p className="text-sm text-rose-500/70 mb-1">Discrepancies Detected</p>
                    <p className="text-3xl font-light text-rose-400">82<span className="text-lg text-rose-400/50 ml-2">Requires Review</span></p>
                </motion.div>
            </div>

            {/* Data Table */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden backdrop-blur-xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-white/10 bg-white/[0.03]">
                                <th className="p-4 text-sm font-medium text-white/50">Order ID</th>
                                <th className="p-4 text-sm font-medium text-white/50">Anomaly Type</th>
                                <th className="p-4 text-sm font-medium text-white/50 text-right">Expected</th>
                                <th className="p-4 text-sm font-medium text-white/50 text-right">Settled</th>
                                <th className="p-4 text-sm font-medium text-white/50">AI Explanation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((row, i) => (
                                <React.Fragment key={i}>
                                    <motion.tr 
                                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 * (i % 10) }}
                                        onClick={() => setSelectedRow(selectedRow === row.order_id ? null : row.order_id)}
                                        className="border-b border-white/5 hover:bg-white/[0.04] cursor-pointer transition-colors group"
                                    >
                                        <td className="p-4 font-mono text-sm text-white/80">{row.order_id || 'UNKNOWN'}</td>
                                        <td className="p-4">
                                            <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(row.match_status)}`}>
                                                {getStatusIcon(row.match_status)}
                                                {row.match_status.replace(/_/g, ' ')}
                                            </div>
                                        </td>
                                        <td className="p-4 text-right font-mono text-white/70">${parseFloat(row.amount || '0').toFixed(2)}</td>
                                        <td className="p-4 text-right font-mono text-white/70">${parseFloat(row.gross_amount || '0').toFixed(2)}</td>
                                        <td className="p-4">
                                            <div className="max-w-md truncate text-white/60 text-sm">
                                                {row.ai_explanation}
                                            </div>
                                        </td>
                                    </motion.tr>
                                    
                                    {/* Expandable row for details */}
                                    <AnimatePresence>
                                        {selectedRow === row.order_id && (
                                            <motion.tr
                                                initial={{ height: 0, opacity: 0 }}
                                                animate={{ height: "auto", opacity: 1 }}
                                                exit={{ height: 0, opacity: 0 }}
                                                className="bg-indigo-500/[0.03]"
                                            >
                                                <td colSpan={5} className="p-6 border-b border-white/5">
                                                    <div className="flex gap-8">
                                                        <div className="flex-1">
                                                            <h4 className="text-xs uppercase tracking-wider text-indigo-400 mb-2 flex items-center"><Activity size={14} className="mr-2"/> AI Analysis</h4>
                                                            <p className="text-white/80 leading-relaxed bg-black/40 p-4 rounded-xl border border-indigo-500/20">{row.ai_explanation}</p>
                                                        </div>
                                                        <div className="w-64 space-y-4">
                                                            <div>
                                                                <h4 className="text-xs uppercase tracking-wider text-white/40 mb-1">Gateway Txn ID</h4>
                                                                <p className="font-mono text-sm text-white/70">{row.gateway_txn_id}</p>
                                                            </div>
                                                            <div className="flex justify-between border-t border-white/10 pt-2">
                                                                <span className="text-sm text-white/50">Fee Deducted</span>
                                                                <span className="font-mono text-rose-400">-${parseFloat(row.fee_amount || '0').toFixed(2)}</span>
                                                            </div>
                                                            <div className="flex justify-between">
                                                                <span className="text-sm text-white/50">Net Payout</span>
                                                                <span className="font-mono text-emerald-400">${parseFloat(row.net_settled || '0').toFixed(2)}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </td>
                                            </motion.tr>
                                        )}
                                    </AnimatePresence>
                                </React.Fragment>
                            ))}
                        </tbody>
                    </table>
                </div>
                {data.length === 0 && (
                    <div className="p-12 text-center text-white/40">
                        No discrepancies found or the CSV is missing. Run the Python generation scripts first!
                    </div>
                )}
            </div>
        </div>
    );
}
