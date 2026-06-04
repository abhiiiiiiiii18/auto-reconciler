"use server";

import { exec } from 'child_process';
import util from 'util';
import path from 'path';

const execPromise = util.promisify(exec);

export async function runReconciliationAction(gateway: string) {
    try {
        const backendDir = path.join(process.cwd(), '../backend');
        
        // 1. Run the Pandas matching engine
        console.log(`Running reconciliation for ${gateway}...`);
        await execPromise(`cd ${backendDir} && ./venv/bin/python3 reconcile.py ${gateway}`);
        
        // 2. Run the Gemini AI (or mock fallback) for explanations
        console.log(`Running AI Anomaly Explanation...`);
        await execPromise(`cd ${backendDir} && ./venv/bin/python3 ai_agent.py`);
        
        return { success: true };
    } catch (e: any) {
        console.error("Error running python scripts:", e);
        return { success: false, error: e.message };
    }
}
