# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Runner script for Mythara Public Affairs VP Bot
Manages brand sentiment, campaigns, crisis response, media relations
"""

from mythara_public_affairs_vp import MytharaPublicAffairsVP
from datetime import datetime

if __name__ == "__main__":
    print("="*60)
    print("MYTHARA PUBLIC AFFAIRS VP - BRAND MONITOR")
    print(f"Run Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("="*60)
    
    # Initialize Public Affairs VP
    vp = MytharaPublicAffairsVP()
    
    # Monitor brand mentions across platforms
    print("\n[CHECK] Monitoring brand mentions...")
    mentions = vp.monitor_brand_mentions(platform='all')
    print(f"   New mentions: {mentions['new_mentions']}")
    print(f"   Overall sentiment: {mentions['overall_sentiment']:.1f}/100")
    
    # Check for negative mentions requiring response
    negative_count = sum(1 for m in mentions['mentions'] if m['sentiment'] == 'negative')
    if negative_count > 0:
        print(f"\n[ALERT] {negative_count} negative mentions detected - response required within 4 hours")
    
    # Analyze public perception
    print("\n[ANALYZE] Public perception analysis...")
    analysis = vp.analyze_public_perception()
    print(f"   Sentiment: {analysis['sentiment_category'].upper()}")
    print(f"   24h Reach: {analysis['metrics']['total_reach_24h']:,}")
    
    # Check sentiment threshold
    if analysis['overall_sentiment'] < 60:
        print("\n[WARN] Brand sentiment below target - launching engagement campaign...")
        campaign = vp.create_campaign(
            campaign_type='thought_leadership',
            target_audience='developers',
            objectives=['Improve brand perception', 'Increase positive mentions']
        )
        print(f"   Campaign ID: {campaign['campaign_id']}")
    
    # Generate and print full report
    print("\n" + "="*60)
    report = vp.generate_public_affairs_report()
    print(report)
    
    print("="*60)
    print("[OK] Public Affairs VP check complete")
    print(f"Next run: Schedule every 4 hours via Windows Task Scheduler")
