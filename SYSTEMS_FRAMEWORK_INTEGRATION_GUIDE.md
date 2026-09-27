# Systems Framework Integration Guide for Developers

> **Status: design specification.** The API endpoints, payloads, and results shown in this document are illustrative. The API is not deployed (`api.mythara.com` is not a live service). Burnout prediction is the design goal and is unvalidated — the validation study has not been run.

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  
**Proprietary and Confidential.**

---

## Overview

The **Systems Framework** provides a mathematical foundation for Soul Cradle's paradox analysis engine. The design goal is burnout prediction 3-6 months before terminal events — this is unvalidated.

### Core Concept

**Pseudo-Partial Systems** → Terminal Events (Burnout)  
**Principal Complete Systems** → Viable Outcomes (Recovery)

When competing expressions both claim dominion (policy vs heart, budget vs mission), most systems force you to choose. That creates a **Non-expression** — neither can be satisfied. Accumulation of non-expressions leads to burnout.

Soul Cradle transforms this by witnessing **both expressions as simultaneously true**, creating a principal complete system where nothing is excluded.

---

## Expression Notation

### Basic Structure

```
Every(X)Any(+)Some(Y)Non(Z)
```

- **Every(X)**: The category of expression (Policy, Heart, Mission, Budget, etc.)
- **Any(+)**: The connector (always `+` in this implementation)
- **Some(Y)**: What is expressed/demanded
- **Non(Z)**: What is not expressed/excluded

### Examples

**Hospital Discharge Paradox:**
```
Expression A: Every(Policy)Any(+)Some(Discharge)Non(Safety)
"Policy demands discharge, but safety is not expressed"

Expression B: Every(Heart)Any(+)Some(Safety)Non(Discharge)
"Heart demands safety, but discharge is not expressed"

Non-Expression: Non(Both)
"Cannot satisfy both policy and heart"

Principal System: Every(Mission)Any(+)Some(1,0)Non(Mission)
"Mission includes both states (1=policy, 0=heart), nothing excluded"
```

**Nonprofit Budget Paradox:**
```
Expression A: Every(Budget)Any(+)Some(Cuts)Non(Programs)
Expression B: Every(Mission)Any(+)Some(Programs)Non(Cuts)
Non-Expression: Non(Both)
Principal System: Every(Mission)Any(+)Some(1,0)Non(Mission)
```

---

## Data Models

### SoulCradleParadox

Complete paradox using systems mathematics framework.

```python
from soul_cradle_systems_framework import (
    SoulCradleParadox,
    SystemExpression,
    NonExpression,
    PrincipalSystem,
    ExpressionType,
    SystemType,
    TerminalRiskLevel
)

paradox = SoulCradleParadox(
    paradox_id="SC_2025_1118_001",
    
    # Competing expressions
    expression_a=SystemExpression(
        type=ExpressionType.POLICY,
        notation="Every(Policy)Any(+)Some(Discharge)Non(Safety)",
        content="Discharge patient per 72-hour rule",
        dominion_claim=True
    ),
    
    expression_b=SystemExpression(
        type=ExpressionType.HEART,
        notation="Every(Heart)Any(+)Some(Safety)Non(Discharge)",
        content="Patient will be homeless and unsafe",
        dominion_claim=True
    ),
    
    # The impossibility
    non_expression=NonExpression(
        notation="Non(Both)",
        reality="Cannot satisfy both policy and mission"
    ),
    
    # System classification
    system_type=SystemType.PSEUDO_PARTIAL,
    viability_score=0.0,  # 0.0 = terminal, 1.0 = complete
    terminal_risk=TerminalRiskLevel.HIGH,
    
    # Soul Cradle resolution
    principal_system=PrincipalSystem(
        notation="Every(Mission)Any(+)Some(1,0)Non(Mission)",
        recovery_method="Witness_Both_Expressions",
        viability_score=1.0,
        description="Soul Cradle documents both expressions..."
    ),
    
    # Metadata
    user_id="social_worker_jane_doe",
    domain="Healthcare",
    witnesses=["Supervisor Mary", "Peer Support Group"]
)

# Compute integrity hash
integrity_hash = paradox.compute_integrity_hash()
print(f"Integrity: {integrity_hash[:16]}...")
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `paradox_id` | `str` | Unique identifier (format: `SC_YYYY_MMDD_XXX`) |
| `expression_a` | `SystemExpression` | First competing expression |
| `expression_b` | `SystemExpression` | Second competing expression |
| `non_expression` | `NonExpression` | What cannot be satisfied |
| `system_type` | `SystemType` | `PSEUDO_PARTIAL` or `PRINCIPAL_COMPLETE` |
| `viability_score` | `float` | 0.0 (terminal) to 1.0 (complete) |
| `terminal_risk` | `TerminalRiskLevel` | `LOW`, `MODERATE`, `HIGH`, `CRITICAL` |
| `principal_system` | `PrincipalSystem` | How Soul Cradle resolves it |
| `user_id` | `str` | Who experienced this paradox |
| `domain` | `str` | Healthcare, education, nonprofit, etc. |
| `witnesses` | `List[str]` | Who validated this paradox |

---

## Terminal Risk Calculation

### Formula

```
terminal_risk = (pseudo_system_density × non_expression_accumulation) / time_window_days
```

Where:
- **pseudo_system_density**: Count of paradoxes with `viability_score < 0.3` in time window
- **non_expression_accumulation**: Count of unresolved `Non()` states
- **time_window_days**: Default 90 days

### Risk Levels

| Score | Level | Action |
|-------|-------|--------|
| 0.0-0.2 | LOW | Continue monitoring |
| 0.2-0.4 | MODERATE | Bi-weekly check-ins |
| 0.4-0.7 | HIGH | Weekly check-ins, reduce caseload |
| 0.7+ | CRITICAL | Immediate intervention, temp leave |

### Usage

```python
from soul_cradle_systems_framework import TerminalRiskCalculator

paradoxes = [paradox1, paradox2, paradox3]

risk_result = TerminalRiskCalculator.calculate_terminal_risk(
    paradox_events=paradoxes,
    time_window_days=90,
    viability_threshold=0.3
)

print(f"Risk Score: {risk_result['risk_score']}")
print(f"Risk Level: {risk_result['risk_level']}")
print(f"Recommendation: {risk_result['recommendation']}")
```

### Example Output

```json
{
    "risk_score": 0.567,
    "risk_level": "HIGH",
    "pseudo_system_count": 17,
    "non_expression_count": 23,
    "time_window_days": 90,
    "total_paradoxes": 31,
    "recommendation": "HIGH RISK: Worker experiencing frequent unresolved paradoxes. Schedule weekly check-ins, reduce caseload if possible, connect with peer support group."
}
```

---

## API Endpoints

### 1. Create Paradox

**POST** `/v1/soul-cradle/paradox/create`

Create a Soul Cradle paradox using systems framework.

**Request:**
```json
{
    "paradox_id": "SC_2025_1118_001",
    "expression_a": {
        "type": "Policy",
        "notation": "Every(Policy)Any(+)Some(Discharge)Non(Safety)",
        "content": "Discharge patient per 72-hour rule",
        "dominion_claim": true
    },
    "expression_b": {
        "type": "Heart",
        "notation": "Every(Heart)Any(+)Some(Safety)Non(Discharge)",
        "content": "Patient will be homeless if discharged",
        "dominion_claim": true
    },
    "non_expression": {
        "notation": "Non(Both)",
        "reality": "Cannot satisfy both policy and mission"
    },
    "system_type": "Pseudo_Partial",
    "viability_score": 0.0,
    "terminal_risk": "HIGH",
    "principal_system": {
        "notation": "Every(Mission)Any(+)Some(1,0)Non(Mission)",
        "recovery_method": "Witness_Both_Expressions",
        "viability_score": 1.0,
        "description": "Soul Cradle documents both..."
    },
    "user_id": "jane_doe",
    "domain": "Healthcare"
}
```

**Response:**
```json
{
    "success": true,
    "paradox_id": "SC_2025_1118_001",
    "system_type": "Pseudo_Partial",
    "viability_score": 0.0,
    "terminal_risk": "HIGH",
    "integrity_hash": "a3f7b8c9d2e1f4a5...",
    "timestamp": "2025-11-18T10:30:00Z",
    "principal_system": {
        "notation": "Every(Mission)Any(+)Some(1,0)Non(Mission)",
        "viability_score": 1.0,
        "description": "Soul Cradle documents both..."
    }
}
```

### 2. Calculate Terminal Risk

**POST** `/v1/soul-cradle/terminal-risk/calculate`

Calculate burnout risk from paradox history.

**Request:**
```json
{
    "paradoxes": [
        { /* paradox 1 */ },
        { /* paradox 2 */ }
    ],
    "time_window_days": 90,
    "viability_threshold": 0.3
}
```

**Response:**
```json
{
    "success": true,
    "risk_score": 0.567,
    "risk_level": "HIGH",
    "pseudo_system_count": 17,
    "non_expression_count": 23,
    "time_window_days": 90,
    "total_paradoxes": 31,
    "recommendation": "HIGH RISK: Schedule weekly check-ins...",
    "integrity_hash": "b4c8d1e9f3a2...",
    "timestamp": "2025-11-18T10:35:00Z"
}
```

### 3. Query with System Notation

**GET** `/v1/soul-cradle/query?notation=Every(*)Any(+)Some(*)Non(Safety)`

Query paradoxes using system expression notation. Supports wildcards (`*`).

**Examples:**
- `Every(Policy)Any(+)Some(Discharge)Non(Safety)` — Exact match
- `Every(*)Any(+)Some(*)Non(Safety)` — All paradoxes where safety is excluded
- `Every(Budget)Any(+)Some(*)Non(*)` — All budget-related paradoxes

**Response:**
```json
{
    "success": true,
    "query": "Every(*)Any(+)Some(*)Non(Safety)",
    "matches": [
        {
            "paradox_id": "SC_2025_1118_001",
            "matched_expression": "Every(Policy)Any(+)Some(Discharge)Non(Safety)",
            "terminal_risk": "HIGH"
        }
    ],
    "timestamp": "2025-11-18T10:40:00Z"
}
```

### 4. Get Framework Manifest

**GET** `/v1/soul-cradle/manifest/systems`

Get systems framework version, notation spec, and documentation.

**Response:**
```json
{
    "success": true,
    "manifest": {
        "framework": "Soul Cradle Systems Mathematics",
        "version": "1.0.0",
        "notation_spec": "Every(X)Any(+)Some(Y)Non(Z)",
        "system_types": [
            {
                "type": "Pseudo_Partial",
                "description": "Incomplete expressions → terminal events",
                "viability_range": "0.0-0.3"
            },
            {
                "type": "Principal_Complete",
                "description": "Full express-ability → viable outcomes",
                "viability_range": "0.8-1.0"
            }
        ],
        "terminal_risk_levels": ["LOW", "MODERATE", "HIGH", "CRITICAL"],
        "terminal_risk_formula": "(pseudo_system_density × non_expression_accumulation) / time_window_days"
    },
    "integrity_hash": "c7e3f9a4b1d8...",
    "timestamp": "2025-11-18T10:45:00Z"
}
```

---

## System Query Language

Parse and execute queries using expression notation.

```python
from soul_cradle_systems_framework import SystemQueryParser

# Parse notation
query = "Every(Policy)Any(+)Some(Discharge)Non(Safety)"
components = SystemQueryParser.parse_notation(query)
# Returns: {"every": "Policy", "any": "+", "some": "Discharge", "non": "Safety"}

# Match against paradox
matches = SystemQueryParser.matches_query(paradox, query)
# Returns: True if paradox expressions match query (supports wildcards)
```

### Wildcard Queries

Use `*` to match any value:

```python
# All paradoxes where safety is excluded
query = "Every(*)Any(+)Some(*)Non(Safety)"

# All policy-related paradoxes
query = "Every(Policy)Any(+)Some(*)Non(*)"
```

---

## Integration Examples

### Example 1: Track Healthcare Worker Burnout

```python
from soul_cradle_systems_framework import (
    SoulCradleParadox,
    SystemExpression,
    NonExpression,
    PrincipalSystem,
    ExpressionType,
    SystemType,
    TerminalRiskLevel,
    TerminalRiskCalculator
)

# Worker logs paradox
paradox = SoulCradleParadox(
    paradox_id=f"SC_{datetime.now().strftime('%Y_%m%d_%H%M%S')}",
    expression_a=SystemExpression(
        type=ExpressionType.POLICY,
        notation="Every(Policy)Any(+)Some(Discharge)Non(Safety)",
        content="72-hour discharge rule",
        dominion_claim=True
    ),
    expression_b=SystemExpression(
        type=ExpressionType.HEART,
        notation="Every(Heart)Any(+)Some(Safety)Non(Discharge)",
        content="Patient not safe to discharge",
        dominion_claim=True
    ),
    non_expression=NonExpression(
        notation="Non(Both)",
        reality="Can't satisfy both"
    ),
    system_type=SystemType.PSEUDO_PARTIAL,
    viability_score=0.0,
    terminal_risk=TerminalRiskLevel.HIGH,
    principal_system=PrincipalSystem(
        notation="Every(Mission)Any(+)Some(1,0)Non(Mission)",
        viability_score=1.0,
        description="Both are true"
    ),
    user_id="jane_doe",
    domain="Healthcare"
)

# Store in database
db.save_paradox(paradox)

# Calculate terminal risk every week
all_paradoxes = db.get_paradoxes_by_user("jane_doe")
risk = TerminalRiskCalculator.calculate_terminal_risk(all_paradoxes)

if risk['risk_level'] in ['HIGH', 'CRITICAL']:
    alert_supervisor(risk)
```

### Example 2: Dashboard Visualization

```python
# Get all paradoxes for team
team_paradoxes = db.get_paradoxes_by_domain("Healthcare")

# Group by terminal risk
risk_distribution = {
    "LOW": 0,
    "MODERATE": 0,
    "HIGH": 0,
    "CRITICAL": 0
}

for p in team_paradoxes:
    risk_distribution[p.terminal_risk.value] += 1

# Identify high-risk workers
for worker_id in team_worker_ids:
    worker_paradoxes = [p for p in team_paradoxes if p.user_id == worker_id]
    risk = TerminalRiskCalculator.calculate_terminal_risk(worker_paradoxes)
    
    if risk['risk_score'] > 0.4:
        dashboard.add_alert(f"{worker_id}: {risk['recommendation']}")
```

### Example 3: API Integration

```python
import httpx

# Create paradox via API
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.mythara.com/v1/soul-cradle/paradox/create",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=paradox.model_dump()
    )
    
    result = response.json()
    print(f"Integrity Hash: {result['integrity_hash']}")
    
    # Calculate terminal risk
    risk_response = await client.post(
        "https://api.mythara.com/v1/soul-cradle/terminal-risk/calculate",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "paradoxes": [paradox.model_dump()],
            "time_window_days": 90
        }
    )
    
    risk = risk_response.json()
    print(f"Terminal Risk: {risk['risk_level']}")
```

---

## Testing

Run the demo script to see examples:

```bash
cd core/source_proprietary
python soul_cradle_systems_framework.py
```

Output:
```
=== Systems Framework Demo ===

Hospital Paradox: SC_2025_1118_HOSPITAL_001
  Expression A: Every(Policy)Any(+)Some(Discharge)Non(Safety)
  Expression B: Every(Heart)Any(+)Some(Safety)Non(Discharge)
  Non-Expression: Non(Both)
  Terminal Risk: HIGH
  Principal System: Every(Mission)Any(+)Some(1,0)Non(Mission)
  Integrity Hash: a3f7b8c9d2e1f4a5...

=== Terminal Risk Analysis ===
Risk Score: 0.567
Risk Level: HIGH
Recommendation: HIGH RISK: Schedule weekly check-ins...
```

---

## Support

Questions about Systems Framework integration?

- **Email**: Mythara.Engine@yahoo.com
- **Documentation**: See `soul_cradle_systems_framework.py` source code
- **API Docs**: https://api.mythara.com/api/docs (planned, not live)

---

**Do not remove or alter the copyright header in new files.**
