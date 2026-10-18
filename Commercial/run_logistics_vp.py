# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Logistics VP Bot
Processes pending orders and monitors fulfillment
"""

from mythara_logistics_vp import MytharaLogisticsVP
from datetime import datetime

if __name__ == "__main__":
    print("="*60)
    print("MYTHARA LOGISTICS VP - ORDER PROCESSING")
    print(f"Run Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("="*60)
    
    # Initialize Logistics VP
    logistics = MytharaLogisticsVP()
    
    # Check for pending orders in database
    print("\n[CHECK] Scanning for pending orders...")
    
    import sqlite3
    conn = sqlite3.connect(logistics.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT order_id FROM orders WHERE status = "pending"')
    pending = cursor.fetchall()
    conn.close()
    
    if pending:
        print(f"[FOUND] {len(pending)} pending orders")
        for (order_id,) in pending:
            print(f"\n[PROCESS] Order: {order_id}")
            logistics.fulfill_order(order_id)
    else:
        print("[OK] No pending orders")
    
    # Generate and print report
    print("\n" + "="*60)
    report = logistics.generate_logistics_report()
    print(report)
    
    print("="*60)
    print("[OK] Logistics VP check complete")
    print(f"Next run: Schedule hourly via Windows Task Scheduler")
