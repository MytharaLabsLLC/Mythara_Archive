#!/usr/bin/env python3
"""
Mythara Gopher - LOCAL DESKTOP APP
100% offline, privacy-first, no server required

Copyright © 2026 Mythara Labs LLC. All rights reserved.

This version runs entirely on the user's device:
- Soul Cradle analysis runs locally (no data sent to servers)
- Results saved to local SQLite database
- Direct email integration to law firms (user's own email account)
- Optional: Generate PDF reports user can send themselves
"""

import os
import sys
import json
import sqlite3
import hashlib
import smtplib
import webbrowser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

# Import Soul Cradle algorithm (runs 100% locally)
from soul_cradle_production import calculate_paradox_severity

# ============================================================================
# LOCAL DATABASE (SQLite - stored on user's device)
# ============================================================================

def get_local_db_path():
    """Get path to local database in user's home directory"""
    app_dir = Path.home() / ".mythara_gopher"
    app_dir.mkdir(exist_ok=True)
    return app_dir / "gopher_local.db"

def init_local_database():
    """Initialize local SQLite database"""
    db_path = get_local_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # User's cases
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            situation_text TEXT NOT NULL,
            paradox_severity REAL NOT NULL,
            classification TEXT NOT NULL,
            distress_score REAL,
            coercion_score REAL,
            contradiction_score REAL,
            action_taken TEXT,
            integrity_hash TEXT NOT NULL
        )
    """)
    
    # Attorney contacts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attorneys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            firm TEXT,
            email TEXT NOT NULL,
            phone TEXT,
            specialization TEXT,
            notes TEXT
        )
    """)
    
    # Seed default attorneys if empty
    cursor.execute("SELECT COUNT(*) FROM attorneys")
    if cursor.fetchone()[0] == 0:
        default_attorneys = [
            ("Frank Azar", "The Strong Arm", "frank@thestrongarm.com", "303-321-8887", 
             "Employment Law, Wage Theft, Discrimination", "Denver, CO - High success rate"),
            ("Generic Employment Attorney", "Legal Aid", "intake@employmentlegal.com", "", 
             "Employment Rights, Harassment", "Virtual - Free consultation")
        ]
        cursor.executemany("""
            INSERT INTO attorneys (name, firm, email, phone, specialization, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, default_attorneys)
    
    conn.commit()
    conn.close()
    return db_path

def save_case_locally(situation_text, result):
    """Save analysis to local database"""
    conn = sqlite3.connect(get_local_db_path())
    cursor = conn.cursor()
    
    # Create integrity hash
    integrity_data = f"{situation_text}:{result['paradox_severity']}:{datetime.utcnow().isoformat()}"
    integrity_hash = hashlib.sha256(integrity_data.encode()).hexdigest()
    
    cursor.execute("""
        INSERT INTO cases 
        (timestamp, situation_text, paradox_severity, classification, 
         distress_score, coercion_score, contradiction_score, integrity_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        situation_text,
        result['paradox_severity'],
        result['classification'],
        result['analysis']['distress_score'],
        result['analysis']['coercion_score'],
        result['analysis']['contradiction_score'],
        integrity_hash
    ))
    
    case_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return case_id, integrity_hash

def get_local_attorneys():
    """Get attorney list from local database"""
    conn = sqlite3.connect(get_local_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, firm, email, phone, specialization FROM attorneys")
    attorneys = cursor.fetchall()
    conn.close()
    return attorneys

# ============================================================================
# PDF GENERATION (Local export)
# ============================================================================

def generate_pdf_report(situation_text, result, case_id, integrity_hash):
    """Generate PDF report user can send to attorneys"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = Path.home() / "Documents" / f"Mythara_Gopher_Analysis_{timestamp}.pdf"
    pdf_path.parent.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30
    )
    story.append(Paragraph("Mythara Gopher - Employment Law Analysis", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Severity Alert
    severity_color = {
        "CRITICAL": colors.red,
        "HIGH": colors.orange,
        "MEDIUM": colors.yellow,
        "LOW": colors.lightblue,
        "MINIMAL": colors.lightgreen
    }.get(result['classification'], colors.grey)
    
    severity_table = Table([[
        Paragraph(f"<b>SEVERITY: {result['classification']}</b><br/>"
                 f"Score: {result['paradox_severity']:.3f}/1.0", styles['Normal'])
    ]], colWidths=[6*inch])
    severity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), severity_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white if result['classification'] in ['CRITICAL', 'HIGH'] else colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black)
    ]))
    story.append(severity_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Your Situation
    story.append(Paragraph("<b>Your Situation:</b>", styles['Heading2']))
    story.append(Paragraph(situation_text.replace('\n', '<br/>'), styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Analysis Details
    story.append(Paragraph("<b>Detailed Analysis:</b>", styles['Heading2']))
    analysis_data = [
        ['Metric', 'Score', 'Meaning'],
        ['Emotional Distress', f"{result['analysis']['distress_score']:.3f}", 'Psychological harm detected'],
        ['Coercion/Threats', f"{result['analysis']['coercion_score']:.3f}", 'Power imbalance, forced compliance'],
        ['Legal Contradiction', f"{result['analysis']['contradiction_score']:.3f}", 'Impossible legal situation']
    ]
    
    analysis_table = Table(analysis_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    analysis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(analysis_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Recommended Action
    story.append(Paragraph("<b>Recommended Action:</b>", styles['Heading2']))
    story.append(Paragraph(result['action_required'], styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Legal Notice
    story.append(Paragraph("<b>Important Legal Notice:</b>", styles['Heading3']))
    story.append(Paragraph(
        "This analysis is provided by Mythara Gopher AI for informational purposes only. "
        "It does NOT constitute legal advice. Only a licensed attorney can provide legal advice "
        "specific to your situation. Consult with an employment attorney immediately.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Integrity Footer
    story.append(Paragraph(f"<b>Case ID:</b> {case_id}", styles['Normal']))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"<b>Integrity Hash:</b> {integrity_hash[:32]}...", styles['Normal']))
    
    doc.build(story)
    return pdf_path

# ============================================================================
# EMAIL INTEGRATION (Direct from user's device)
# ============================================================================

def send_email_directly(attorney_email, subject, body, pdf_attachment=None, user_email=None, user_password=None):
    """
    Send email directly from user's device using their email account
    
    Note: User must enable "App Passwords" for Gmail/Outlook
    """
    if not user_email or not user_password:
        raise ValueError("Email credentials required. User must provide their own email/password.")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = user_email
    msg['To'] = attorney_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF if provided
    if pdf_attachment and os.path.exists(pdf_attachment):
        with open(pdf_attachment, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_attachment)}')
            msg.attach(part)
    
    # Detect email provider and use appropriate SMTP
    if 'gmail' in user_email.lower():
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
    elif 'outlook' in user_email.lower() or 'hotmail' in user_email.lower():
        smtp_server = 'smtp-mail.outlook.com'
        smtp_port = 587
    elif 'yahoo' in user_email.lower():
        smtp_server = 'smtp.mail.yahoo.com'
        smtp_port = 587
    else:
        smtp_server = 'smtp.gmail.com'  # Default fallback
        smtp_port = 587
    
    # Send email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(user_email, user_password)
    server.send_message(msg)
    server.quit()
    
    return True

# ============================================================================
# GUI APPLICATION
# ============================================================================

class GopherLocalApp:
    """Local desktop application for Mythara Gopher"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mythara Gopher - Employment Law Assistant")
        self.root.geometry("900x700")
        
        # Initialize database
        init_local_database()
        
        # Header
        header = ttk.Label(root, text="🦎 Mythara Gopher - Local Privacy-First Assistant", 
                          font=('Arial', 16, 'bold'))
        header.pack(pady=10)
        
        disclaimer = ttk.Label(root, text="100% Private - All analysis runs on YOUR device. No data sent to servers.",
                              font=('Arial', 10, 'italic'))
        disclaimer.pack()
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        ttk.Label(main_frame, text="Describe your employment situation:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        self.text_input = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD, font=('Arial', 11))
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=10)
        self.text_input.insert(1.0, "Example: My boss says I have to work unpaid overtime or I'll be fired...")
        
        # Analyze button
        analyze_btn = ttk.Button(main_frame, text="🔍 Analyze My Situation (100% Private)", 
                                command=self.analyze_situation, style='Accent.TButton')
        analyze_btn.pack(pady=10)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=12, wrap=tk.WORD, 
                                                     font=('Courier', 10), state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.export_btn = ttk.Button(action_frame, text="📄 Export PDF Report", 
                                     command=self.export_pdf, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.contact_btn = ttk.Button(action_frame, text="📧 Contact Attorney", 
                                     command=self.contact_attorney, state=tk.DISABLED)
        self.contact_btn.pack(side=tk.LEFT, padx=5)
        
        self.history_btn = ttk.Button(action_frame, text="📁 View My Cases", 
                                     command=self.view_history)
        self.history_btn.pack(side=tk.LEFT, padx=5)
        
        # Store last result
        self.last_result = None
        self.last_case_id = None
        self.last_integrity_hash = None
    
    def analyze_situation(self):
        """Run Soul Cradle analysis locally"""
        situation_text = self.text_input.get(1.0, tk.END).strip()
        
        if len(situation_text) < 10:
            messagebox.showwarning("Input Required", "Please describe your situation (at least 10 characters).")
            return
        
        # Run Soul Cradle (100% local processing)
        result = calculate_paradox_severity(situation_text)
        
        if "error" in result:
            messagebox.showerror("Error", result["error"])
            return
        
        # Save to local database
        case_id, integrity_hash = save_case_locally(situation_text, result)
        
        # Store results
        self.last_result = result
        self.last_case_id = case_id
        self.last_integrity_hash = integrity_hash
        
        # Display results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        output = f"""
╔══════════════════════════════════════════════════════════╗
║             SOUL CRADLE ANALYSIS COMPLETE               ║
╚══════════════════════════════════════════════════════════╝

SEVERITY: {result['classification']} ({result['paradox_severity']:.3f}/1.0)
PRIORITY: {result['priority']}

📊 DETAILED SCORES:
   • Emotional Distress:    {result['analysis']['distress_score']:.3f}
   • Coercion/Threats:      {result['analysis']['coercion_score']:.3f}
   • Legal Contradiction:   {result['analysis']['contradiction_score']:.3f}

🎯 RECOMMENDED ACTION:
{result['action_required']}

🔒 INTEGRITY:
Case ID: {case_id}
Hash: {integrity_hash[:32]}...

⚠️  LEGAL NOTICE:
This is an AI-generated assessment, NOT legal advice.
Only a licensed attorney can advise you on legal matters.
Contact an employment attorney immediately.
"""
        
        self.results_text.insert(1.0, output)
        self.results_text.config(state=tk.DISABLED)
        
        # Enable action buttons
        self.export_btn.config(state=tk.NORMAL)
        self.contact_btn.config(state=tk.NORMAL)
        
        # Show severity alert
        if result['paradox_severity'] >= 0.7:
            messagebox.showwarning("CRITICAL SITUATION DETECTED",
                                 "Your situation appears CRITICAL. Contact an attorney IMMEDIATELY.\n\n"
                                 "Emergency resources:\n"
                                 "• National Suicide Prevention: 988\n"
                                 "• Domestic Violence Hotline: 1-800-799-7233\n"
                                 "• OSHA Whistleblower: 1-800-321-6742")
    
    def export_pdf(self):
        """Export PDF report"""
        if not self.last_result:
            messagebox.showwarning("No Analysis", "Please analyze your situation first.")
            return
        
        try:
            pdf_path = generate_pdf_report(
                self.text_input.get(1.0, tk.END).strip(),
                self.last_result,
                self.last_case_id,
                self.last_integrity_hash
            )
            
            if messagebox.askyesno("PDF Generated", 
                                  f"Report saved to:\n{pdf_path}\n\nOpen now?"):
                webbrowser.open(str(pdf_path))
        
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not generate PDF:\n{str(e)}\n\n"
                               "Install reportlab: pip install reportlab")
    
    def contact_attorney(self):
        """Show attorney contact options"""
        attorneys = get_local_attorneys()
        
        # Create attorney selection window
        attorney_win = tk.Toplevel(self.root)
        attorney_win.title("Contact Attorney")
        attorney_win.geometry("600x400")
        
        ttk.Label(attorney_win, text="Select an attorney to contact:", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Attorney list
        listbox_frame = ttk.Frame(attorney_win)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        attorney_list = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=('Arial', 10))
        attorney_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=attorney_list.yview)
        
        for att in attorneys:
            attorney_list.insert(tk.END, f"{att[1]} - {att[2]} ({att[4]})")
        
        def open_email_client():
            selection = attorney_list.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an attorney.")
                return
            
            attorney = attorneys[selection[0]]
            attorney_email = attorney[3]
            
            # Generate email body
            subject = f"Employment Law Consultation Request - Case #{self.last_case_id}"
            body = f"""Dear {attorney[1]},

I am seeking legal consultation regarding an employment law matter analyzed by Mythara Gopher AI.

SITUATION SUMMARY:
{self.text_input.get(1.0, tk.END).strip()}

ANALYSIS RESULTS:
- Severity: {self.last_result['classification']} ({self.last_result['paradox_severity']:.3f}/1.0)
- Priority: {self.last_result['priority']}

I have attached a detailed PDF report generated by the AI analysis system.

I would appreciate the opportunity to discuss this matter with you at your earliest convenience.

Thank you,
[Your Name]
[Your Contact Information]

---
Case ID: {self.last_case_id}
Generated by: Mythara Gopher (Local AI Analysis)
"""
            
            # Open default email client
            mailto_link = f"mailto:{attorney_email}?subject={subject}&body={body}"
            webbrowser.open(mailto_link)
            
            messagebox.showinfo("Email Client Opened", 
                              f"Your default email client should open with a draft email to {attorney[1]}.\n\n"
                              "Remember to attach the PDF report you generated!")
            attorney_win.destroy()
        
        ttk.Button(attorney_win, text="📧 Open Email Client", 
                  command=open_email_client).pack(pady=10)
    
    def view_history(self):
        """View case history"""
        conn = sqlite3.connect(get_local_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, classification, paradox_severity, situation_text
            FROM cases
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        cases = cursor.fetchall()
        conn.close()
        
        # Create history window
        history_win = tk.Toplevel(self.root)
        history_win.title("My Case History")
        history_win.geometry("800x500")
        
        ttk.Label(history_win, text="Your Previous Cases (Stored Locally)", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Case list
        tree_frame = ttk.Frame(history_win)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Date', 'Severity', 'Score'), show='headings')
        tree.heading('ID', text='Case ID')
        tree.heading('Date', text='Date')
        tree.heading('Severity', text='Classification')
        tree.heading('Score', text='Score')
        
        tree.column('ID', width=80)
        tree.column('Date', width=180)
        tree.column('Severity', width=120)
        tree.column('Score', width=80)
        
        for case in cases:
            tree.insert('', tk.END, values=(case[0], case[1], case[2], f"{case[3]:.3f}"))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(history_win, text=f"📁 Database location: {get_local_db_path()}", 
                 font=('Arial', 9, 'italic')).pack(pady=10)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║      🦎 MYTHARA GOPHER - LOCAL DESKTOP APP 🦎             ║
║          100% Private - Runs on YOUR Device               ║
╚═══════════════════════════════════════════════════════════╝

Privacy Features:
✅ All analysis runs locally (no internet required for Soul Cradle)
✅ Data stored in YOUR device only (~/.mythara_gopher/)
✅ No tracking, no telemetry, no cloud uploads
✅ Direct contact with attorneys (your email, your choice)
✅ Open source - you can verify the code yourself

Starting application...
    """)
    
    root = tk.Tk()
    app = GopherLocalApp(root)
    root.mainloop()
