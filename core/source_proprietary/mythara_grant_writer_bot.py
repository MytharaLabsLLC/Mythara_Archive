# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
Mythara Grant Writing Specialist Bot
Continuously searches for grants, analyzes winning examples, and writes applications
Focus: Infrastructure grants for dedicated servers and operations scaling
"""

import sqlite3
import hashlib
import json
import requests
from datetime import datetime
from typing import List

# Public Grants.gov opportunity-search API (no API key required).
# NOTE: post directly to apply07.grants.gov. Posting to www.grants.gov gets a
# 301/302 redirect to this host, and requests follows it by converting the
# POST into a GET, which the API rejects with 405.
GRANTS_GOV_SEARCH_URL = "https://apply07.grants.gov/grantsws/rest/opportunities/search/"
# Short on purpose: (connect seconds, read seconds). Any failure -> sample fallback.
GRANTS_GOV_TIMEOUT = (5, 10)
# Label stamped on EVERY fallback output and in the search_grants docstring.
SAMPLE_DATA_NOTICE = "SAMPLE DATA — offline fallback, not live results."


class MytharaGrantWriterBot:
    def __init__(self, db_path: str = "mythara_grants.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.orchestrator_url = "http://localhost:5000"
        self._init_database()
        self._register_with_orchestrator()

    def _init_database(self):
        """Initialize database schema"""
        c = self.conn.cursor()

        # Grant opportunities database
        c.execute("""
            CREATE TABLE IF NOT EXISTS grant_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grant_name TEXT NOT NULL,
                grantor TEXT NOT NULL,
                grant_type TEXT CHECK(grant_type IN ('federal', 'state', 'private', 'corporate', 'foundation', 'sbir', 'sttr')),
                focus_area TEXT,
                award_amount TEXT,
                deadline DATE,
                eligibility TEXT,
                url TEXT,
                status TEXT CHECK(status IN ('discovered', 'analyzing', 'writing', 'submitted', 'awarded', 'rejected', 'not_pursuing')),
                fit_score INTEGER CHECK(fit_score >= 0 AND fit_score <= 100),
                discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                integrity_hash TEXT NOT NULL
            )
        """)

        # Winning grant examples database
        c.execute("""
            CREATE TABLE IF NOT EXISTS winning_grants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grant_name TEXT NOT NULL,
                recipient TEXT,
                award_amount TEXT,
                year INTEGER,
                grantor TEXT,
                industry TEXT,
                project_description TEXT,
                success_factors TEXT,
                narrative_excerpt TEXT,
                budget_excerpt TEXT,
                source_url TEXT,
                analysis_notes TEXT,
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Grant applications database
        c.execute("""
            CREATE TABLE IF NOT EXISTS grant_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grant_opportunity_id INTEGER NOT NULL,
                application_title TEXT NOT NULL,
                narrative TEXT,
                budget TEXT,
                project_summary TEXT,
                objectives TEXT,
                methodology TEXT,
                impact_statement TEXT,
                sustainability_plan TEXT,
                version INTEGER DEFAULT 1,
                status TEXT CHECK(status IN ('draft', 'review', 'final', 'submitted')),
                submission_date TIMESTAMP,
                result TEXT CHECK(result IN ('pending', 'awarded', 'rejected', 'withdrawn')),
                award_amount TEXT,
                feedback TEXT,
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (grant_opportunity_id) REFERENCES grant_opportunities(id)
            )
        """)

        # Grant search queries
        c.execute("""
            CREATE TABLE IF NOT EXISTS grant_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_query TEXT NOT NULL,
                search_source TEXT CHECK(search_source IN ('grants.gov', 'foundation_center', 'sbir.gov', 'corporate', 'manual')),
                results_found INTEGER DEFAULT 0,
                new_opportunities INTEGER DEFAULT 0,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                integrity_hash TEXT NOT NULL
            )
        """)

        # Infrastructure needs database
        c.execute("""
            CREATE TABLE IF NOT EXISTS infrastructure_needs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                need_category TEXT CHECK(need_category IN ('servers', 'networking', 'storage', 'security', 'software', 'personnel', 'facility')),
                description TEXT NOT NULL,
                estimated_cost REAL,
                priority TEXT CHECK(priority IN ('critical', 'high', 'medium', 'low')),
                justification TEXT,
                grant_alignment TEXT,
                status TEXT CHECK(status IN ('needed', 'funded', 'in_progress', 'completed')),
                integrity_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Audit trail
        c.execute("""
            CREATE TABLE IF NOT EXISTS grant_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                integrity_hash TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        self._populate_initial_infrastructure_needs()

    def _populate_initial_infrastructure_needs(self):
        """Populate infrastructure needs for Mythara"""
        c = self.conn.cursor()

        # Check if already populated
        c.execute("SELECT COUNT(*) FROM infrastructure_needs")
        if c.fetchone()[0] > 0:
            return

        # Define Mythara infrastructure requirements
        needs = [
            {
                "category": "servers",
                "description": "Dedicated GPU servers for AI/ML orchestration (4x NVIDIA A100 GPUs)",
                "cost": 50000,
                "priority": "critical",
                "justification": "Enable real-time SSIP verification at scale, support 1000+ concurrent contract validations",
                "grant_alignment": "SBIR Phase II, NSF SBIR, AWS Cloud Credits",
            },
            {
                "category": "servers",
                "description": "Production application servers (8-core, 32GB RAM, redundant pair)",
                "cost": 15000,
                "priority": "critical",
                "justification": "Host Mythara API, orchestrator, and VP bot fleet for 99.9% uptime SLA",
                "grant_alignment": "Small Business Innovation grants, State tech grants",
            },
            {
                "category": "servers",
                "description": "Database servers with high-IOPS storage (PostgreSQL cluster)",
                "cost": 20000,
                "priority": "critical",
                "justification": "Store contract integrity hashes, audit trails, and customer data with storage built to HIPAA/SOC 2 control standards (not currently certified)",
                "grant_alignment": "Cybersecurity grants, Healthcare IT grants",
            },
            {
                "category": "networking",
                "description": "Enterprise firewall and DDoS protection (Cloudflare Enterprise)",
                "cost": 12000,
                "priority": "high",
                "justification": "Protect against attacks, ensure service availability for enterprise customers",
                "grant_alignment": "Cybersecurity Innovation grants, DHS SBIR",
            },
            {
                "category": "networking",
                "description": "Load balancers and CDN infrastructure",
                "cost": 8000,
                "priority": "high",
                "justification": "Distribute traffic globally, reduce latency for international customers",
                "grant_alignment": "Infrastructure modernization grants",
            },
            {
                "category": "storage",
                "description": "Encrypted object storage (S3-compatible, 50TB)",
                "cost": 10000,
                "priority": "high",
                "justification": "Store contract documents, audit logs, backups with AES-256 encryption",
                "grant_alignment": "Data security grants, Compliance infrastructure grants",
            },
            {
                "category": "storage",
                "description": "Backup and disaster recovery infrastructure",
                "cost": 7000,
                "priority": "high",
                "justification": "Ensure business continuity, meet enterprise RTO/RPO requirements (4hr/1hr)",
                "grant_alignment": "Business continuity grants, Resilience grants",
            },
            {
                "category": "security",
                "description": "Security Operations Center (SOC) tooling (SIEM, IDS/IPS)",
                "cost": 25000,
                "priority": "critical",
                "justification": "Monitor for threats, work toward SOC 2 Type II and CMMC Level 3 certification (not currently held)",
                "grant_alignment": "DHS Cybersecurity grants, DOD SBIR (defense contractors)",
            },
            {
                "category": "security",
                "description": "Hardware Security Modules (HSMs) for key management",
                "cost": 30000,
                "priority": "high",
                "justification": "FIPS 140-2 Level 3 compliant key storage for cryptographic operations",
                "grant_alignment": "Federal compliance grants, Financial services security grants",
            },
            {
                "category": "software",
                "description": "Enterprise monitoring and observability (Datadog/New Relic)",
                "cost": 15000,
                "priority": "high",
                "justification": "Real-time performance monitoring, incident response, SLA tracking",
                "grant_alignment": "Operational excellence grants",
            },
            {
                "category": "software",
                "description": "CI/CD pipeline infrastructure (GitHub Enterprise, Jenkins)",
                "cost": 10000,
                "priority": "medium",
                "justification": "Automated testing, deployment, code quality assurance",
                "grant_alignment": "Software development grants, Innovation grants",
            },
            {
                "category": "personnel",
                "description": "DevOps engineer (1 FTE, 1 year)",
                "cost": 120000,
                "priority": "critical",
                "justification": "Manage infrastructure, ensure uptime, handle scaling operations",
                "grant_alignment": "Workforce development grants, SBIR personnel costs",
            },
            {
                "category": "personnel",
                "description": "Security engineer (1 FTE, 1 year)",
                "cost": 130000,
                "priority": "critical",
                "justification": "Work toward SOC 2, CMMC certifications, manage security operations",
                "grant_alignment": "Cybersecurity workforce grants, Defense contractor grants",
            },
            {
                "category": "facility",
                "description": "Colocation facility costs (1 rack, 1 year)",
                "cost": 24000,
                "priority": "high",
                "justification": "Physical security, redundant power, network connectivity for on-prem servers",
                "grant_alignment": "Infrastructure grants, Manufacturing USA facilities",
            },
            {
                "category": "facility",
                "description": "Cloud infrastructure (AWS/Azure hybrid, 1 year)",
                "cost": 60000,
                "priority": "critical",
                "justification": "Global availability, auto-scaling, hybrid cloud architecture",
                "grant_alignment": "AWS Cloud Credits, Azure Credits, Cloud innovation grants",
            },
        ]

        for need in needs:
            data = {
                "need_category": need["category"],
                "description": need["description"],
                "estimated_cost": need["cost"],
                "priority": need["priority"],
                "justification": need["justification"],
                "grant_alignment": need["grant_alignment"],
                "status": "needed",
            }
            integrity_hash = self._calculate_integrity_hash(data)

            c.execute(
                """
                INSERT INTO infrastructure_needs (
                    need_category, description, estimated_cost, priority,
                    justification, grant_alignment, status, integrity_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    need["category"],
                    need["description"],
                    need["cost"],
                    need["priority"],
                    need["justification"],
                    need["grant_alignment"],
                    "needed",
                    integrity_hash,
                ),
            )

        self.conn.commit()
        print(
            f"[OK] Populated {len(needs)} infrastructure needs (Total: ${sum(n['cost'] for n in needs):,.0f})"
        )

    def _calculate_integrity_hash(self, data: dict) -> str:
        """Calculate SHA-256 integrity hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _register_with_orchestrator(self):
        """Register with Mythara Orchestrator"""
        try:
            response = requests.post(
                f"{self.orchestrator_url}/register",
                json={
                    "vp_name": "Grant Writer Bot",
                    "capabilities": [
                        "grant_search",
                        "grant_writing",
                        "winning_analysis",
                        "infrastructure_planning",
                    ],
                    "status": "active",
                },
            )
            if response.status_code == 200:
                print("[OK] Registered with Mythara Orchestrator")
            else:
                print(f"[!] Orchestrator registration failed: {response.status_code}")
        except Exception as e:
            print(f"[!] Could not connect to orchestrator: {e}")

    def _fetch_grants_gov(self, keyword: str, rows: int = 10) -> List[dict]:
        """One live call to the public Grants.gov opportunity-search API.

        POSTs JSON {"keyword": ..., "oppStatuses": "forecasted|posted", ...}
        and maps the documented "oppHits" response shape onto this bot's
        grant-dict format.

        Raises on ANY failure: network error, timeout, HTTP error, bad JSON,
        or an unexpected response shape. Callers catch everything and fall
        back to labeled sample data.
        """
        resp = requests.post(
            GRANTS_GOV_SEARCH_URL,
            json={
                "keyword": keyword,
                "oppStatuses": "forecasted|posted",
                "rows": rows,
                "startRecordNum": 0,
                "sortBy": "openDate|desc",
            },
            timeout=GRANTS_GOV_TIMEOUT,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MytharaGrantWriterBot/1.0",
            },
        )
        resp.raise_for_status()
        payload = resp.json()  # raises on non-JSON bodies
        hits = payload.get("oppHits")
        if not isinstance(hits, list):
            raise ValueError(
                "unexpected grants.gov response shape "
                f"(keys: {list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__})"
            )

        grants: List[dict] = []
        for hit in hits:
            if not isinstance(hit, dict):
                continue
            title = hit.get("title") or "(untitled opportunity)"
            grantor = hit.get("agencyName") or hit.get("agency") or "Unknown agency"
            opp_id = hit.get("id") or ""
            url = (
                f"https://www.grants.gov/search-results-detail/{opp_id}"
                if opp_id
                else "https://www.grants.gov/"
            )
            ceiling = hit.get("awardCeiling")
            grants.append(
                {
                    "name": title,
                    "number": hit.get("number") or "",
                    "grantor": grantor,
                    "type": "federal",  # grants.gov lists federal opportunities only
                    "focus": hit.get("oppCategory") or keyword,
                    "amount": f"${ceiling}" if ceiling else "See announcement",
                    "deadline": hit.get("closeDate") or "",
                    "eligibility": hit.get("eligibleApplicants") or "See announcement",
                    "url": url,
                    "fit_score": self._fit_score(f"{title} {grantor}", [keyword]),
                }
            )
        return grants

    @staticmethod
    def _dedupe_grants(grants: List[dict]) -> List[dict]:
        """Drop duplicate opportunities (same opportunity number + grantor)."""
        seen = set()
        unique: List[dict] = []
        for grant in grants:
            key = (grant.get("number") or grant.get("name"), grant.get("grantor"))
            if key not in seen:
                seen.add(key)
                unique.append(grant)
        return unique

    @staticmethod
    def _fit_score(text: str, keywords: List[str]) -> int:
        """Naive fit heuristic: base 60, +5 per keyword found, capped at 95.

        This is a rough keyword-overlap score, not a real assessment.
        """
        score = 60
        haystack = (text or "").lower()
        for kw in keywords:
            if kw.strip().lower() and kw.strip().lower() in haystack:
                score += 5
        return min(score, 95)

    def search_grants(
        self, keywords: List[str] = None, grant_type: str = None
    ) -> List[dict]:
        """Search for grant opportunities.

        Tries the live public Grants.gov API first (no API key required):
        POST https://apply07.grants.gov/grantsws/rest/opportunities/search/
        with a short timeout (5s connect / 10s read).

        On ANY failure — no network, timeout, HTTP error, bad JSON, or an
        unexpected response shape — it falls back to built-in sample data.
        Every fallback output is labeled:
        "SAMPLE DATA — offline fallback, not live results."
        """
        c = self.conn.cursor()

        if keywords is None:
            keywords = [
                "infrastructure",
                "servers",
                "cloud computing",
                "cybersecurity",
                "small business",
                "technology",
                "innovation",
                "SBIR",
                "STTR",
                "digital transformation",
                "AI",
                "blockchain",
                "data security",
            ]

        # Live first: public Grants.gov API (no key). ANY failure -> labeled sample data.
        live_grants: List[dict] = []
        used_fallback = False
        try:
            for kw in keywords[:2]:  # keep the live attempt bounded (2 short calls max)
                live_grants.extend(self._fetch_grants_gov(kw, rows=10))
            discovered_grants = self._dedupe_grants(live_grants)
            print(
                f"[OK] Live Grants.gov search returned {len(discovered_grants)} opportunities"
            )
        except Exception as e:  # noqa: BLE001 -- ANY failure means offline fallback
            print(f"[!] Live Grants.gov search failed ({type(e).__name__}: {e})")
            print(f"[!] {SAMPLE_DATA_NOTICE}")
            discovered_grants = [
                {
                    "name": "NSF SBIR Phase II - Cybersecurity Infrastructure",
                    "grantor": "National Science Foundation",
                    "type": "sbir",
                    "focus": "Cybersecurity, Infrastructure",
                    "amount": "$750,000",
                    "deadline": "2025-12-15",
                    "eligibility": "Small businesses with Phase I award",
                    "url": "https://www.sbir.gov/opportunities",
                    "fit_score": 95,
                },
                {
                    "name": "AWS Cloud Credits for Startups",
                    "grantor": "Amazon Web Services",
                    "type": "corporate",
                    "focus": "Cloud infrastructure, Startups",
                    "amount": "$100,000 in credits",
                    "deadline": "Rolling",
                    "eligibility": "Venture-backed or accelerator startups",
                    "url": "https://aws.amazon.com/activate/",
                    "fit_score": 92,
                },
                {
                    "name": "DHS SBIR - Critical Infrastructure Protection",
                    "grantor": "Department of Homeland Security",
                    "type": "sbir",
                    "focus": "Infrastructure security, Blockchain",
                    "amount": "$1,000,000",
                    "deadline": "2026-01-31",
                    "eligibility": "US small businesses, security clearance",
                    "url": "https://www.dhs.gov/science-and-technology/sbir",
                    "fit_score": 88,
                },
                {
                    "name": "State Tech Innovation Grant - California",
                    "grantor": "California Office of Economic Development",
                    "type": "state",
                    "focus": "Technology infrastructure, Job creation",
                    "amount": "$250,000",
                    "deadline": "2025-11-30",
                    "eligibility": "California-based tech companies",
                    "url": "https://business.ca.gov/grants/",
                    "fit_score": 85,
                },
                {
                    "name": "Microsoft Azure Credits for Nonprofits/Startups",
                    "grantor": "Microsoft",
                    "type": "corporate",
                    "focus": "Cloud infrastructure, AI/ML",
                    "amount": "$150,000 in credits",
                    "deadline": "Rolling",
                    "eligibility": "Startups, nonprofits, mission-driven",
                    "url": "https://azure.microsoft.com/en-us/pricing/member-offers/credit-for-nonprofits/",
                    "fit_score": 90,
                },
                {
                    "name": "NIST Small Business Innovation Research",
                    "grantor": "National Institute of Standards and Technology",
                    "type": "sbir",
                    "focus": "Cybersecurity, Standards, Compliance",
                    "amount": "$500,000",
                    "deadline": "2026-02-28",
                    "eligibility": "Small businesses, CMMC focus",
                    "url": "https://www.nist.gov/sbir",
                    "fit_score": 87,
                },
                {
                    "name": "DOE SBIR - Energy Infrastructure Resilience",
                    "grantor": "Department of Energy",
                    "type": "sbir",
                    "focus": "Infrastructure resilience, Security",
                    "amount": "$1,200,000",
                    "deadline": "2025-12-01",
                    "eligibility": "Energy sector innovation",
                    "url": "https://www.energy.gov/eere/amo/doe-sbir-sttr-phase-i-release-2",
                    "fit_score": 75,
                },
                {
                    "name": "Siemens Foundation Technology Grant",
                    "grantor": "Siemens Foundation",
                    "type": "foundation",
                    "focus": "STEM, Manufacturing, Infrastructure",
                    "amount": "$100,000",
                    "deadline": "2026-03-15",
                    "eligibility": "Tech companies with social impact",
                    "url": "https://www.siemens-foundation.org/",
                    "fit_score": 78,
                },
            ]
            # Stamp every fallback record as sample data.
            for _g in discovered_grants:
                _g["notice"] = SAMPLE_DATA_NOTICE
            used_fallback = True

        if grant_type:
            discovered_grants = [
                g for g in discovered_grants if g.get("type") == grant_type
            ]

        # Store discovered grants
        new_grants = 0
        for grant in discovered_grants:
            data = {
                "grant_name": grant.get("name", "(untitled)"),
                "grantor": grant.get("grantor", "Unknown"),
                "grant_type": grant.get("type", "federal"),
                "focus_area": grant.get("focus", ""),
                "award_amount": grant.get("amount", ""),
                "deadline": grant.get("deadline", ""),
                "eligibility": grant.get("eligibility", ""),
                "url": grant.get("url", ""),
                "fit_score": grant.get("fit_score", 0),
            }
            integrity_hash = self._calculate_integrity_hash(data)

            try:
                c.execute(
                    """
                    INSERT INTO grant_opportunities (
                        grant_name, grantor, grant_type, focus_area, award_amount,
                        deadline, eligibility, url, status, fit_score, notes, integrity_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data["grant_name"],
                        data["grantor"],
                        data["grant_type"],
                        data["focus_area"],
                        data["award_amount"],
                        data["deadline"],
                        data["eligibility"],
                        data["url"],
                        "discovered",
                        data["fit_score"],
                        grant.get("notice") or "Live result from Grants.gov API",
                        integrity_hash,
                    ),
                )
                new_grants += 1
            except sqlite3.IntegrityError:
                pass  # Already exists

        self.conn.commit()

        # Log search ("manual" = our own labeled sample data; schema CHECK allows it)
        search_data = {
            "search_query": ", ".join(keywords),
            "search_source": "manual" if used_fallback else "grants.gov",
            "results_found": len(discovered_grants),
            "new_opportunities": new_grants,
        }
        search_hash = self._calculate_integrity_hash(search_data)

        c.execute(
            """
            INSERT INTO grant_searches (search_query, search_source, results_found, new_opportunities, integrity_hash)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                search_data["search_query"],
                search_data["search_source"],
                search_data["results_found"],
                search_data["new_opportunities"],
                search_hash,
            ),
        )

        self.conn.commit()
        self._log_action(
            f"Grant search completed: {new_grants} new opportunities discovered",
            details=SAMPLE_DATA_NOTICE if used_fallback else "live Grants.gov results",
        )

        return discovered_grants

    def analyze_winning_grant(
        self,
        grant_name: str,
        recipient: str,
        amount: str,
        year: int,
        narrative_excerpt: str = None,
    ) -> dict:
        """Analyze a winning grant to learn success patterns"""
        c = self.conn.cursor()

        # Simulated analysis (in production, use NLP to extract patterns)
        success_factors = json.dumps(
            [
                "Clear problem statement with quantifiable impact",
                "Strong project methodology with milestones",
                "Detailed budget with justifications",
                "Letters of support from industry partners",
                "Previous track record of successful execution",
                "Alignment with grantor's strategic priorities",
                "Measurable outcomes and evaluation plan",
            ]
        )

        data = {
            "grant_name": grant_name,
            "recipient": recipient,
            "award_amount": amount,
            "year": year,
            "success_factors": success_factors,
            "narrative_excerpt": narrative_excerpt,
        }

        integrity_hash = self._calculate_integrity_hash(data)

        c.execute(
            """
            INSERT INTO winning_grants (
                grant_name, recipient, award_amount, year, success_factors,
                narrative_excerpt, integrity_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                grant_name,
                recipient,
                amount,
                year,
                success_factors,
                narrative_excerpt,
                integrity_hash,
            ),
        )

        self.conn.commit()
        self._log_action(f"Analyzed winning grant: {grant_name} ({recipient})")

        return {
            "grant_name": grant_name,
            "recipient": recipient,
            "amount": amount,
            "success_factors": json.loads(success_factors),
        }

    def write_grant_application(
        self, grant_opportunity_id: int, title: str = None
    ) -> dict:
        """Write a grant application based on infrastructure needs"""
        c = self.conn.cursor()

        # Get grant opportunity details
        c.execute(
            "SELECT grant_name, grantor, focus_area, award_amount FROM grant_opportunities WHERE id = ?",
            (grant_opportunity_id,),
        )
        grant_info = c.fetchone()

        if not grant_info:
            return {"error": "Grant opportunity not found"}

        grant_name, grantor, focus_area, award_amount = grant_info

        # Get infrastructure needs
        c.execute("""
            SELECT description, estimated_cost, justification, priority
            FROM infrastructure_needs
            WHERE status = 'needed'
            ORDER BY 
                CASE priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END
            LIMIT 5
        """)
        needs = c.fetchall()

        # Generate application narrative (template-based, in production use AI)
        narrative = f"""
PROJECT TITLE: Scaling Mythara Infrastructure for Enterprise Contract Verification

EXECUTIVE SUMMARY (draft — figures below are projections and targets, not current performance; verify before filing):
Mythara is developing a Symbolic Safety Integrity Protocol (SSIP) 
that provides cryptographic verification for contracts and legal agreements. Our 
technology addresses the critical need for tamper-proof, auditable contract management 
in industries including healthcare, financial services, government, and manufacturing.

This grant will enable Mythara to deploy dedicated server infrastructure capable 
of processing 10,000+ contract verifications per day while maintaining 99.9% uptime 
and meeting stringent security requirements aligned with SOC 2, CMMC Level 3, and HIPAA control frameworks (certifications not currently held).

PROBLEM STATEMENT:
Contract fraud, disputes, and inefficiencies cost organizations significantly each year. 
(Insert a verified figure with citation before filing.) 
Current solutions (DocuSign, Adobe Sign) provide basic e-signatures but lack cryptographic 
integrity verification. Our SSIP technology fills this gap by creating immutable audit 
trails with blockchain-style verification.

Current infrastructure limitations prevent us from serving enterprise customers who require:
- 99.9% uptime SLA
- SOC 2 Type II certification
- CMMC Level 3 compliance (defense contractors)
- Real-time verification at scale (1000+ concurrent operations)

PROJECT OBJECTIVES:
1. Deploy production-grade server infrastructure (GPU servers, application servers, databases)
2. Achieve SOC 2 Type II and CMMC Level 3 certifications
3. Scale to 10,000 contract verifications per day
4. Onboard 50 enterprise customers in Year 1
5. Create 5 high-paying jobs (DevOps, Security, Engineering)

METHODOLOGY:
Phase 1 (Months 1-3): Infrastructure Deployment
- Deploy dedicated GPU servers for AI/ML orchestration
- Set up redundant application and database servers
- Implement enterprise security stack (SIEM, IDS/IPS, HSMs)

Phase 2 (Months 4-6): Security Certification
- Complete SOC 2 Type II audit
- Achieve CMMC Level 3 certification
- Deploy Security Operations Center (SOC)

Phase 3 (Months 7-12): Scale & Customer Onboarding
- Onboard 50 enterprise customers
- Process 10,000+ daily verifications
- Achieve $2M ARR milestone

BUDGET JUSTIFICATION:
Infrastructure investment of ${sum(need[1] for need in needs):,.0f} will enable:
"""

        for desc, cost, justification, priority in needs[:5]:
            narrative += f"\n- {desc} (${cost:,.0f}): {justification}"

        narrative += """

IMPACT & SUSTAINABILITY (projections — targets, not current results):
Year 1 Impact:
- 50 enterprise customers deployed
- 3.65M contract verifications processed annually
- $2M in revenue (self-sustaining after Year 1)
- 5 high-skilled jobs created
- Zero contract fraud for customers (100% integrity verification)

Long-term Sustainability:
Mythara operates on a SaaS model with 95% gross margins. Infrastructure 
investment will be recovered within 12 months through customer revenue. By Year 3, 
we project 500 customers and $20M ARR.

EVALUATION PLAN:
Quarterly metrics:
- System uptime (target: 99.9%)
- Contract verifications processed
- Customer acquisition
- Revenue growth
- Certification milestones achieved
"""

        # Generate budget
        budget = "BUDGET SUMMARY:\n\n"
        budget += f"{'Category':<30} {'Cost':>15} {'Justification':<50}\n"
        budget += "=" * 100 + "\n"

        total_cost = 0
        for desc, cost, justification, priority in needs[:10]:
            category = desc.split("(")[0].strip()[:28]
            budget += f"{category:<30} ${cost:>14,.0f} {justification[:48]}\n"
            total_cost += cost

        budget += "=" * 100 + "\n"
        budget += f"{'TOTAL REQUEST':<30} ${total_cost:>14,.0f}\n"

        # Save application
        app_data = {
            "grant_opportunity_id": grant_opportunity_id,
            "application_title": title
            or f"Mythara Infrastructure Scaling - {grant_name}",
            "narrative": narrative,
            "budget": budget,
            "project_summary": narrative.split("\n\n")[1],  # Executive summary
            "status": "draft",
        }

        integrity_hash = self._calculate_integrity_hash(app_data)

        c.execute(
            """
            INSERT INTO grant_applications (
                grant_opportunity_id, application_title, narrative, budget,
                project_summary, status, integrity_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                grant_opportunity_id,
                app_data["application_title"],
                narrative,
                budget,
                app_data["project_summary"],
                "draft",
                integrity_hash,
            ),
        )

        app_id = c.lastrowid
        self.conn.commit()

        self._log_action(f"Grant application drafted: {app_data['application_title']}")

        return {
            "application_id": app_id,
            "title": app_data["application_title"],
            "grant_name": grant_name,
            "grantor": grantor,
            "budget_total": f"${total_cost:,.0f}",
            "status": "draft",
            "integrity_hash": integrity_hash,
        }

    def get_infrastructure_needs(self) -> List[dict]:
        """Get all infrastructure needs"""
        c = self.conn.cursor()

        c.execute("""
            SELECT need_category, description, estimated_cost, priority, 
                   justification, grant_alignment, status
            FROM infrastructure_needs
            ORDER BY 
                CASE priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END,
                estimated_cost DESC
        """)

        results = []
        for row in c.fetchall():
            results.append(
                {
                    "category": row[0],
                    "description": row[1],
                    "cost": row[2],
                    "priority": row[3],
                    "justification": row[4],
                    "grant_alignment": row[5],
                    "status": row[6],
                }
            )

        return results

    def generate_grant_report(self) -> str:
        """Generate comprehensive grant activity report"""
        c = self.conn.cursor()

        # Get stats
        c.execute("SELECT COUNT(*) FROM grant_opportunities")
        total_opportunities = c.fetchone()[0]

        c.execute(
            'SELECT COUNT(*) FROM grant_opportunities WHERE status = "discovered"'
        )
        new_opportunities = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM grant_applications WHERE status = "submitted"')
        submitted_apps = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM grant_applications WHERE result = "awarded"')
        awarded_grants = c.fetchone()[0]

        c.execute(
            'SELECT SUM(estimated_cost) FROM infrastructure_needs WHERE status = "needed"'
        )
        total_funding_needed = c.fetchone()[0] or 0

        c.execute("SELECT COUNT(*) FROM winning_grants")
        winning_examples = c.fetchone()[0]

        report = f"""
================================================================================
MYTHARA GRANT WRITING BOT - DAILY REPORT
================================================================================

GRANT OPPORTUNITIES:
   Total Opportunities Tracked: {total_opportunities}
   New Opportunities (Pending Review): {new_opportunities}
   Applications Submitted: {submitted_apps}
   Grants Awarded: {awarded_grants}

INFRASTRUCTURE FUNDING:
   Total Funding Needed: ${total_funding_needed:,.0f}
   Winning Grant Examples Analyzed: {winning_examples}

TOP 5 GRANT OPPORTUNITIES (by Fit Score):
"""

        c.execute("""
            SELECT grant_name, grantor, award_amount, deadline, fit_score, status
            FROM grant_opportunities
            ORDER BY fit_score DESC
            LIMIT 5
        """)

        for row in c.fetchall():
            name, grantor, amount, deadline, fit, status = row
            report += f"\n   {name}"
            report += (
                f"\n      Grantor: {grantor} | Amount: {amount} | Deadline: {deadline}"
            )
            report += f"\n      Fit Score: {fit}/100 | Status: {status}"

        report += "\n\nINFRASTRUCTURE NEEDS (Critical Priority):\n"

        c.execute("""
            SELECT description, estimated_cost, grant_alignment
            FROM infrastructure_needs
            WHERE priority = 'critical' AND status = 'needed'
            LIMIT 5
        """)

        for row in c.fetchall():
            desc, cost, alignment = row
            report += f"\n   - {desc}"
            report += f"\n     Cost: ${cost:,.0f} | Grant Alignment: {alignment}"

        report += "\n\n" + "=" * 80 + "\n"

        return report

    def _log_action(self, action: str, details: str = None):
        """Log action to audit trail"""
        c = self.conn.cursor()

        data = {
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }

        integrity_hash = self._calculate_integrity_hash(data)

        c.execute(
            """
            INSERT INTO grant_audit (action, details, integrity_hash)
            VALUES (?, ?, ?)
        """,
            (action, details, integrity_hash),
        )

        self.conn.commit()


if __name__ == "__main__":
    print("Initializing Mythara Grant Writing Bot...")
    print("=" * 80)

    bot = MytharaGrantWriterBot()

    # Demo workflow
    print("\n[DEMO] Searching for grant opportunities\n")
    grants = bot.search_grants()
    print(f"[OK] Discovered {len(grants)} grant opportunities")

    print("\n[DEMO] Analyzing winning grant examples\n")
    winning = bot.analyze_winning_grant(
        "NSF SBIR Phase II - AI Infrastructure",
        "TechStartup Inc",
        "$750,000",
        2024,
        "Our innovative AI platform addresses critical infrastructure needs...",
    )
    print(f"[OK] Analyzed winning grant: {winning['grant_name']}")
    print(f"     Success factors identified: {len(winning['success_factors'])}")

    print("\n[DEMO] Writing grant application\n")
    application = bot.write_grant_application(1, "Mythara Infrastructure Scaling")
    print(f"[OK] Grant application drafted: {application['title']}")
    print(f"     For: {application['grant_name']}")
    print(f"     Budget Total: {application['budget_total']}")

    print("\n[DEMO] Infrastructure needs summary\n")
    needs = bot.get_infrastructure_needs()
    total_critical = sum(n["cost"] for n in needs if n["priority"] == "critical")
    print(f"[OK] {len(needs)} infrastructure needs identified")
    print(f"     Critical priority funding needed: ${total_critical:,.0f}")

    # Generate report
    print("\n" + bot.generate_grant_report())

    print("\n[OK] Grant Writer Bot demo complete!")
    print("=" * 80)
