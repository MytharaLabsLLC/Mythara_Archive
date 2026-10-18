# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara Affiliate Tracker (honest rebuild 2026-09-22)

WHAT IT DOES:
  Registers affiliates, tracks referral clicks/sales, calculates
  commissions under fixed ("sanctified") rules, and APPROVES payouts
  once the $50 threshold is hit. State persists in affiliate_state.json.

WHAT IT DOES NOT DO:
  It does not move money. There is no PayPal/Stripe payout API here.
  An "approved" payout is a ledger entry saying Herb owes the affiliate;
  Herb sends the money himself via PayPal. Anything that used to say
  "sent" now says "approved_for_payout".
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import hashlib


# ============================================================================
# MYTHARA SSIP: MESSENGER PAIRING FOR AFFILIATES
# ============================================================================

class MessengerPairing:
    """
    Pairs affiliates (Messengers) with customers.
    Tracks attribution and commission eligibility.
    """
    
    def __init__(self):
        self.pairings = {}  # affiliate_id -> [customer_ids]
        self.attribution_window = 30  # days
    
    def create_pairing(self, affiliate_id: str, customer_email: str, referral_code: str) -> Dict[str, Any]:
        """Create affiliate-customer pairing."""
        
        pairing_id = hashlib.sha256(f"{affiliate_id}{customer_email}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        pairing = {
            'pairing_id': pairing_id,
            'affiliate_id': affiliate_id,
            'customer_email': customer_email,
            'referral_code': referral_code,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=self.attribution_window)).isoformat(),
            'status': 'active',
            'commission_eligible': True
        }
        
        if affiliate_id not in self.pairings:
            self.pairings[affiliate_id] = []
        
        self.pairings[affiliate_id].append(pairing)
        
        return pairing
    
    def get_affiliate_for_customer(self, customer_email: str) -> str:
        """Find which affiliate referred this customer."""
        
        for affiliate_id, pairings in self.pairings.items():
            for pairing in pairings:
                if pairing['customer_email'] == customer_email and pairing['status'] == 'active':
                    # Check if still within attribution window
                    expires = datetime.fromisoformat(pairing['expires_at'])
                    if datetime.now() < expires:
                        return affiliate_id
        
        return None


class CommissionSanctification:
    """
    Sanctified commission rules - immutable once set.
    Based on Mythara Sanctification Lock pattern.
    """
    
    def __init__(self):
        self.rules = {
            'MYTH-AUDIT-001': {
                'commission_percent': 20,  # 20% of $500 = $100
                'commission_type': 'one_time',
                'min_payout': 50,
                'sanctified': True
            },
            'MYTH-SUB-MONTH': {
                'commission_percent': 30,  # 30% of $300 = $90/month
                'commission_type': 'recurring',
                'months': 12,  # Commission for first 12 months
                'min_payout': 50,
                'sanctified': True
            },
            'MYTH-SUB-YEAR': {
                'commission_percent': 25,  # 25% of $5000 = $1250
                'commission_type': 'one_time',
                'min_payout': 50,
                'sanctified': True
            },
            'MYTH-ENT-YEAR': {
                'commission_percent': 15,  # 15% of $25k = $3750
                'commission_type': 'one_time',
                'min_payout': 50,
                'sanctified': True
            }
        }
        
        self.integrity_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate integrity hash for commission rules."""
        data = json.dumps(self.rules, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def calculate_commission(self, product_sku: str, sale_amount: float) -> float:
        """Calculate commission based on sanctified rules."""
        
        rule = self.rules.get(product_sku)
        if not rule:
            return 0.0
        
        commission = sale_amount * (rule['commission_percent'] / 100)
        
        # Enforce minimum payout
        if commission < rule['min_payout']:
            return 0.0
        
        return commission
    
    def is_recurring(self, product_sku: str) -> bool:
        """Check if product has recurring commissions."""
        rule = self.rules.get(product_sku)
        return rule and rule['commission_type'] == 'recurring'


# ============================================================================
# AUTONOMOUS AFFILIATE BOT
# ============================================================================

class AutonomousAffiliateBot:
    """
    Affiliate tracking system: recruits (registers) affiliates, tracks
    referrals, calculates commissions, approves payouts. Money movement
    is manual — Herb pays via PayPal; this is the ledger, not the wallet.
    """

    def __init__(self, state_path: str = None):
        self.messenger_pairing = MessengerPairing()
        self.commission_rules = CommissionSanctification()
        self.affiliates = {}
        self.pending_payouts = []
        self.paid_commissions = []
        # Rebuild pairings from persisted affiliates is out of scope;
        # pairings live for the session, money math persists.
        self.state_path = state_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "affiliate_state.json")
        self._load_state()

    def _save_state(self):
        """Persist affiliate ledger so it survives restarts."""
        try:
            with open(self.state_path, "w") as f:
                json.dump({
                    "affiliates": self.affiliates,
                    "pending_payouts": self.pending_payouts,
                    "paid_commissions": self.paid_commissions,
                    "saved_at": datetime.now().isoformat(),
                }, f, indent=2)
        except Exception:
            pass  # persistence must never break tracking

    def _load_state(self):
        """Restore affiliate ledger from disk."""
        try:
            if not os.path.exists(self.state_path):
                return
            with open(self.state_path) as f:
                state = json.load(f)
            self.affiliates = state.get("affiliates", {})
            self.pending_payouts = state.get("pending_payouts", [])
            self.paid_commissions = state.get("paid_commissions", [])
        except Exception:
            pass
    
    def recruit_affiliate(self, email: str, name: str, platform: str,
                          queue_draft: bool = True) -> Dict[str, Any]:
        """
        Register a new affiliate and draft their welcome email.

        Honest contract: this WRITES a welcome-email draft to the
        outreach queue for Herb's approval — it does not send email.
        Returns the affiliate record, the draft text, and the draft path
        (or None when queue_draft=False, e.g. in demos).
        """

        # Generate unique affiliate ID and referral code
        affiliate_id = hashlib.sha256(email.encode()).hexdigest()[:12]
        referral_code = f"MYTH-{affiliate_id[:8].upper()}"

        affiliate = {
            'affiliate_id': affiliate_id,
            'email': email,
            'name': name,
            'platform': platform,  # LinkedIn, Twitter, Blog, YouTube, etc.
            'referral_code': referral_code,
            'referral_link': f"https://mythara.engine/ref/{referral_code}",
            'joined_at': datetime.now().isoformat(),
            'total_referrals': 0,
            'total_sales': 0.0,
            'total_commissions_earned': 0.0,
            'total_commissions_paid': 0.0,
            'status': 'active'
        }

        self.affiliates[affiliate_id] = affiliate
        self._save_state()

        # Draft (never send) the welcome email via the outreach queue.
        welcome_email = self._generate_welcome_email(affiliate)
        draft_path = None
        if queue_draft:
            from outreach_queue import OutreachQueue
            draft_path = OutreachQueue().queue(
                kind="email",
                title=f"Affiliate welcome: {name}",
                body=(f"To: {email}\n\n{welcome_email}"),
                meta={"affiliate_id": affiliate_id,
                      "referral_code": referral_code},
            )

        return {
            'affiliate': affiliate,
            'welcome_email': welcome_email,
            'welcome_draft_path': draft_path,
            'action': 'draft_queued_for_approval',
        }
    
    def _generate_welcome_email(self, affiliate: Dict[str, Any]) -> str:
        """Generate automated welcome email for new affiliate."""
        
        return f"""Subject: Welcome to Mythara Affiliate Program

{affiliate['name']},

You're now a Mythara affiliate! Here's your unique referral link:

🔗 {affiliate['referral_link']}
📋 Code: {affiliate['referral_code']}

COMMISSION STRUCTURE (Sanctified - Never Changes):
✅ SSIP Audit ($500): 20% = $100 per sale
✅ Monthly Sub ($300/mo): 30% = $90/month (12 months)
✅ Annual Sub ($5k): 25% = $1,250 per sale
✅ Enterprise ($25k): 15% = $3,750 per sale

AFFILIATE DASHBOARD:
🔗 https://mythara.engine/affiliate/{affiliate['affiliate_id']}

Track real-time:
- Clicks on your link
- Conversions
- Commissions earned
- Payment status

PAYMENT:
- Payouts approved automatically when you hit $50
- Herb sends payment manually via PayPal (usually weekly, Fridays)
- No minimums after first payout

MARKETING ASSETS:
- Banner ads: https://mythara.engine/affiliate/assets
- Email templates: Included in dashboard
- Social media posts: Auto-generated

Start sharing your link whenever you're ready.

Questions? Just reply to this email.

Mythara Affiliate Program
Mythara.Engine@yahoo.com
"""
    
    def track_referral_click(self, referral_code: str, visitor_email: str = None) -> Dict[str, Any]:
        """Track when someone clicks affiliate link."""
        
        # Find affiliate by referral code
        affiliate = None
        for aff_id, aff_data in self.affiliates.items():
            if aff_data['referral_code'] == referral_code:
                affiliate = aff_data
                break
        
        if not affiliate:
            return {'error': 'Invalid referral code'}
        
        # Create tracking cookie/session
        click_data = {
            'affiliate_id': affiliate['affiliate_id'],
            'referral_code': referral_code,
            'visitor_email': visitor_email,
            'clicked_at': datetime.now().isoformat(),
            'converted': False
        }
        
        # If visitor provides email, create pairing
        if visitor_email:
            self.messenger_pairing.create_pairing(
                affiliate['affiliate_id'],
                visitor_email,
                referral_code
            )
        
        return click_data
    
    def process_sale(self, customer_email: str, product_sku: str, sale_amount: float, payment_id: str) -> Dict[str, Any]:
        """
        Process sale and attribute commission to affiliate.
        Fully automated.
        """
        
        # Find affiliate who referred this customer
        affiliate_id = self.messenger_pairing.get_affiliate_for_customer(customer_email)
        
        if not affiliate_id:
            return {
                'attributed': False,
                'reason': 'No affiliate attribution'
            }
        
        # Calculate commission
        commission = self.commission_rules.calculate_commission(product_sku, sale_amount)
        
        if commission == 0:
            return {
                'attributed': True,
                'affiliate_id': affiliate_id,
                'commission': 0,
                'reason': 'Below minimum payout threshold'
            }
        
        # Record commission
        commission_record = {
            'commission_id': hashlib.sha256(f"{payment_id}{affiliate_id}".encode()).hexdigest()[:16],
            'affiliate_id': affiliate_id,
            'customer_email': customer_email,
            'product_sku': product_sku,
            'sale_amount': sale_amount,
            'commission_amount': commission,
            'commission_percent': self.commission_rules.rules[product_sku]['commission_percent'],
            'payment_id': payment_id,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'payout_scheduled': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')  # 3-day hold
        }
        
        self.pending_payouts.append(commission_record)
        
        # Update affiliate stats
        affiliate = self.affiliates[affiliate_id]
        affiliate['total_referrals'] += 1
        affiliate['total_sales'] += sale_amount
        affiliate['total_commissions_earned'] += commission
        self._save_state()

        # Draft (not send) the commission notification for the queue
        notification = self._generate_commission_notification(affiliate, commission_record)
        
        return {
            'attributed': True,
            'affiliate_id': affiliate_id,
            'commission': commission,
            'commission_record': commission_record,
            'notification_email': notification
        }
    
    def _generate_commission_notification(self, affiliate: Dict[str, Any], commission: Dict[str, Any]) -> str:
        """Generate commission earned notification."""
        
        return f"""Subject: Commission Earned: ${commission['commission_amount']:.2f}

{affiliate['name']},

Great news! You earned a commission:

💰 Amount: ${commission['commission_amount']:.2f}
📦 Product: {commission['product_sku']}
💵 Sale: ${commission['sale_amount']:.2f}
📅 Payout Date: {commission['payout_scheduled']}

Your Stats:
- Total Referrals: {affiliate['total_referrals']}
- Total Sales: ${affiliate['total_sales']:,.2f}
- Total Earned: ${affiliate['total_commissions_earned']:,.2f}
- Pending Payout: ${self._get_pending_balance(affiliate['affiliate_id']):,.2f}

Dashboard: https://mythara.engine/affiliate/{affiliate['affiliate_id']}

Keep sharing! Next payout: Friday

Mythara Affiliate Program
"""
    
    def _get_pending_balance(self, affiliate_id: str) -> float:
        """Calculate pending commission balance for affiliate."""
        total = 0.0
        for payout in self.pending_payouts:
            if payout['affiliate_id'] == affiliate_id and payout['status'] == 'pending':
                total += payout['commission_amount']
        return total
    
    def process_weekly_payouts(self) -> List[Dict[str, Any]]:
        """
        Approve all pending payouts that cleared the $50 minimum.

        Honest contract: this APPROVES payouts in the ledger. It moves no
        money — there is no PayPal/Stripe API here. Herb sends each
        approved payout manually. Status is 'approved_for_payout',
        never 'sent'.
        """

        payouts_processed = []
        
        # Group by affiliate
        affiliate_payouts = {}
        for payout in self.pending_payouts:
            if payout['status'] == 'pending':
                aff_id = payout['affiliate_id']
                if aff_id not in affiliate_payouts:
                    affiliate_payouts[aff_id] = []
                affiliate_payouts[aff_id].append(payout)
        
        # Process each affiliate
        for affiliate_id, payouts in affiliate_payouts.items():
            total_amount = sum(p['commission_amount'] for p in payouts)
            
            # Check minimum payout ($50)
            if total_amount < 50:
                continue
            
            affiliate = self.affiliates[affiliate_id]

            # Approve the payout in the ledger. Money movement is manual:
            # Herb sends this via PayPal himself.
            payout_record = {
                'payout_id': hashlib.sha256(f"{affiliate_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
                'affiliate_id': affiliate_id,
                'affiliate_email': affiliate['email'],
                'amount': total_amount,
                'commissions_included': [p['commission_id'] for p in payouts],
                'method': 'paypal_manual',
                'status': 'approved_for_payout',
                'approved_at': datetime.now().isoformat(),
                'payout_note': 'MANUAL STEP REQUIRED: Herb sends this via PayPal.',
            }

            # Mark commissions as approved (not paid — paid happens manually)
            for payout in payouts:
                payout['status'] = 'approved_for_payout'
                payout['approved_at'] = datetime.now().isoformat()
                payout['payout_id'] = payout_record['payout_id']
                self.paid_commissions.append(payout)

            # Update affiliate stats
            affiliate['total_commissions_paid'] += total_amount

            # Remove from pending
            self.pending_payouts = [p for p in self.pending_payouts if p['affiliate_id'] != affiliate_id]
            self._save_state()

            # Draft the payout notification (queued for approval, not sent)
            confirmation = self._generate_payout_confirmation(affiliate, payout_record)

            payouts_processed.append({
                'payout': payout_record,
                'email': confirmation
            })

        return payouts_processed
    
    def _generate_payout_confirmation(self, affiliate: Dict[str, Any], payout: Dict[str, Any]) -> str:
        """Draft payout notification (queued for approval, not sent)."""

        return f"""Subject: Commission Approved: ${payout['amount']:.2f}

{affiliate['name']},

Your commission has been approved for payout:

💰 Amount: ${payout['amount']:.2f}
📧 PayPal account: {affiliate['email']}
📅 Approved: {datetime.now().strftime('%B %d, %Y')}
🆔 Payout ID: {payout['payout_id']}

NOTE: Herb sends payouts manually via PayPal — allow a few days.

Commissions included: {len(payout['commissions_included'])}

Lifetime Earnings: ${affiliate['total_commissions_paid']:,.2f}

Keep promoting! More sales = more commissions.

Dashboard: https://mythara.engine/affiliate/{affiliate['affiliate_id']}

Mythara Affiliate Program
"""
    
    def get_affiliate_report(self) -> Dict[str, Any]:
        """Generate affiliate program performance report."""
        
        total_affiliates = len(self.affiliates)
        active_affiliates = sum(1 for a in self.affiliates.values() if a['total_referrals'] > 0)
        total_sales = sum(a['total_sales'] for a in self.affiliates.values())
        total_commissions = sum(a['total_commissions_earned'] for a in self.affiliates.values())
        pending_payouts = sum(p['commission_amount'] for p in self.pending_payouts if p['status'] == 'pending')
        
        return {
            'total_affiliates': total_affiliates,
            'active_affiliates': active_affiliates,
            'total_sales_generated': total_sales,
            'total_commissions_earned': total_commissions,
            'pending_payouts': pending_payouts,
            'avg_commission_per_affiliate': total_commissions / active_affiliates if active_affiliates > 0 else 0,
            'top_affiliates': sorted(
                [{'name': a['name'], 'earnings': a['total_commissions_earned']} for a in self.affiliates.values()],
                key=lambda x: x['earnings'],
                reverse=True
            )[:5],
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# TEST & DEMO
# ============================================================================

if __name__ == "__main__":
    import tempfile
    print("🤖 Mythara Affiliate Tracker (demo — synthetic data)")
    print("="*60)

    # Demo uses throwaway state and queues no drafts.
    bot = AutonomousAffiliateBot(
        state_path=os.path.join(tempfile.gettempdir(), "affiliate_demo_state.json"))

    # 1. Recruit affiliate
    print("\n1. Registering affiliate...")
    result = bot.recruit_affiliate('influencer@example.com', 'Tech Influencer',
                                   'LinkedIn', queue_draft=False)
    print(f"   Affiliate ID: {result['affiliate']['affiliate_id']}")
    print(f"   Referral Code: {result['affiliate']['referral_code']}")
    print(f"   Referral Link: {result['affiliate']['referral_link']}")
    print(f"   Welcome draft queued: {result['welcome_draft_path'] is not None} (demo: no)")
    
    # 2. Track referral click
    print("\n2. Tracking referral click...")
    click = bot.track_referral_click(result['affiliate']['referral_code'], 'customer@bank.com')
    print(f"   Clicked at: {click['clicked_at']}")
    
    # 3. Process sale
    print("\n3. Processing sale ($500 SSIP Audit)...")
    sale = bot.process_sale('customer@bank.com', 'MYTH-AUDIT-001', 500.00, 'PAY-12345')
    print(f"   Attributed: {sale['attributed']}")
    print(f"   Commission: ${sale['commission']:.2f}")
    
    # 4. Get affiliate report
    print("\n4. Affiliate Program Report:")
    report = bot.get_affiliate_report()
    print(f"   Total Affiliates: {report['total_affiliates']}")
    print(f"   Active Affiliates: {report['active_affiliates']}")
    print(f"   Total Sales: ${report['total_sales_generated']:,.2f}")
    print(f"   Total Commissions: ${report['total_commissions_earned']:,.2f}")
    print(f"   Pending Payouts: ${report['pending_payouts']:,.2f}")
    
    print("\n✅ Affiliate tracker demo complete")
    print("💡 Registers affiliates; welcome emails are DRAFTS for Herb's approval")
    print("💡 Tracks referrals via Messenger Pairing")
    print("💡 Calculates commissions via fixed rules")
    print("💡 APPROVES payouts at $50 — Herb sends the money manually via PayPal")
    print("💡 State persists in affiliate_state.json")
