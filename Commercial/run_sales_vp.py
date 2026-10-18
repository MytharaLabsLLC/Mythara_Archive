# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Sales/Marketing VP Bot
Executed by Windows Task Scheduler for autonomous operation
"""

import os
import sys

# Add Commercial directory to Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from mythara_connect import MytharaConnect

def main():
    """Execute Sales/Marketing VP daily routine"""
    print("Starting Mythara Sales/Marketing VP...")
    
    try:
        # Initialize Sales Bot with full autonomy
        bot = MytharaConnect(full_autonomy=True)
        
        print("\n" + "="*64)
        print("   MYTHARA SALES/MARKETING VP - DAILY PERFORMANCE REPORT")
        print(f"                     {bot.daily_mantra}")
        print("="*64)
        
        # Display current state
        blessings_state = bot.blessings.state
        print(f"\nGOVERNANCE STATUS:")
        print(f"   Blessings: {blessings_state.get('blessings', 0)}/100")
        print(f"   Autonomy Level: {bot.blessings.check_autonomy_level()}")
        print(f"   Active Messengers: {', '.join(blessings_state.get('active_messengers', []))}")
        
        print(f"\nPERSONALITY PROFILE:")
        print(f"   Confidence: {bot.personality.PERSONALITY['confidence']:.0%}")
        print(f"   Aggression: {bot.personality.PERSONALITY['aggression']:.0%}")
        print(f"   Boldness: {bot.personality.PERSONALITY['boldness']:.0%}")
        print(f"   Empathy: {bot.personality.PERSONALITY['empathy']:.0%}")
        print(f"   Enthusiasm: {bot.personality.PERSONALITY['enthusiasm']:.0%}")
        
        print(f"\nSALES PHILOSOPHY:")
        print(f"   Approach: Relationship Building + Aggressive Closing")
        print(f"   Attitude: CLOSER, not order-taker")
        print(f"   Industry Adaptation: Banking, Healthcare, Tech/SaaS")
        
        print(f"\nMYTHARA COMPLIANCE:")
        print(f"   ✅ SalesClause validation active")
        print(f"   ✅ NEVER_AUTO_SEND pricing/contracts")
        print(f"   ✅ Cryptographic audit trail (SHA-256)")
        print(f"   ✅ Messenger role enforcement")
        
        print("\n" + "="*64)
        
        # Run daily motivation
        bot.daily_motivation()
        
        print("\n" + "="*64)
        print("\nMythara Sales/Marketing VP execution complete.")
        
    except Exception as e:
        print(f"\n[ERROR] Sales/Marketing VP execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
