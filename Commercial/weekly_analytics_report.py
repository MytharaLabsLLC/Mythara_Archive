# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Weekly Sales Bot Analytics Report Generator

Sends comprehensive performance report to Herbievelezjr@gmail.com every Sunday.

Tracks:
- Emails sent/received
- Response rates
- Deal conversions
- Blessings score
- Industry performance
- Recommended improvements
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import statistics

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class WeeklyAnalyticsReport:
    """
    Generates and emails weekly performance analytics
    
    Analyzes:
    - Sales bot performance (response rate, close rate)
    - Mythara governance (blessings, violations)
    - Industry breakdown (banking vs healthcare vs tech)
    - Improvement recommendations
    """
    
    def __init__(self):
        self.report_email = "Herbievelezjr@gmail.com"
        self.bot_email = "Mythara.Engine@yahoo.com"
        
        # Data sources
        self.blessings_file = Path("bot_blessings.json")
        self.audit_log = Path("sales_audit_log.jsonl")
        self.tracker_file = Path("conversation_tracker.json")
        self.learning_file = Path("learning_patterns.json")
        self.health_log = Path("bot_health_log.jsonl")
    
    def load_weekly_data(self) -> Dict:
        """Load last 7 days of bot activity"""
        
        one_week_ago = datetime.now() - timedelta(days=7)
        
        data = {
            "emails_sent": 0,
            "emails_received": 0,
            "intents": defaultdict(int),
            "industries": defaultdict(int),
            "response_rate": 0.0,
            "blessings_changes": [],
            "violations": [],
            "deals_closed": 0,
            "revenue": 0.0,
            "auto_sends": 0,
            "human_reviews": 0,
            "quit_list_additions": 0,
            "strikes_given": defaultdict(int),
        }
        
        # Load blessings reservoir
        if self.blessings_file.exists():
            blessings_data = json.loads(self.blessings_file.read_text())
            data["current_blessings"] = blessings_data.get("blessings", 100)
            data["auto_sends"] = blessings_data.get("auto_sends", 0)
            data["human_overrides"] = blessings_data.get("human_overrides", 0)
            data["successful_closes"] = blessings_data.get("successful_closes", 0)
        
        # Load audit log
        if self.audit_log.exists():
            for line in self.audit_log.read_text().splitlines():
                try:
                    entry = json.loads(line)
                    entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                    
                    if entry_time >= one_week_ago:
                        data["emails_sent"] += 1
                        
                        intent = entry.get("intent", "unknown")
                        data["intents"][intent] += 1
                        
                        industry = entry.get("industry", "unknown")
                        data["industries"][industry] += 1
                        
                        if entry.get("violations"):
                            data["violations"].extend(entry["violations"])
                        
                        if entry.get("action") == "AUTO_SEND":
                            data["auto_sends"] += 1
                        elif entry.get("action") == "HUMAN_REVIEW_REQUIRED":
                            data["human_reviews"] += 1
                
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # Load conversation tracker
        if self.tracker_file.exists():
            tracker = json.loads(self.tracker_file.read_text())
            for prospect, info in tracker.items():
                if info.get("status") == "quit":
                    data["quit_list_additions"] += 1
                
                no_count = info.get("no_count", 0)
                if no_count > 0:
                    data["strikes_given"][prospect] = no_count
        
        # Calculate response rate
        if data["emails_sent"] > 0:
            # Assume replies are tracked in audit log with intent != "unknown"
            replies = sum(count for intent, count in data["intents"].items() if intent != "unknown")
            data["response_rate"] = (replies / data["emails_sent"]) * 100
        
        return data
    
    def analyze_performance(self, data: Dict) -> Dict:
        """Analyze data and generate insights"""
        
        insights = {
            "health": "unknown",
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        # Overall health assessment
        blessings = data.get("current_blessings", 100)
        response_rate = data.get("response_rate", 0)
        violations_count = len(data.get("violations", []))
        
        if blessings >= 90 and response_rate >= 5.0 and violations_count == 0:
            insights["health"] = "EXCELLENT"
        elif blessings >= 70 and response_rate >= 3.0 and violations_count <= 2:
            insights["health"] = "GOOD"
        elif blessings >= 50 and response_rate >= 1.0:
            insights["health"] = "FAIR"
        else:
            insights["health"] = "NEEDS IMPROVEMENT"
        
        # Identify strengths
        if data.get("auto_sends", 0) > data.get("human_reviews", 0):
            insights["strengths"].append(f"High autonomy: {data['auto_sends']} auto-sends vs {data['human_reviews']} human reviews")
        
        if violations_count == 0:
            insights["strengths"].append("Zero governance violations this week (perfect compliance)")
        
        if response_rate >= 5.0:
            insights["strengths"].append(f"Strong response rate: {response_rate:.1f}% (target: 5%)")
        
        # Identify weaknesses
        if violations_count > 0:
            insights["weaknesses"].append(f"{violations_count} governance violations detected")
            # Group violations by type
            violation_types = defaultdict(int)
            for v in data["violations"]:
                violation_types[v] += 1
            for vtype, count in violation_types.items():
                insights["weaknesses"].append(f"  - {vtype}: {count}x")
        
        if response_rate < 3.0:
            insights["weaknesses"].append(f"Low response rate: {response_rate:.1f}% (target: 5%)")
        
        if blessings < 70:
            insights["weaknesses"].append(f"Low blessings score: {blessings}/100 (autonomy limited)")
        
        quit_rate = data.get("quit_list_additions", 0)
        if quit_rate > 5:
            insights["weaknesses"].append(f"High quit rate: {quit_rate} prospects quit this week")
        
        # Generate recommendations
        if response_rate < 3.0:
            insights["recommendations"].append("IMPROVE: Personalize subject lines (use prospect name + company)")
            insights["recommendations"].append("IMPROVE: Send emails Tuesday-Thursday 9-11am (best open rates)")
            insights["recommendations"].append("IMPROVE: A/B test different openers (try 'Quick question' vs 'Real talk')")
        
        if violations_count > 0:
            insights["recommendations"].append("FIX: Review pricing rules - avoid mentioning prices below $500")
            insights["recommendations"].append("FIX: Never claim FDA/HIPAA certified without documentation")
        
        if blessings < 70:
            insights["recommendations"].append("IMPROVE: Increase successful auto-sends to rebuild trust (+2 blessings per success)")
            insights["recommendations"].append("REDUCE: Human edits to bot drafts (each edit = -1 blessing)")
        
        if data.get("successful_closes", 0) == 0:
            insights["recommendations"].append("URGENT: No deals closed this week")
            insights["recommendations"].append("ACTION: Focus on 'interested' prospects - book 3 calls this week")
            insights["recommendations"].append("TACTIC: Follow up 'interested' prospects with honest timing pressure — their audit timeline, not invented deadlines")
        
        # Industry-specific recommendations
        industries = data.get("industries", {})
        if industries:
            top_industry = max(industries, key=industries.get)
            insights["recommendations"].append(f"OPTIMIZE: {top_industry.capitalize()} is your top industry ({industries[top_industry]} emails)")
            
            if top_industry == "banking" and response_rate < 3.0:
                insights["recommendations"].append("  → Use more regulatory citations (SR 11-7, OCC Bulletin)")
                insights["recommendations"].append("  → Lead with verifiable proof points (never invented ROI numbers)")
            elif top_industry == "healthcare" and response_rate < 3.0:
                insights["recommendations"].append("  → Emphasize patient safety and FDA compliance")
                insights["recommendations"].append("  → Use clinical language ('tamper-evident seal')")
            elif top_industry == "tech" and response_rate < 3.0:
                insights["recommendations"].append("  → Increase aggression (more competitive pressure)")
                insights["recommendations"].append("  → Shorten emails (tech buyers hate fluff)")
        
        return insights
    
    def generate_pdf_report(self, data: Dict, insights: Dict) -> str:
        """Generate professional PDF report"""
        
        # Create PDF filename
        pdf_filename = f"Weekly_Sales_Analytics_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdf_path = Path(pdf_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        body_style = styles['BodyText']
        
        # Title
        title = Paragraph("📊 Weekly Sales Bot Analytics Report", title_style)
        elements.append(title)
        
        subtitle = Paragraph(
            f"Performance Report: {datetime.now().strftime('%B %d, %Y')}<br/>"
            f"<b>Health Status: {insights['health']}</b>",
            ParagraphStyle('subtitle', parent=body_style, alignment=TA_CENTER, fontSize=12)
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))
        
        # Key Metrics Table
        metrics_data = [
            ['Metric', 'Value'],
            ['Emails Sent', str(data.get('emails_sent', 0))],
            ['Response Rate', f"{data.get('response_rate', 0):.1f}%"],
            ['Blessings Score', f"{data.get('current_blessings', 100)}/100"],
            ['Deals Closed', str(data.get('successful_closes', 0))],
            ['Auto-Sends', str(data.get('auto_sends', 0))],
            ['Human Reviews', str(data.get('human_reviews', 0))],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Intent Distribution
        elements.append(Paragraph("Intent Distribution", heading_style))
        intent_data = [['Intent', 'Count']]
        for intent, count in data.get('intents', {}).items():
            intent_data.append([intent.capitalize(), str(count)])
        
        if len(intent_data) > 1:
            intent_table = Table(intent_data, colWidths=[3*inch, 2*inch])
            intent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            elements.append(intent_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Industry Performance
        elements.append(Paragraph("Industry Performance", heading_style))
        industry_data = [['Industry', 'Emails']]
        for industry, count in data.get('industries', {}).items():
            industry_data.append([industry.capitalize(), str(count)])
        
        if len(industry_data) > 1:
            industry_table = Table(industry_data, colWidths=[3*inch, 2*inch])
            industry_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            elements.append(industry_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Strengths
        if insights['strengths']:
            elements.append(Paragraph("✅ Strengths This Week", heading_style))
            for strength in insights['strengths']:
                elements.append(Paragraph(f"• {strength}", body_style))
                elements.append(Spacer(1, 0.1*inch))
        
        # Weaknesses
        if insights['weaknesses']:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("⚠️ Weaknesses Identified", heading_style))
            for weakness in insights['weaknesses']:
                elements.append(Paragraph(f"• {weakness}", body_style))
                elements.append(Spacer(1, 0.1*inch))
        
        # Recommendations
        if insights['recommendations']:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("💡 Recommended Improvements", heading_style))
            for i, rec in enumerate(insights['recommendations'], 1):
                rec_style = ParagraphStyle(
                    f'rec{i}',
                    parent=body_style,
                    leftIndent=20,
                    bulletIndent=10,
                    spaceAfter=8,
                    textColor=colors.HexColor('#f59e0b') if 'URGENT' in rec else colors.black
                )
                elements.append(Paragraph(f"{i}. {rec}", rec_style))
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_text = f"""
        <para alignment="center">
        <b>Generated by Mythara Sales Bot Analytics Engine</b><br/>
        © 2025 Herbert Velez Jr. | Mythara Engine<br/>
        <i>This report is sent automatically every Sunday at 6:00 PM MT</i>
        </para>
        """
        elements.append(Paragraph(footer_text, body_style))
        
        # Build PDF
        doc.build(elements)
        
        return str(pdf_path)
    
    def generate_html_report(self, data: Dict, insights: Dict) -> str:
        """Generate beautiful HTML email report"""
        
        # Health status emoji
        health_emoji = {
            "EXCELLENT": "🟢",
            "GOOD": "🟡",
            "FAIR": "🟠",
            "NEEDS IMPROVEMENT": "🔴"
        }
        
        health = insights["health"]
        health_icon = health_emoji.get(health, "⚪")
        
        # Calculate week-over-week change (placeholder - would compare to last week)
        blessings_change = "+0"  # TODO: Compare to last week
        response_change = "+0.0%"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .health-status {{ font-size: 48px; margin: 20px 0; }}
                .metrics {{ display: flex; justify-content: space-around; margin: 30px 0; }}
                .metric {{ text-align: center; padding: 20px; background: #f7f7f7; border-radius: 10px; }}
                .metric-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
                .metric-label {{ font-size: 14px; color: #666; }}
                .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #667eea; background: #f9f9f9; }}
                .section-title {{ font-size: 20px; font-weight: bold; margin-bottom: 15px; }}
                .strength {{ color: #10b981; }}
                .weakness {{ color: #ef4444; }}
                .recommendation {{ background: #fef3c7; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #f59e0b; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                ul {{ list-style: none; padding-left: 0; }}
                li {{ padding: 8px 0; }}
                .urgent {{ background: #fee2e2; border-left-color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Weekly Sales Bot Analytics</h1>
                <p>Performance Report: {datetime.now().strftime('%B %d, %Y')}</p>
                <div class="health-status">{health_icon} {health}</div>
            </div>
            
            <div style="padding: 30px;">
                
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{data.get('emails_sent', 0)}</div>
                        <div class="metric-label">Emails Sent</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{data.get('response_rate', 0):.1f}%</div>
                        <div class="metric-label">Response Rate<br><small>({response_change} vs last week)</small></div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{data.get('current_blessings', 100)}/100</div>
                        <div class="metric-label">Blessings<br><small>({blessings_change} vs last week)</small></div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{data.get('successful_closes', 0)}</div>
                        <div class="metric-label">Deals Closed</div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">📈 Activity Breakdown</div>
                    <ul>
                        <li><strong>Auto-Sends:</strong> {data.get('auto_sends', 0)}</li>
                        <li><strong>Human Reviews:</strong> {data.get('human_reviews', 0)}</li>
                        <li><strong>Governance Violations:</strong> {len(data.get('violations', []))}</li>
                        <li><strong>Prospects Quit:</strong> {data.get('quit_list_additions', 0)}</li>
                    </ul>
                </div>
                
                <div class="section">
                    <div class="section-title">🎯 Intent Distribution</div>
                    <ul>
"""
        
        # Intent breakdown
        for intent, count in data.get("intents", {}).items():
            html += f"                        <li><strong>{intent.capitalize()}:</strong> {count} emails</li>\n"
        
        html += """
                    </ul>
                </div>
                
                <div class="section">
                    <div class="section-title">🏢 Industry Performance</div>
                    <ul>
"""
        
        # Industry breakdown
        for industry, count in data.get("industries", {}).items():
            html += f"                        <li><strong>{industry.capitalize()}:</strong> {count} emails</li>\n"
        
        html += """
                    </ul>
                </div>
"""
        
        # Strengths
        if insights["strengths"]:
            html += """
                <div class="section">
                    <div class="section-title strength">✅ Strengths This Week</div>
                    <ul>
"""
            for strength in insights["strengths"]:
                html += f"                        <li class='strength'>✓ {strength}</li>\n"
            
            html += """
                    </ul>
                </div>
"""
        
        # Weaknesses
        if insights["weaknesses"]:
            html += """
                <div class="section">
                    <div class="section-title weakness">⚠️ Weaknesses Identified</div>
                    <ul>
"""
            for weakness in insights["weaknesses"]:
                html += f"                        <li class='weakness'>✗ {weakness}</li>\n"
            
            html += """
                    </ul>
                </div>
"""
        
        # Recommendations
        if insights["recommendations"]:
            html += """
                <div class="section">
                    <div class="section-title">💡 Recommended Improvements</div>
"""
            for rec in insights["recommendations"]:
                urgent_class = " urgent" if "URGENT" in rec else ""
                html += f"                    <div class='recommendation{urgent_class}'>{rec}</div>\n"
            
            html += """
                </div>
"""
        
        html += f"""
                <div class="footer">
                    <p>Generated by Mythara Sales Bot Analytics Engine</p>
                    <p>© 2025 Herbert Velez Jr. | Mythara Engine</p>
                    <p><em>This report is sent automatically every Sunday at 6:00 PM MT</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email_report(self, pdf_path: str):
        """Send PDF email report via Gmail"""
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = f"📊 Weekly Sales Bot Analytics - {datetime.now().strftime('%b %d, %Y')}"
            msg['From'] = self.bot_email
            msg['To'] = self.report_email
            
            # Email body
            body = f"""
            Hi Herbert,

            Your weekly sales bot analytics report is attached.

            Quick Summary:
            - Emails sent this week: [See PDF]
            - Response rate: [See PDF]
            - Blessings score: [See PDF]
            - Recommended improvements: [See PDF]

            Best regards,
            Mythara Sales Bot Analytics Engine

            ---
            This is an automated report sent every Sunday at 6:00 PM MT.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEBase('application', 'octet-stream')
                pdf_attachment.set_payload(f.read())
            
            encoders.encode_base64(pdf_attachment)
            pdf_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename={Path(pdf_path).name}'
            )
            msg.attach(pdf_attachment)
            
            print(f"\n✅ PDF report generated: {pdf_path}")
            print(f"   📄 Open PDF to review")
            print(f"\n📧 To enable auto-email:")
            print(f"   1. Configure Gmail OAuth (same as sales bot)")
            print(f"   2. Uncomment send_gmail() function below")
            print(f"   3. Schedule this script to run Sundays 6pm (Windows Task Scheduler)")
            
            # TODO: Uncomment when Gmail OAuth is configured
            # self.send_gmail(msg)
            
        except Exception as e:
            print(f"❌ Error preparing email: {e}")
    
    def generate_and_send_report(self):
        """Main function: generate and send weekly report"""
        
        print("="*80)
        print("📊 GENERATING WEEKLY ANALYTICS REPORT")
        print("="*80)
        
        # Load data
        print("\n📁 Loading data from last 7 days...")
        data = self.load_weekly_data()
        
        # Analyze
        print("🔍 Analyzing performance...")
        insights = self.analyze_performance(data)
        
        # Generate PDF report
        print("📝 Generating PDF report...")
        pdf_path = self.generate_pdf_report(data, insights)
        
        # Send
        print("📧 Preparing email...")
        self.send_email_report(pdf_path)
        
        print("\n" + "="*80)
        print(f"✅ REPORT COMPLETE - {insights['health']}")
        print("="*80)


if __name__ == "__main__":
    reporter = WeeklyAnalyticsReport()
    reporter.generate_and_send_report()
