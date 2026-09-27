# DrMythara Medical Team Suite - Quick Reference

> **Status: technical documentation for an experimental module.** This is not a medical device, is not clinically validated, and has not been audited for HIPAA or any other compliance framework. The disclaimers at the bottom of this page are part of the contract — this system supports administrative workflows; it does not diagnose, treat, or advise.

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

---

## ⚡ Quick Start Commands

### Run Full Suite
```powershell
python run_medical_team_suite.py
```

### Run Compliance Bot Only
```powershell
python run_drmythara_bot.py
```

### Schedule Automated Tasks (Admin Required)
```powershell
# Run as Administrator
.\schedule_medical_team_bots.ps1
```

---

## 🤖 10 Medical Team Bots

### Essential Bots (Critical Clinical Functions)

| Bot | Purpose | Key Features |
|-----|---------|--------------|
| 🚑 **Triage Coordinator** | Patient prioritization | Urgency assessment, provider assignment, wait time tracking |
| 📋 **Clinical Documentation** | Medical record support | SOAP notes, documentation completeness, unsigned note tracking |
| ⚖️ **Compliance Monitor** | HIPAA/FDA monitoring | PHI protection, access control, audit logs, compliance alerts |
| 🚨 **Crisis Response** | Emergency protocols | Code Blue/Red/Grey/Pink activation, team coordination |

### Non-Essential Bots (Support Roles)

| Bot | Purpose | Key Features |
|-----|---------|--------------|
| 📚 **Patient Education** | Health literacy | Condition education, materials distribution, comprehension tracking |
| 📅 **Scheduling Coordinator** | Appointment management | Calendar management, reminders, rescheduling |
| 🏗️ **Resource Allocation** | Equipment/staffing | Resource tracking, optimization, shortage alerts |
| 📑 **Administrative Assistant** | Paperwork/billing | Insurance verification, billing codes, prior authorizations |
| 📊 **Quality Assurance** | Process improvement | Quality metrics, bottleneck identification, satisfaction monitoring |
| 🎓 **Continuing Education** | Staff training | Certification tracking, expiring credentials, compliance training |

---

## 📊 Common Operations

### Create Triage Case
```python
from Commercial.mythara_medical_team_suite import MedicalTeamSuite

suite = MedicalTeamSuite()

triage_case = suite.triage_bot.assess_triage(
    patient_id="PT001",
    chief_complaint="Chest pain, shortness of breath",
    vital_signs={
        "heart_rate": 110,
        "blood_pressure_systolic": 145,
        "blood_pressure_diastolic": 95,
        "temperature_f": 98.6,
        "respiratory_rate": 22,
        "oxygen_saturation": 94
    }
)

print(f"Case ID: {triage_case.case_id}")
print(f"Urgency: {triage_case.urgency_level.value}")
```

### Schedule Appointment
```python
from datetime import datetime, timedelta

appointment = suite.scheduling_bot.schedule_appointment(
    patient_id="PT001",
    provider_id="DR_SMITH",
    appointment_type="follow_up",
    scheduled_time=(datetime.utcnow() + timedelta(days=7)).isoformat(),
    duration_minutes=30
)
```

### Create Compliance Alert
```python
alert = suite.compliance_bot.create_alert(
    alert_type="HIPAA",
    severity="high",
    description="Unauthorized access attempt detected",
    affected_systems=["EMR_SYSTEM", "RADIOLOGY_PACS"]
)
```

### Activate Crisis Protocol
```python
response = suite.crisis_bot.activate_crisis_protocol(
    protocol_code="code_blue",
    location="ER Room 3",
    details="Patient unresponsive, no pulse"
)
```

### Generate Clinical Note Template
```python
note = suite.clinical_doc_bot.create_note_template(
    note_type="SOAP",
    patient_id="PT001",
    encounter_id="ENC_12345",
    provider_id="DR_JONES"
)
```

---

## 🔐 Urgency Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| **EMERGENCY** | Life-threatening | Immediate |
| **URGENT** | Serious condition | < 15 minutes |
| **SEMI_URGENT** | Moderate condition | < 2 hours |
| **NON_URGENT** | Stable condition | < 24 hours |
| **ROUTINE** | Scheduled care | As scheduled |

---

## 🚨 Crisis Protocols

| Code | Description | Response Team |
|------|-------------|---------------|
| **Code Blue** | Cardiac/respiratory arrest | Physician, Nurse, RT, Pharmacist |
| **Code Red** | Fire emergency | Security, Facilities, Nursing |
| **Code Grey** | Combative person | Security, Behavioral Health, Nursing |
| **Code Pink** | Infant/child abduction | Security, Nursing, Administration |

---

## 📋 Status Checking

### Get Suite Health Report
```python
report = suite.generate_suite_report()

print(f"Active triage cases: {report['overall_health']['active_triage_cases']}")
print(f"Compliance alerts: {report['overall_health']['unresolved_compliance_alerts']}")
print(f"Today's appointments: {report['overall_health']['todays_scheduled_appointments']}")
```

### Check Individual Bot Status
```python
# Triage bot
status = suite.triage_bot.get_status()
print(f"Active cases by urgency: {status['active_cases_by_urgency']}")

# Compliance bot
status = suite.compliance_bot.get_status()
print(f"Alerts by severity: {status['active_alerts_by_severity']}")

# Scheduling bot
status = suite.scheduling_bot.get_status()
print(f"Today's appointments: {status['todays_appointments']}")
```

---

## 🗄️ Database Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `triage_cases` | Patient triage | patient_id, urgency_level, vital_signs |
| `clinical_notes` | Medical documentation | note_type, provider_id, signed |
| `compliance_alerts` | HIPAA/FDA alerts | severity, resolved, remediation_required |
| `education_sessions` | Patient education | topic, comprehension_level |
| `appointments` | Scheduling | scheduled_time, status |
| `resource_allocations` | Equipment/staff | resource_type, allocated_to |
| `quality_metrics` | QA measurements | metric_name, metric_value |
| `staff_training` | Certifications | course_name, certification_expires |

---

## 🔧 Task Scheduler Management

### View All DrMythara Tasks
```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like 'DrMythara*'}
```

### Run Task Manually
```powershell
Start-ScheduledTask -TaskName 'DrMythara_MedicalTeamSuite_Hourly'
```

### Disable Task
```powershell
Disable-ScheduledTask -TaskName 'DrMythara_ComplianceMonitor_15Min'
```

### Enable Task
```powershell
Enable-ScheduledTask -TaskName 'DrMythara_ComplianceMonitor_15Min'
```

### Remove All Tasks
```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like 'DrMythara*'} | Unregister-ScheduledTask -Confirm:$false
```

---

## ⚠️ Critical Disclaimers

### What This System IS:
- ✅ Administrative workflow support
- ✅ Compliance monitoring
- ✅ Documentation assistance
- ✅ Resource coordination
- ✅ Quality tracking

### What This System IS NOT:
- ❌ Medical advice provider
- ❌ Diagnostic tool
- ❌ Treatment decision-maker
- ❌ Medical device
- ❌ Substitute for licensed professionals
- ❌ Emergency services (call 911)

---

## 📊 Report Files

### Generated Reports
```
medical_team_report_YYYYMMDD_HHMMSS.json
```

### Report Contents
- Suite ID and timestamp
- All 10 bot statuses
- Essential bot metrics (triage, compliance, documentation, crisis)
- Support bot metrics (scheduling, education, QA, etc.)
- Overall suite health
- SHA-256 integrity hash

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `Commercial/mythara_medical_team_suite.py` | Main bot implementation |
| `run_medical_team_suite.py` | Suite runner script |
| `run_drmythara_bot.py` | Compliance bot runner |
| `schedule_medical_team_bots.ps1` | Task scheduler setup |
| `Legal/Compliance/US/Mental_Health_Clinical_Integration.md` | Mental health clinical design notes |
| *(doc not present in repo)* | Full medical team suite documentation — not written |

---

## 🆘 Troubleshooting

### Database Locked Error
```python
# Close any open connections
import sqlite3
conn = sqlite3.connect("mythara_medical_team.db")
conn.close()
```

### Bot Not Initializing
```python
# Check logs
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Missing Dependencies
```powershell
pip install -r requirements.txt
```

### Task Scheduler Permissions
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → Run as Administrator
```

---

## 📞 Support

For issues or questions:
- Email: mytharalabs@yahoo.com
- Related files: see the table above (a standalone full-documentation file is not present in the repo)
- Repository: Mythara_Archive

---

**Built with Mythara SSIP Framework**  
*Integrity-First Healthcare Bot Orchestration*
