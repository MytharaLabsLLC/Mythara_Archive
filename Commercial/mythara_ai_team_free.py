# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
🤖 MYTHARA AI TEAM - FREE VERSION (No AI API Needed)
====================================================

UPDATED: Uses rule-based logic instead of AI APIs
- Marketing Bot: Scores leads using simple rules
- Sales Trainer Bot: Analyzes conversations using pattern matching
- Cost: $0/month (no API calls)

For advanced AI features, upgrade to Google Gemini (free tier) or OpenAI (paid).
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# ============================================================================
# HELPER: Simple Pattern Matching (Replaces AI)
# ============================================================================

def analyze_text_patterns(text: str, patterns: Dict[str, List[str]]) -> List[str]:
    """
    Simple pattern matching - replaces AI analysis.
    
    Args:
        text: Text to analyze
        patterns: Dict of pattern_name -> list of keywords
    
    Returns:
        List of detected patterns
    """
    text_lower = text.lower()
    detected = []
    
    for pattern_name, keywords in patterns.items():
        if any(keyword.lower() in text_lower for keyword in keywords):
            detected.append(pattern_name)
    
    return detected


# ============================================================================
# BOT 1: MARKETING BOT (Rule-Based Lead Scoring)
# ============================================================================

class MarketingBot:
    """Marketing Bot - Uses rule-based logic instead of AI."""
    
    def __init__(self):
        self.lead_scoring_rules = {
            "industry_points": {
                "Banking": 40,
                "Healthcare": 40,
                "Insurance": 35,
                "Tech": 25,
                "SaaS": 25,
                "Finance": 30,
                "Fintech": 35
            },
            "company_size_points": {
                ">$100M": 30,
                "$50M-$100M": 20,
                "$10M-$50M": 10,
                "<$10M": 5
            },
            "engagement_points": {
                "email_open": 5,
                "link_click": 10,
                "reply": 15,
                "demo_request": 25,
                "pricing_page": 20
            }
        }
        
        self.best_subject_lines = [
            "Your model validation is non-compliant (here's why)",
            "[EXAMPLE] How a bank could cut validation from 6 weeks to 8 days",
            "[EXAMPLE] Why banks are investing in AI audit trails"
        ]
        
        self.optimal_send_times = {
            "Banking": "Tuesday 9am MT",
            "Healthcare": "Wednesday 10am MT",
            "Tech": "Thursday 2pm MT"
        }
    
    def score_lead(self, lead: Dict[str, Any]) -> int:
        """
        Score lead using simple rules (no AI).
        
        Returns: 0-100 score
        """
        score = 0
        
        # Industry fit (0-40 points)
        industry = lead.get('industry', '')
        for industry_name, points in self.lead_scoring_rules['industry_points'].items():
            if industry_name.lower() in industry.lower():
                score += points
                break
        else:
            score += 10  # Default for unlisted industries
        
        # Company size (0-30 points)
        revenue = lead.get('revenue', '<$10M')
        score += self.lead_scoring_rules['company_size_points'].get(revenue, 5)
        
        # Engagement (0-30 points)
        if lead.get('email_opens', 0) > 0:
            score += self.lead_scoring_rules['engagement_points']['email_open']
        if lead.get('clicked_link', False):
            score += self.lead_scoring_rules['engagement_points']['link_click']
        if lead.get('replied', False):
            score += self.lead_scoring_rules['engagement_points']['reply']
        if lead.get('requested_demo', False):
            score += self.lead_scoring_rules['engagement_points']['demo_request']
        if lead.get('visited_pricing', False):
            score += self.lead_scoring_rules['engagement_points']['pricing_page']
        
        return min(score, 100)  # Cap at 100
    
    def train_sales_bot(self) -> Dict[str, Any]:
        """Return training data for Sales Bot."""
        return {
            "best_performing_subject_lines": self.best_subject_lines,
            "optimal_send_times": self.optimal_send_times,
            "hot_leads_threshold": 70
        }


# ============================================================================
# BOT 2: SALES TRAINER BOT (Rule-Based Conversation Analysis)
# ============================================================================

class SalesTrainerBot:
    """Sales Trainer Bot - Analyzes conversations using pattern matching."""
    
    def __init__(self):
        self.winning_patterns = {
            "urgency_works": ["deadline", "expires", "limited time", "other banks", "competitors"],
            "compliance_language_works": ["audit", "compliance", "regulation", "OCC", "CFPB", "FDA"],
            "social_proof_works": ["illustrative example", "peer companies", "case study", "reference"],
            "competitive_pressure_works": ["we're talking to", "other vendors", "3 other", "evaluating"],
            "fast_response_wins": []  # Detected by response time, not text
        }
        
        self.losing_patterns = {
            "pricing_too_early": ["only $", "just $", "cheap", "discount", "save money"],
            "technical_jargon_loses": ["API", "cryptographic", "SHA-256", "algorithm", "backend"],
            "overselling_loses": ["best in industry", "revolutionary", "game-changer", "amazing"]
        }
    
    def analyze_conversation(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze conversation using pattern matching (no AI).
        
        Args:
            conversation: Dict with 'messages', 'outcome', 'tactics_used'
        
        Returns:
            Analysis with detected patterns and lessons
        """
        all_text = " ".join(conversation.get('messages', []))
        outcome = conversation.get('outcome', 'unknown')
        
        # Detect patterns
        winning_detected = analyze_text_patterns(all_text, self.winning_patterns)
        losing_detected = analyze_text_patterns(all_text, self.losing_patterns)
        
        lessons = []
        
        # If conversation succeeded, amplify winning patterns
        if outcome == 'closed':
            for pattern in winning_detected:
                lessons.append({
                    "pattern": pattern,
                    "recommendation": f"✅ AMPLIFY: {pattern.replace('_', ' ')} worked in this deal"
                })
        
        # If conversation failed, retire losing patterns
        if outcome == 'lost':
            for pattern in losing_detected:
                lessons.append({
                    "pattern": pattern,
                    "recommendation": f"❌ RETIRE: {pattern.replace('_', ' ')} contributed to loss"
                })
        
        return {
            "conversation_id": conversation.get('id', 'unknown'),
            "outcome": outcome,
            "winning_patterns": winning_detected,
            "losing_patterns": losing_detected,
            "lessons": lessons
        }
    
    def generate_training_update(self, conversations: List[Dict]) -> Dict[str, Any]:
        """
        Generate training update based on conversation analysis.
        
        Returns:
            Dict with tactics_to_amplify, tactics_to_retire, new_tactics_to_test
        """
        tactics_to_amplify = []
        tactics_to_retire = []
        new_tactics_to_test = []
        
        # Count pattern frequency in successful vs failed conversations
        pattern_stats = {}
        
        for conv in conversations:
            analysis = self.analyze_conversation(conv)
            outcome = conv.get('outcome')
            
            for pattern in analysis['winning_patterns']:
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {"success": 0, "failure": 0}
                if outcome == 'closed':
                    pattern_stats[pattern]['success'] += 1
                elif outcome == 'lost':
                    pattern_stats[pattern]['failure'] += 1
            
            for pattern in analysis['losing_patterns']:
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {"success": 0, "failure": 0}
                if outcome == 'closed':
                    pattern_stats[pattern]['success'] += 1
                elif outcome == 'lost':
                    pattern_stats[pattern]['failure'] += 1
        
        # Generate recommendations
        for pattern, stats in pattern_stats.items():
            total = stats['success'] + stats['failure']
            if total == 0:
                continue
            
            success_rate = stats['success'] / total
            
            # Amplify patterns with >60% success rate
            if success_rate > 0.6 and stats['success'] > 0:
                tactics_to_amplify.append({
                    "tactic": pattern,
                    "reason": f"{stats['success']}/{total} conversations succeeded using this",
                    "success_rate": f"{success_rate*100:.0f}%"
                })
            
            # Retire patterns with <40% success rate
            elif success_rate < 0.4 and stats['failure'] > 0:
                tactics_to_retire.append({
                    "tactic": pattern,
                    "reason": f"{stats['failure']}/{total} conversations failed using this",
                    "success_rate": f"{success_rate*100:.0f}%"
                })
        
        # Suggest new tactics to test (industry-specific)
        industries_in_conversations = set(conv.get('industry', 'Unknown') for conv in conversations)
        
        if 'Banking' in industries_in_conversations:
            new_tactics_to_test.append({
                "tactic": "regulatory_deadline",
                "hypothesis": "Banking prospects respond to regulatory deadlines (OCC, CFPB)",
                "test_approach": "A/B test emails mentioning compliance deadlines vs generic urgency"
            })
        
        if 'Healthcare' in industries_in_conversations:
            new_tactics_to_test.append({
                "tactic": "patient_safety_angle",
                "hypothesis": "Healthcare prospects care about patient safety more than ROI",
                "test_approach": "Lead with 'prevent medical errors' instead of 'save time'"
            })
        
        return {
            "tactics_to_amplify": tactics_to_amplify,
            "tactics_to_retire": tactics_to_retire,
            "new_tactics_to_test": new_tactics_to_test,
            "analyzed_conversations": len(conversations),
            "timestamp": datetime.now().isoformat()
        }
    
    def update_sales_bot_tactics(self, training_update: Dict[str, Any]) -> bool:
        """
        Push training update to Sales Bot.
        In production, this would update a tactics file or database.
        """
        print(f"\n📝 Training update generated:")
        print(f"   • {len(training_update['tactics_to_amplify'])} tactics to amplify")
        print(f"   • {len(training_update['tactics_to_retire'])} tactics to retire")
        print(f"   • {len(training_update['new_tactics_to_test'])} new A/B tests proposed")
        
        # In production, save to file or database
        # For now, just log
        return True


# ============================================================================
# BOT 3: PAYMENT MONITOR BOT (Loyverse Integration)
# ============================================================================

class PaymentMonitorBot:
    """
    Monitors Loyverse for payments and sends alerts.
    Uses rule-based logic to flag important transactions.
    """
    
    def __init__(self):
        self.access_token = os.getenv('LOYVERSE_ACCESS_TOKEN', '')  # set via environment; never hardcode
        self.api_base_url = "https://api.loyverse.com/v1.0"
        
    def get_recent_receipts(self, hours_back: int = 24) -> List[Dict]:
        """Fetch recent receipts from Loyverse."""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Get receipts from last N hours
        since = datetime.now() - timedelta(hours=hours_back)
        
        try:
            response = requests.get(
                f"{self.api_base_url}/receipts",
                headers=headers,
                params={
                    "created_at_min": since.isoformat(),
                    "limit": 100
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('receipts', [])
            else:
                print(f"⚠️ Loyverse API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️ Error fetching receipts: {e}")
            return []
    
    def analyze_payment(self, receipt: Dict) -> Dict[str, Any]:
        """
        Analyze a payment and flag important events.
        """
        total = receipt.get('total_money', 0)
        line_items = receipt.get('line_items', [])
        customer = receipt.get('customer_name', 'Unknown')
        
        flags = []
        priority = 'normal'
        
        # High-value transaction (>$10k)
        if total >= 10000:
            flags.append('high_value')
            priority = 'high'
        
        # Enterprise license purchase
        enterprise_skus = ['MYTH-ENT-YEAR', 'MYTH-VOIP-2026', 'MYTH-ADDON-ESCROW']
        for item in line_items:
            sku = item.get('sku', '')
            if sku in enterprise_skus:
                flags.append('enterprise_purchase')
                priority = 'critical'
        
        # Early adopter pricing used
        early_skus = ['MYTH-AUDIT-001', 'MYTH-SUB-MONTH']
        for item in line_items:
            sku = item.get('sku', '')
            if sku in early_skus and total < 1000:
                flags.append('early_adopter')
        
        # First-time customer
        if receipt.get('customer_id') and receipt.get('receipt_number', 1) == 1:
            flags.append('first_purchase')
        
        return {
            'receipt_id': receipt.get('receipt_number'),
            'customer': customer,
            'total': total,
            'items': [item.get('sku') for item in line_items],
            'flags': flags,
            'priority': priority,
            'timestamp': receipt.get('created_at')
        }
    
    def send_alert(self, analysis: Dict[str, Any]) -> bool:
        """
        Send alert for important payments.
        In production, this would email/SMS you.
        """
        if analysis['priority'] in ['high', 'critical']:
            print(f"\n🚨 PAYMENT ALERT - {analysis['priority'].upper()}")
            print(f"   Customer: {analysis['customer']}")
            print(f"   Total: ${analysis['total']:,.2f}")
            print(f"   Items: {', '.join(analysis['items'])}")
            print(f"   Flags: {', '.join(analysis['flags'])}")
            print(f"   Time: {analysis['timestamp']}")
            return True
        return False
    
    def monitor_payments(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Main monitoring function - checks for new payments.
        """
        receipts = self.get_recent_receipts(hours_back)
        
        total_revenue = 0
        high_priority_count = 0
        all_analyses = []
        
        for receipt in receipts:
            analysis = self.analyze_payment(receipt)
            all_analyses.append(analysis)
            
            total_revenue += analysis['total']
            
            if self.send_alert(analysis):
                high_priority_count += 1
        
        return {
            'period_hours': hours_back,
            'total_transactions': len(receipts),
            'total_revenue': total_revenue,
            'high_priority_alerts': high_priority_count,
            'analyses': all_analyses,
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# ORCHESTRATOR: Coordinates all bots
# ============================================================================

class MytharaAITeam:
    """Orchestrates all bots (Marketing, Sales Trainer, Payment Monitor, Autonomous Sales)."""
    
    def __init__(self):
        self.marketing_bot = MarketingBot()
        self.sales_trainer_bot = SalesTrainerBot()
        self.payment_monitor_bot = PaymentMonitorBot()
        
        # Import autonomous sales bot
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from mythara_autonomous_sales import AutonomousSalesBot
            self.autonomous_sales_bot = AutonomousSalesBot()
        except:
            self.autonomous_sales_bot = None
    
    def run_payment_monitor(self, hours_back: int = 24) -> str:
        """Run payment monitoring and return formatted report."""
        result = self.payment_monitor_bot.monitor_payments(hours_back)
        
        report = f"""
💰 PAYMENT MONITOR REPORT
Period: Last {result['period_hours']} hours
Generated: {result['timestamp']}

📊 SUMMARY:
   • Total Transactions: {result['total_transactions']}
   • Total Revenue: ${result['total_revenue']:,.2f}
   • High Priority Alerts: {result['high_priority_alerts']}

"""
        
        if result['analyses']:
            report += "📋 TRANSACTIONS:\n"
            for analysis in result['analyses']:
                report += f"\n   Receipt #{analysis['receipt_id']}"
                report += f"\n   Customer: {analysis['customer']}"
                report += f"\n   Total: ${analysis['total']:,.2f}"
                report += f"\n   Items: {', '.join(analysis['items'])}"
                if analysis['flags']:
                    report += f"\n   🏷️ Flags: {', '.join(analysis['flags'])}"
                report += f"\n   Priority: {analysis['priority']}"
                report += "\n"
        else:
            report += "✅ No transactions in this period\n"
        
        return report
    
    def run_autonomous_sales(self, prospect_list: List[Dict] = None) -> str:
        """Run autonomous sales bot - zero human contact."""
        
        if not self.autonomous_sales_bot:
            return "❌ Autonomous Sales Bot not loaded"
        
        if not prospect_list:
            # Use default test prospect
            prospect_list = [{
                'email': 'prospect@company.com',
                'name': 'Prospect',
                'company': 'Company',
                'industry': 'Technology'
            }]
        
        report = f"""
🤖 AUTONOMOUS SALES BOT REPORT
Generated: {datetime.now().isoformat()}

📧 PROCESSING {len(prospect_list)} PROSPECTS:

"""
        
        for prospect in prospect_list:
            result = self.autonomous_sales_bot.process_prospect(prospect)
            report += f"\n   • {prospect['email']}"
            report += f"\n     Stage: {result['current_stage']}"
            report += f"\n     Score: {result['current_score']}"
            report += f"\n     Actions: {len(result['actions_taken'])}"
            report += "\n"
        
        # Get pipeline report
        pipeline = self.autonomous_sales_bot.get_pipeline_report()
        
        report += f"""
📊 PIPELINE STATUS:
   • Total Prospects: {pipeline['total_prospects']}
   • Cold: {pipeline['pipeline_stages'].get('cold', 0)}
   • Engaged: {pipeline['pipeline_stages'].get('engaged', 0)}
   • Invoiced: {pipeline['pipeline_stages'].get('invoiced', 0)}
   • Customers: {pipeline['pipeline_stages'].get('customer', 0)}

💰 REVENUE:
   • Closed Deals: {pipeline['closed_deals']}
   • Total Revenue: ${pipeline['total_revenue']:,.2f}
   • Avg Deal Size: ${pipeline['avg_deal_size']:,.2f}

🔐 SSIP CLAUSE PERFORMANCE:
"""
        
        for clause_id, perf in pipeline['clause_performance'].items():
            report += f"\n   {clause_id}: {perf['invocations']} invocations, {perf['success_rate']:.1f}% success"
        
        report += "\n\n✅ Zero human contact - fully autonomous"
        
        return report
    
    def daily_standup(self) -> Dict[str, Any]:
        """Generate daily performance summary."""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "marketing_bot": {
                "leads_generated": "Check logs",
                "hot_leads": "Check logs"
            },
            "sales_trainer_bot": {
                "conversations_analyzed": "Check logs",
                "tactics_updated": "Check logs"
            }
        }
    
    def weekly_performance_report(self) -> str:
        """Generate weekly email report."""
        report = f"""
📊 MYTHARA AI TEAM - WEEKLY REPORT
Week of {datetime.now().strftime('%B %d, %Y')}

🤖 BOTS ACTIVE: 2/6
   ✅ Marketing Bot (running hourly)
   ✅ Sales Trainer Bot (running every 6 hours)
   ⏳ Growth Strategy Bot (not deployed)
   ⏳ Backlog Bot (not deployed)
   ⏳ Brand Awareness Bot (not deployed)
   ⏳ HR Bot (not deployed)

📊 MARKETING BOT:
   • Leads generated: Check logs
   • Hot leads (>70 score): Check logs
   • Cost: $0 (rule-based, no API)

🎓 SALES TRAINER BOT:
   • Conversations analyzed: Check logs
   • Tactics updated: Check logs
   • Cost: $0 (rule-based, no API)

💰 COST THIS WEEK: $0
   (Upgrade to Google Gemini for AI-powered analysis)

🎯 NEXT STEPS:
   1. Get free Google Gemini API key: https://ai.google.dev/
   2. Deploy remaining 4 bots
   3. Set up PostgreSQL database
   4. Configure Google Ads for real lead generation

---
Mythara Engine - Autonomous AI Team
"""
        return report


if __name__ == "__main__":
    print("🤖 Mythara AI Team - Free Version")
    print("Uses rule-based logic (no AI API needed)")
    print("")
    
    team = MytharaAITeam()
    
    # Test Marketing Bot
    print("Testing Marketing Bot...")
    test_lead = {
        "email": "test@bank.com",
        "company": "Test Bank",
        "industry": "Banking",
        "revenue": ">$100M",
        "email_opens": 3,
        "clicked_link": True
    }
    score = team.marketing_bot.score_lead(test_lead)
    print(f"✅ Lead scored: {score}/100")
    
    # Test Sales Trainer Bot
    print("\nTesting Sales Trainer Bot...")
    test_conv = {
        "id": "test_001",
        "outcome": "closed",
        "messages": ["We can help you meet the OCC deadline", "That's important", "Let's do it"]
    }
    analysis = team.sales_trainer_bot.analyze_conversation(test_conv)
    print(f"✅ Conversation analyzed: {len(analysis['lessons'])} lessons learned")
    
    print("\n✅ All bots working (rule-based mode)")
    print("💡 Upgrade to Google Gemini for AI-powered features (free tier available)")
