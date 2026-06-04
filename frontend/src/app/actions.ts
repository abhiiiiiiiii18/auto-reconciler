"use server";

import { exec } from 'child_process';
import util from 'util';
import path from 'path';

const execPromise = util.promisify(exec);

export async function runReconciliationAction(gateway: string) {
    try {
        const backendDir = path.join(process.cwd(), '../backend');
        
        console.log(`Running reconciliation for ${gateway}...`);
        await execPromise(`cd ${backendDir} && ./venv/bin/python3 reconcile.py ${gateway}`);
        
        console.log(`Running AI Anomaly Explanation...`);
        await execPromise(`cd ${backendDir} && ./venv/bin/python3 ai_agent.py`);
        
        return { success: true };
    } catch (e: any) {
        console.error("Error running python scripts:", e);
        return { success: false, error: e.message };
    }
}

export async function resolveDiscrepancyAction(orderId: string) {
    try {
        const backendDir = path.join(process.cwd(), '../backend');
        
        console.log(`Resolving discrepancy for ${orderId} via Accounting Sync...`);
        // Call the mock accounting sync script
        await execPromise(`cd ${backendDir} && ./venv/bin/python3 accounting_sync.py ${orderId}`);
        
        return { success: true };
    } catch (e: any) {
        console.error("Error running accounting sync:", e);
        return { success: false, error: e.message };
    }
}
