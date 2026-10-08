import os
# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Mythara VP of Public Affairs - Autonomous Brand & Communication Management
Manages public image, social media, press releases, community engagement, crisis response.

Uses Mythara SSIP:
- Blessings Reservoir: Tracks brand sentiment (0-100 score)
- MessengerPairing: Links campaigns to audience segments
- Sanctification: Brand voice guidelines (immutable)
- Clause Invocation: Communication templates
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

# Orchestrator connection
ORCHESTRATOR_URL = "http://localhost:5000"
# QUICKFIX FIX: Moved to environment variable (CWE-798)
VP_MASTER_TOKEN = os.getenv("VP_MASTER_TOKEN", "")  # Set via environment

class BrandSentimentReservoir:
    """
    Tracks public sentiment about Mythara brand (SSIP Blessings Reservoir pattern).
    Sentiment score 0-100 based on social media, reviews, mentions.
    """
    
    def __init__(self):
        self.sentiment_scores = {}  # {platform: score}
        self.mentions = []
    
    def add_mention(self, platform: str, sentiment: str, reach: int, content: str):
        """Track brand mention and update sentiment."""
        mention = {
            'timestamp': datetime.now().isoformat(),
            'platform': platform,
            'sentiment': sentiment,  # 'positive', 'neutral', 'negative'
            'reach': reach,
            'content': content[:200]
        }
        self.mentions.append(mention)
        
        # Update platform sentiment score
        if platform not in self.sentiment_scores:
            self.sentiment_scores[platform] = 50  # Start neutral
        
        # Adjust score based on sentiment and reach
        impact = (reach / 1000) * 10  # Higher reach = bigger impact
        if sentiment == 'positive':
            self.sentiment_scores[platform] = min(100, self.sentiment_scores[platform] + impact)
        elif sentiment == 'negative':
            self.sentiment_scores[platform] = max(0, self.sentiment_scores[platform] - impact)
        
        return mention
    
    def get_overall_sentiment(self) -> float:
        """Calculate overall brand sentiment across all platforms."""
        if not self.sentiment_scores:
            return 50.0  # Neutral
        return sum(self.sentiment_scores.values()) / len(self.sentiment_scores)
    
    def get_recent_mentions(self, hours: int = 24) -> List[Dict]:
        """Get mentions from last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [m for m in self.mentions if datetime.fromisoformat(m['timestamp']) > cutoff]


class CommunicationClause:
    """
    Invokable communication template (SSIP Clause pattern).
    Each clause represents a type of public statement.
    """
    
    def __init__(self, clause_id: str, name: str, template: str, channels: List[str]):
        self.clause_id = clause_id
        self.name = name
        self.template = template
        self.channels = channels  # ['twitter', 'linkedin', 'press']
        self.invocation_count = 0
        self.integrity_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate SSIP integrity hash."""
        data = f"{self.clause_id}{self.name}{self.template}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def invoke(self, context: Dict[str, str]) -> Dict[str, Any]:
        """Invoke clause with context to generate communication."""
        message = self.template
        for key, value in context.items():
            message = message.replace(f"{{{key}}}", str(value))
        
        self.invocation_count += 1
        
        return {
            'clause_id': self.clause_id,
            'message': message,
            'channels': self.channels,
            'invoked_at': datetime.now().isoformat(),
            'integrity_hash': self.integrity_hash
        }


class AudienceSegment:
    """
    Messenger Pairing pattern - links campaigns to specific audience groups.
    """
    
    def __init__(self):
        self.segments = {
            'enterprise': {
                'interests': ['security', 'compliance', 'ROI', 'enterprise solutions'],
                'platforms': ['linkedin', 'industry_press'],
                'tone': 'professional'
            },
            'developers': {
                'interests': ['API', 'integration', 'documentation', 'open source'],
                'platforms': ['twitter', 'github', 'reddit'],
                'tone': 'technical'
            },
            'investors': {
                'interests': ['revenue', 'growth', 'market opportunity', 'team'],
                'platforms': ['linkedin', 'pitch_decks'],
                'tone': 'confident'
            },
            'media': {
                'interests': ['innovation', 'impact', 'story', 'founders'],
                'platforms': ['press_release', 'email'],
                'tone': 'narrative'
            }
        }
    
    def get_segment(self, segment_name: str) -> Dict[str, Any]:
        """Get audience segment details."""
        return self.segments.get(segment_name, self.segments['enterprise'])
    
    def match_content_to_segment(self, keywords: List[str]) -> str:
        """Match content keywords to best audience segment."""
        scores = {}
        for segment, details in self.segments.items():
            score = sum(1 for kw in keywords if kw.lower() in [i.lower() for i in details['interests']])
            scores[segment] = score
        
        return max(scores, key=scores.get)


class MytharaPublicAffairsVP:
    """
    VP of Public Affairs - Autonomous brand and communication management.
    Handles social media, press releases, crisis response, community engagement.
    """
    
    def __init__(self):
        self.bot_id = "public_affairs_vp"
        self.bot_token = None
        self.sentiment_reservoir = BrandSentimentReservoir()
        self.audience_segments = AudienceSegment()
        self.sanctified_guidelines = self._init_brand_guidelines()
        self.communication_clauses = self._initialize_clauses()
        self.campaigns = []
        self.crisis_events = []
        
        # Register with orchestrator
        self._register()
    
    def _init_brand_guidelines(self) -> Dict[str, Any]:
        """Initialize sanctified brand voice guidelines (immutable)."""
        guidelines = {
            'voice': {
                'professional': True,
                'innovative': True,
                'transparent': True,
                'technical': True
            },
            'prohibited_topics': [
                'politics',
                'religion',
                'controversial social issues',
                'competitor criticism'
            ],
            'required_disclaimers': [
                'All rights reserved',
                'Enterprise licensing required'
            ],
            'tone_scale': {
                'enterprise': 'authoritative',
                'developers': 'collaborative',
                'investors': 'confident',
                'media': 'storytelling'
            },
            'response_times': {
                'crisis': '1 hour',
                'negative_mention': '4 hours',
                'inquiry': '24 hours',
                'positive_mention': '48 hours'
            }
        }
        
        guidelines['integrity_hash'] = hashlib.sha256(
            json.dumps(guidelines, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        return guidelines
    
    def _initialize_clauses(self) -> Dict[str, CommunicationClause]:
        """Initialize communication clauses."""
        return {
            'PRODUCT_LAUNCH': CommunicationClause(
                'CLAUSE_PR_001',
                'Product Launch Announcement',
                "🚀 Introducing {product_name}: {value_prop}. {details} Learn more: {link}",
                ['twitter', 'linkedin', 'press_release']
            ),
            'MILESTONE': CommunicationClause(
                'CLAUSE_MS_001',
                'Company Milestone',
                "🎉 Mythara milestone: {achievement}! {impact} Thank you to {stakeholders}. {next_steps}",
                ['twitter', 'linkedin', 'blog']
            ),
            'CRISIS_RESPONSE': CommunicationClause(
                'CLAUSE_CR_001',
                'Crisis Communication',
                "We're aware of {issue}. Status: {status}. Actions taken: {actions}. ETA: {eta}. Updates: {link}",
                ['twitter', 'linkedin', 'email', 'status_page']
            ),
            'THOUGHT_LEADERSHIP': CommunicationClause(
                'CLAUSE_TL_001',
                'Industry Insight',
                "{topic}: {insight}. Why it matters: {impact}. Our approach: {solution}. Read more: {link}",
                ['linkedin', 'blog', 'medium']
            ),
            'COMMUNITY_ENGAGEMENT': CommunicationClause(
                'CLAUSE_CE_001',
                'Community Response',
                "Thanks {user} for {action}! {appreciation} {call_to_action}",
                ['twitter', 'reddit', 'discord']
            ),
            'INVESTOR_UPDATE': CommunicationClause(
                'CLAUSE_IV_001',
                'Investor Communication',
                "Q{quarter} Update: {metric} grew {growth}%. Key wins: {achievements}. Next focus: {priorities}.",
                ['email', 'pitch_deck']
            )
        }
    
    def _register(self):
        """Register Public Affairs VP with orchestrator."""
        try:
            response = requests.post(f"{ORCHESTRATOR_URL}/register_bot", json={
                'vp_token': VP_MASTER_TOKEN,
                'bot_id': self.bot_id,
                'bot_name': 'Public Affairs VP Bot'
            })
            if response.status_code == 200:
                self.bot_token = response.json()['bot_token']
                print(f"[OK] Registered as Public Affairs VP")
                print(f"   Token: {self.bot_token[:16]}...")
            else:
                print(f"[WARN] Registration failed: {response.text}")
        except Exception as e:
            print(f"[WARN] Could not register with orchestrator: {e}")
            print("   Running in standalone mode")
    
    def monitor_brand_mentions(self, platform: str = 'all') -> Dict[str, Any]:
        """
        Monitor social media and web for brand mentions.
        In production: would integrate with Twitter API, Google Alerts, etc.
        """
        
        # Sample mentions (SIMULATED for testing — these are not real
        # customer statements; no customer has implemented SSIP)
        sample_mentions = [
            {
                'platform': 'twitter',
                'sentiment': 'positive',
                'reach': 5000,
                'content': 'Reading up on @MytharaEngine SSIP — interesting approach to AI safety guardrails.'
            },
            {
                'platform': 'linkedin',
                'sentiment': 'neutral',
                'reach': 1200,
                'content': 'Evaluating Mythara Engine for our enterprise AI governance needs.'
            },
            {
                'platform': 'reddit',
                'sentiment': 'positive',
                'reach': 8000,
                'content': 'Mythara symbolic integrity writeup is a solid read on AI safety tooling.'
            }
        ]
        
        monitored = []
        for mention in sample_mentions:
            if platform == 'all' or mention['platform'] == platform:
                recorded = self.sentiment_reservoir.add_mention(
                    mention['platform'],
                    mention['sentiment'],
                    mention['reach'],
                    mention['content']
                )
                monitored.append(recorded)
        
        return {
            'platform': platform,
            'new_mentions': len(monitored),
            'overall_sentiment': self.sentiment_reservoir.get_overall_sentiment(),
            'mentions': monitored
        }
    
    def create_campaign(self, campaign_type: str, target_audience: str, objectives: List[str]) -> Dict[str, Any]:
        """
        Create public affairs campaign.
        campaign_type: 'product_launch', 'thought_leadership', 'crisis_response'
        """
        
        campaign = {
            'campaign_id': hashlib.sha256(f"{campaign_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            'campaign_type': campaign_type,
            'target_audience': target_audience,
            'objectives': objectives,
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'messages': [],
            'metrics': {
                'reach': 0,
                'engagement': 0,
                'sentiment_shift': 0
            }
        }
        
        # Get audience segment details
        segment = self.audience_segments.get_segment(target_audience)
        campaign['platforms'] = segment['platforms']
        campaign['tone'] = segment['tone']
        
        # Generate initial messages based on campaign type
        if campaign_type == 'product_launch':
            clause = self.communication_clauses['PRODUCT_LAUNCH']
            message = clause.invoke({
                'product_name': 'Mythara SSIP Audit Service',
                'value_prop': 'Enterprise AI safety compliance in 48 hours',
                'details': 'Cryptographic integrity verification, regulatory readiness, zero-trust architecture.',
                'link': 'https://mythara.engine/audit'
            })
            campaign['messages'].append(message)
        
        elif campaign_type == 'thought_leadership':
            clause = self.communication_clauses['THOUGHT_LEADERSHIP']
            message = clause.invoke({
                'topic': 'AI Safety Beyond Alignment',
                'insight': 'Traditional alignment focuses on goals. Symbolic integrity ensures immutable safety constraints.',
                'impact': 'Prevents reward hacking, goal drift, and unintended consequences.',
                'solution': 'Mythara SSIP: Sanctification + Shadow Resolver + Blessings Reservoir',
                'link': 'https://mythara.engine/blog/ssip-explained'
            })
            campaign['messages'].append(message)
        
        self.campaigns.append(campaign)
        
        return campaign
    
    def handle_crisis(self, issue: str, severity: str) -> Dict[str, Any]:
        """
        Handle crisis communication (Shadow_Resolver pattern for brand protection).
        severity: 'low', 'medium', 'high', 'critical'
        """
        
        crisis = {
            'crisis_id': hashlib.sha256(f"{issue}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            'issue': issue,
            'severity': severity,
            'detected_at': datetime.now().isoformat(),
            'status': 'responding',
            'actions': []
        }
        
        # Immediate response based on severity
        if severity in ['high', 'critical']:
            # Invoke crisis response clause immediately
            clause = self.communication_clauses['CRISIS_RESPONSE']
            
            response_message = clause.invoke({
                'issue': issue,
                'status': 'investigating',
                'actions': 'Team mobilized, root cause analysis in progress',
                'eta': '1 hour for initial findings',
                'link': 'https://status.mythara.engine'
            })
            
            crisis['actions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'immediate_public_response',
                'message': response_message,
                'sanctioned': True  # Approved by sanctified crisis protocol
            })
            
            # Alert stakeholders
            crisis['actions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'alert_stakeholders',
                'recipients': ['investors', 'customers', 'partners'],
                'sanctioned': True
            })
        
        elif severity == 'medium':
            # Prepare response within 4 hours
            crisis['actions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'monitor_and_prepare',
                'response_deadline': (datetime.now() + timedelta(hours=4)).isoformat(),
                'sanctioned': True
            })
        
        else:  # low
            # Acknowledge and track
            crisis['actions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'acknowledge_and_track',
                'response_deadline': (datetime.now() + timedelta(hours=24)).isoformat(),
                'sanctioned': True
            })
        
        self.crisis_events.append(crisis)
        
        return crisis
    
    def generate_press_release(self, subject: str, details: Dict[str, str]) -> Dict[str, Any]:
        """Generate formal press release."""
        
        press_release = {
            'release_id': hashlib.sha256(f"{subject}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            'subject': subject,
            'date': datetime.now().strftime('%B %d, %Y'),
            'content': f"""
FOR IMMEDIATE RELEASE

{subject}

{details.get('location', 'Remote')}, {datetime.now().strftime('%B %d, %Y')} – {details.get('lede', '')}

{details.get('body', '')}

{details.get('quote', '')}

{details.get('background', '')}

About Mythara Engine:
Mythara Engine builds symbolic safety integrity protocol (SSIP) tooling for enterprise AI systems. The approach combines cryptographic sanctification, emotional fidelity tracking, and zero-trust architecture. No certifications, customer counts, or revenue figures are claimed here.

Contact:
Mythara.Engine@yahoo.com
https://mythara.engine

###

""",
            'distribution_list': ['PR Newswire', 'TechCrunch', 'VentureBeat', 'AI News'],
            'embargo_until': None,
            'integrity_hash': hashlib.sha256(subject.encode()).hexdigest()[:16]
        }
        
        return press_release
    
    def respond_to_inquiry(self, inquiry_type: str, sender: str, question: str) -> Dict[str, Any]:
        """
        Respond to media/public inquiries.
        inquiry_type: 'media', 'customer', 'investor', 'general'
        """
        
        # Get appropriate tone from sanctified guidelines
        if inquiry_type == 'media':
            tone = self.sanctified_guidelines['tone_scale']['media']
            response_time = self.sanctified_guidelines['response_times']['inquiry']
        elif inquiry_type == 'investor':
            tone = self.sanctified_guidelines['tone_scale']['investors']
            response_time = self.sanctified_guidelines['response_times']['inquiry']
        else:
            tone = self.sanctified_guidelines['tone_scale']['enterprise']
            response_time = self.sanctified_guidelines['response_times']['inquiry']
        
        response = {
            'inquiry_id': hashlib.sha256(f"{sender}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            'inquiry_type': inquiry_type,
            'sender': sender,
            'question': question,
            'received_at': datetime.now().isoformat(),
            'response_deadline': (datetime.now() + timedelta(hours=24)).isoformat(),
            'tone': tone,
            'status': 'draft',
            'draft_response': self._generate_response_draft(inquiry_type, question, tone)
        }
        
        return response
    
    def _generate_response_draft(self, inquiry_type: str, question: str, tone: str) -> str:
        """Generate draft response to inquiry."""
        
        if 'pricing' in question.lower():
            return f"""Thank you for your interest in Mythara Engine.

Our enterprise SSIP solutions are customized based on scale, use case, and compliance requirements. Pricing starts at $500 for our SSIP Audit service (48-hour turnaround) and scales to annual enterprise licenses.

I'd be happy to schedule a call to discuss your specific needs and provide a tailored proposal.

Best regards,
Mythara Public Affairs Team
Mythara.Engine@yahoo.com"""
        
        elif 'security' in question.lower() or 'compliance' in question.lower():
            return f"""Thank you for asking about Mythara's security and compliance approach.

Our SSIP (Symbolic Safety Integrity Protocol) uses cryptographic sanctification to ensure AI behavior remains within defined safety boundaries. Key features:

• Zero-trust architecture with integrity hashing
• We are not SOC 2 certified — ask us for our current security documentation
• GDPR/CCPA data protection
• Immutable audit trails
• Shadow Resolver failsafe mechanisms

We'd be happy to provide our security whitepaper and schedule a technical deep dive.

Best regards,
Mythara Public Affairs Team"""
        
        else:
            return f"""Thank you for reaching out to Mythara Engine.

We appreciate your interest and will provide a detailed response within 24 hours. In the meantime, you can learn more about our SSIP technology at https://mythara.engine.

Best regards,
Mythara Public Affairs Team
Mythara.Engine@yahoo.com"""
    
    def analyze_public_perception(self) -> Dict[str, Any]:
        """Generate public perception analysis report."""
        
        overall_sentiment = self.sentiment_reservoir.get_overall_sentiment()
        recent_mentions = self.sentiment_reservoir.get_recent_mentions(hours=24)
        
        # Categorize mentions by sentiment
        positive = [m for m in recent_mentions if m['sentiment'] == 'positive']
        neutral = [m for m in recent_mentions if m['sentiment'] == 'neutral']
        negative = [m for m in recent_mentions if m['sentiment'] == 'negative']
        
        # Calculate total reach
        total_reach = sum(m['reach'] for m in recent_mentions)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'overall_sentiment': overall_sentiment,
            'sentiment_category': 'positive' if overall_sentiment > 60 else 'neutral' if overall_sentiment > 40 else 'negative',
            'metrics': {
                'total_mentions_24h': len(recent_mentions),
                'total_reach_24h': total_reach,
                'positive_mentions': len(positive),
                'neutral_mentions': len(neutral),
                'negative_mentions': len(negative)
            },
            'platform_breakdown': self.sentiment_reservoir.sentiment_scores,
            'top_mentions': recent_mentions[:5],
            'recommendations': []
        }
        
        # Generate recommendations
        if overall_sentiment < 60:
            analysis['recommendations'].append("Increase thought leadership content to improve brand perception")
        
        if len(negative) > 0:
            analysis['recommendations'].append(f"Address {len(negative)} negative mentions within 4 hours (sanctified guideline)")
        
        if total_reach < 10000:
            analysis['recommendations'].append("Launch engagement campaign to increase brand visibility")
        
        if not analysis['recommendations']:
            analysis['recommendations'].append("Maintain current communication strategy - sentiment positive")
        
        return analysis
    
    def generate_public_affairs_report(self) -> str:
        """Generate comprehensive Public Affairs status report."""
        
        perception = self.analyze_public_perception()
        recent_mentions = self.sentiment_reservoir.get_recent_mentions(hours=24)
        
        report = f"""
PUBLIC AFFAIRS VP REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

{'='*60}

BRAND SENTIMENT:
   Overall Score: {perception['overall_sentiment']:.1f}/100
   Category: {perception['sentiment_category'].upper()}
   
   24-Hour Metrics:
   • Total Mentions: {perception['metrics']['total_mentions_24h']}
   • Total Reach: {perception['metrics']['total_reach_24h']:,}
   • Positive: {perception['metrics']['positive_mentions']} mentions
   • Neutral: {perception['metrics']['neutral_mentions']} mentions
   • Negative: {perception['metrics']['negative_mentions']} mentions

{'='*60}

PLATFORM BREAKDOWN:
"""
        
        for platform, score in perception['platform_breakdown'].items():
            status = "[GOOD]" if score > 60 else "[WARN]" if score > 40 else "[ALERT]"
            report += f"   {status} {platform.capitalize()}: {score:.1f}/100\n"
        
        report += f"""
{'='*60}

ACTIVE CAMPAIGNS ({len(self.campaigns)}):
"""
        
        if self.campaigns:
            for campaign in self.campaigns[-3:]:
                report += f"\n   • {campaign['campaign_type'].upper()}"
                report += f"\n     Audience: {campaign['target_audience']}"
                report += f"\n     Status: {campaign['status']}"
                report += f"\n     Messages: {len(campaign['messages'])}"
        else:
            report += "\n   No active campaigns"
        
        report += f"""

{'='*60}

CRISIS EVENTS ({len(self.crisis_events)}):
"""
        
        if self.crisis_events:
            for crisis in self.crisis_events[-3:]:
                report += f"\n   • {crisis['issue']}"
                report += f"\n     Severity: {crisis['severity'].upper()}"
                report += f"\n     Status: {crisis['status']}"
                report += f"\n     Actions: {len(crisis['actions'])}"
        else:
            report += "\n   [OK] No crisis events"
        
        report += f"""

{'='*60}

SANCTIFIED BRAND GUIDELINES:
   Voice: Professional, Innovative, Transparent, Technical
   Prohibited: {', '.join(self.sanctified_guidelines['prohibited_topics'][:2])}...
   Crisis Response Time: {self.sanctified_guidelines['response_times']['crisis']}
   Integrity Hash: {self.sanctified_guidelines['integrity_hash']}

{'='*60}

RECOMMENDATIONS:
"""
        
        for rec in perception['recommendations']:
            report += f"\n   -> {rec}"
        
        report += f"""

{'='*60}

RECENT MENTIONS (Last 24h):
"""
        
        if recent_mentions:
            for mention in recent_mentions[:5]:
                sentiment_icon = "[+]" if mention['sentiment'] == 'positive' else "[-]" if mention['sentiment'] == 'negative' else "[=]"
                report += f"\n   {sentiment_icon} {mention['platform'].capitalize()} ({mention['reach']:,} reach)"
                report += f"\n      \"{mention['content'][:80]}...\""
        else:
            report += "\n   No recent mentions"
        
        report += f"""

Next check: {(datetime.now() + timedelta(hours=4)).strftime('%I:%M %p')}
"""
        
        return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("MYTHARA PUBLIC AFFAIRS VP")
    print("="*60)
    
    vp = MytharaPublicAffairsVP()
    
    # Monitor brand mentions
    print("\n1. Monitoring brand mentions...")
    mentions = vp.monitor_brand_mentions(platform='all')
    print(f"   New mentions: {mentions['new_mentions']}")
    print(f"   Overall sentiment: {mentions['overall_sentiment']:.1f}/100")
    
    # Create thought leadership campaign
    print("\n2. Creating thought leadership campaign...")
    campaign = vp.create_campaign(
        campaign_type='thought_leadership',
        target_audience='developers',
        objectives=['Educate on SSIP', 'Build technical credibility', 'Drive API adoption']
    )
    print(f"   Campaign ID: {campaign['campaign_id']}")
    print(f"   Target: {campaign['target_audience']}")
    print(f"   Platforms: {', '.join(campaign['platforms'])}")
    
    # Simulate crisis handling
    print("\n3. Testing crisis response...")
    crisis = vp.handle_crisis(
        issue="API latency spike detected in EU region",
        severity="medium"
    )
    print(f"   Crisis ID: {crisis['crisis_id']}")
    print(f"   Severity: {crisis['severity']}")
    print(f"   Actions: {len(crisis['actions'])}")
    
    # Generate press release
    print("\n4. Generating press release...")
    press_release = vp.generate_press_release(
        subject="Mythara Engine Ships Symbolic Safety Integrity Protocol for Enterprise AI",
        details={
            'location': 'Remote',
            'lede': 'Mythara Engine today announced the public release of its Symbolic Safety Integrity Protocol (SSIP) tooling for enterprise AI systems.',
            'body': 'The release adds cryptographic integrity hashing, immutable audit trails, and failsafe resolver patterns for teams building guardrails around AI deployments. Early design partners and pilots are not publicly disclosed; no customer claims are made in this draft.',
            'quote': '"AI safety cannot be an afterthought. SSIP is designed to help AI systems operate within defined ethical and operational boundaries," said Herbert Velez Jr.',
            'background': 'Mythara Engine builds SSIP integrity tooling for AI systems. The company is a solo-founded project; no funding rounds, revenue figures, or customer counts are claimed in this draft.'
        }
    )
    print(f"   Release ID: {press_release['release_id']}")
    print(f"   Distribution: {len(press_release['distribution_list'])} outlets")
    
    # Analyze public perception
    print("\n5. Analyzing public perception...")
    analysis = vp.analyze_public_perception()
    print(f"   Sentiment: {analysis['sentiment_category'].upper()} ({analysis['overall_sentiment']:.1f}/100)")
    print(f"   24h Reach: {analysis['metrics']['total_reach_24h']:,}")
    
    # Generate full report
    print("\n6. Generating Public Affairs report...")
    report = vp.generate_public_affairs_report()
    print(report)
    
    print("="*60)
    print("[OK] Public Affairs VP operational")
    print("Brand monitoring active")
    print("Crisis response ready")
    print("Communication clauses loaded")
