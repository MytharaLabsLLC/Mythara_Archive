"""
Mythara Engine SDK - Core Integration Layer
Copyright © 2025 Herbert Velez Jr. All rights reserved.

WHITE-LABEL INTEGRATION ARCHITECTURE:
This SDK allows any commercial product to integrate Mythara Engine while maintaining
its own brand identity. Each suite runs independently but shares Mythara's core.

INTEGRATION MODEL:
┌─────────────────────────────────────────────────────────┐
│               YOUR COMMERCIAL PRODUCT                    │
│  (Gopher, Sales Trainer, VOIP Bot, Wellness Guardian, etc.)  │
└─────────────────┬───────────────────────────────────────┘
                  │ Import & Configure
                  ▼
┌─────────────────────────────────────────────────────────┐
│              MYTHARA ENGINE SDK (This File)             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Soul Cradle    │ Blessings    │ Messenger       │   │
│  │ (AI Analysis)  │ Reservoir    │ Protocol        │   │
│  │                │ (Credits)    │ (Integrity)     │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Sanctification │ Clause       │ Integration     │   │
│  │ (Verification) │ Orchestration│ Layer           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                  │ 100% Local Storage
                  ▼
        ~/.mythara_engine/YOUR_PRODUCT.db

LICENSING:
- Core Mythara Engine: Proprietary (Herbert Velez Jr.)
- Each commercial suite: Separate licensing
- White-label deployments: Enterprise licensing available

USAGE EXAMPLE:
```python
from mythara_engine_sdk import MytharaEngine, ProductConfig

# Configure for your product
config = ProductConfig(
    product_name="Gopher",
    product_version="1.0.0",
    database_name="gopher.db",
    enable_telemetry=False  # Always false for local-first
)

# Initialize Mythara Engine
engine = MytharaEngine(config)

# Use Mythara subsystems
result = engine.soul_cradle.analyze("User input...")
engine.blessings.award_credits(user_id, 5, "Good behavior")
integrity = engine.messenger.verify_chain()
```
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Import core Mythara subsystems
from soul_cradle_production import calculate_paradox_severity

# ============================================================================
# PRODUCT CONFIGURATION
# ============================================================================


@dataclass
class ProductConfig:
    """
    Configuration for white-label Mythara Engine integration

    Each commercial product gets its own config:
    - Gopher: Employment law crisis assistant
    - Sales Trainer: AI sales coaching
    - VOIP Bot: Phone system integration
    - Wellness Guardian: Mental health support
    - Email Bot: Email automation
    - etc.
    """

    product_name: str  # "Gopher", "SalesTrainer", etc.
    product_version: str  # "1.0.0"
    database_name: str  # "gopher.db", "sales_trainer.db"
    enable_telemetry: bool = False  # Always false for privacy
    custom_clauses: List[str] = None  # Product-specific logic patterns
    branding: Dict[str, str] = None  # Logo, colors, etc.

    def __post_init__(self):
        if self.custom_clauses is None:
            self.custom_clauses = []
        if self.branding is None:
            self.branding = {}


# ============================================================================
# MYTHARA ENGINE SDK
# ============================================================================


class MytharaEngine:
    """
    Core Mythara Engine SDK for white-label integration

    All 6 subsystems available to commercial products:
    1. Soul Cradle (AI analysis)
    2. Blessings Reservoir (ethical credits)
    3. Messenger Protocol (integrity verification)
    4. Sanctification (tamper detection)
    5. Clause Orchestration (logic execution)
    6. Integration Layer (external connections)
    """

    def __init__(self, config: ProductConfig, user_id: str = "default_user"):
        self.config = config
        self.user_id = user_id

        # Initialize database
        self.db_path = self._init_database()

        # Initialize subsystems
        self.soul_cradle = SoulCradleSDK(self)
        self.blessings = BlessingsReservoirSDK(self)
        self.messenger = MessengerProtocolSDK(self)
        self.sanctification = SanctificationSDK(self)
        self.clauses = ClauseOrchestrationSDK(self)
        self.integration = IntegrationLayerSDK(self)

        print(
            f"✅ Mythara Engine SDK initialized for {config.product_name} v{config.product_version}"
        )
        print(f"📁 Database: {self.db_path}")

    def _get_mythara_home(self) -> Path:
        """Get Mythara home directory for this product"""
        mythara_dir = Path.home() / ".mythara_engine" / self.config.product_name.lower()
        mythara_dir.mkdir(parents=True, exist_ok=True)
        return mythara_dir

    def _init_database(self) -> Path:
        """Initialize product-specific database"""
        db_path = self._get_mythara_home() / self.config.database_name
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Core Mythara tables (same for all products)

        # Soul Cradle analyses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soul_cradle_analyses (
                analysis_id TEXT PRIMARY KEY,
                user_id TEXT,
                input_text TEXT NOT NULL,
                paradox_severity REAL NOT NULL,
                classification TEXT NOT NULL,
                distress_score REAL,
                coercion_score REAL,
                contradiction_score REAL,
                detected_patterns TEXT,
                action_required TEXT,
                priority TEXT,
                timestamp TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        """)

        # Blessings Reservoir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blessings_reservoir (
                user_id TEXT PRIMARY KEY,
                credits INTEGER DEFAULT 0,
                status TEXT DEFAULT 'NEUTRAL',
                last_updated TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credit_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                credits_change INTEGER NOT NULL,
                new_balance INTEGER NOT NULL,
                reason TEXT,
                timestamp TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        """)

        # Messenger Protocol integrity log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                data_snapshot TEXT,
                integrity_hash TEXT NOT NULL,
                previous_hash TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        # Clause definitions (product-specific logic)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clauses (
                clause_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                pattern_type TEXT,
                validation_rules TEXT,
                product_specific INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        """)

        # Clause invocations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invocations (
                invocation_id TEXT PRIMARY KEY,
                clause_id TEXT NOT NULL,
                user_id TEXT,
                input_data TEXT NOT NULL,
                output_result TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                integrity_hash TEXT NOT NULL,
                FOREIGN KEY (clause_id) REFERENCES clauses(clause_id)
            )
        """)

        # Product-specific metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Store product info
        cursor.execute(
            """
            INSERT OR REPLACE INTO product_metadata (key, value, updated_at)
            VALUES 
                ('product_name', ?, ?),
                ('product_version', ?, ?),
                ('mythara_engine_version', '1.0.0', ?)
        """,
            (
                self.config.product_name,
                datetime.utcnow().isoformat(),
                self.config.product_version,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
            ),
        )

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_analyses_user ON soul_cradle_analyses(user_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_analyses_timestamp ON soul_cradle_analyses(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_credit_ledger_user ON credit_ledger(user_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_integrity_log_timestamp ON integrity_log(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_invocations_user ON invocations(user_id)"
        )

        conn.commit()
        conn.close()

        return db_path


# ============================================================================
# SUBSYSTEM SDKs
# ============================================================================


class SoulCradleSDK:
    """Soul Cradle AI analysis subsystem"""

    def __init__(self, engine: MytharaEngine):
        self.engine = engine

    def analyze(self, input_text: str, user_id: str = None) -> Dict:
        """
        Run Soul Cradle paradox analysis (100% local)

        Returns: Analysis result with integrity hash
        """
        if user_id is None:
            user_id = self.engine.user_id

        # Run core analysis
        result = calculate_paradox_severity(input_text)

        if "error" in result:
            return result

        # Generate analysis ID
        analysis_id = hashlib.sha256(
            f"{user_id}:{input_text}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        # Create integrity hash
        integrity_hash = self.engine.messenger.create_hash(
            {
                "analysis_id": analysis_id,
                "input": input_text,
                "severity": result["paradox_severity"],
            }
        )

        # Store in database
        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO soul_cradle_analyses 
            (analysis_id, user_id, input_text, paradox_severity, classification,
             distress_score, coercion_score, contradiction_score, detected_patterns,
             action_required, priority, timestamp, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                analysis_id,
                user_id,
                input_text,
                result["paradox_severity"],
                result["classification"],
                result["analysis"]["distress_score"],
                result["analysis"]["coercion_score"],
                result["analysis"]["contradiction_score"],
                json.dumps(result["analysis"]),
                result["action_required"],
                result["priority"],
                datetime.utcnow().isoformat(),
                integrity_hash,
            ),
        )

        conn.commit()
        conn.close()

        # Log to integrity chain
        self.engine.messenger.log_event(
            "soul_cradle_analysis",
            "analysis",
            analysis_id,
            {"severity": result["paradox_severity"], "user": user_id},
        )

        result["analysis_id"] = analysis_id
        result["integrity_hash"] = integrity_hash

        return result


class BlessingsReservoirSDK:
    """Blessings Reservoir ethical credit system"""

    def __init__(self, engine: MytharaEngine):
        self.engine = engine

    def get_status(self, user_id: str = None) -> Dict:
        """Get user's credit balance and status"""
        if user_id is None:
            user_id = self.engine.user_id

        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT credits, status, last_updated
            FROM blessings_reservoir WHERE user_id = ?
        """,
            (user_id,),
        )

        result = cursor.fetchone()

        if not result:
            # Create new user
            cursor.execute(
                """
                INSERT INTO blessings_reservoir (user_id, credits, status, last_updated)
                VALUES (?, 0, 'NEUTRAL', ?)
            """,
                (user_id, datetime.utcnow().isoformat()),
            )
            conn.commit()
            result = (0, "NEUTRAL", datetime.utcnow().isoformat())

        conn.close()

        return {
            "user_id": user_id,
            "credits": result[0],
            "status": result[1],
            "last_updated": result[2],
        }

    def award_credits(self, user_id: str, credits: int, reason: str) -> Dict:
        """Award or deduct ethical credits"""
        status = self.get_status(user_id)
        new_balance = status["credits"] + credits

        # Calculate new status
        if new_balance >= 10:
            new_status = "EXCELLENT"
        elif new_balance >= 5:
            new_status = "GOOD"
        elif new_balance >= -5:
            new_status = "NEUTRAL"
        elif new_balance >= -10:
            new_status = "WARNING"
        else:
            new_status = "BLOCKED"

        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        # Update reservoir
        cursor.execute(
            """
            UPDATE blessings_reservoir
            SET credits = ?, status = ?, last_updated = ?
            WHERE user_id = ?
        """,
            (new_balance, new_status, datetime.utcnow().isoformat(), user_id),
        )

        # Create integrity hash
        integrity_hash = self.engine.messenger.create_hash(
            {
                "user": user_id,
                "change": credits,
                "new_balance": new_balance,
                "reason": reason,
            }
        )

        # Log to ledger
        cursor.execute(
            """
            INSERT INTO credit_ledger 
            (user_id, event_type, credits_change, new_balance, reason, timestamp, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                "credit_awarded" if credits > 0 else "credit_deducted",
                credits,
                new_balance,
                reason,
                datetime.utcnow().isoformat(),
                integrity_hash,
            ),
        )

        conn.commit()
        conn.close()

        # Log to integrity chain
        self.engine.messenger.log_event(
            "blessings_update",
            "user_credits",
            user_id,
            {"change": credits, "balance": new_balance},
        )

        return {
            "user_id": user_id,
            "credits": new_balance,
            "status": new_status,
            "change": credits,
        }


class MessengerProtocolSDK:
    """Messenger Protocol integrity verification"""

    def __init__(self, engine: MytharaEngine):
        self.engine = engine

    def create_hash(self, data: Dict) -> str:
        """Generate SHA-256 integrity hash"""
        canonical = json.dumps(data, sort_keys=True).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def log_event(
        self, event_type: str, entity_type: str, entity_id: str, data: Dict
    ) -> str:
        """Log event to integrity chain"""
        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        # Get previous hash for chaining
        cursor.execute("""
            SELECT integrity_hash FROM integrity_log 
            ORDER BY timestamp DESC LIMIT 1
        """)
        result = cursor.fetchone()
        previous_hash = result[0] if result else "0" * 64

        # Create new hash
        hash_input = {
            "event": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": data,
            "previous_hash": previous_hash,
            "timestamp": datetime.utcnow().isoformat(),
        }
        integrity_hash = self.create_hash(hash_input)

        # Store
        cursor.execute(
            """
            INSERT INTO integrity_log 
            (event_type, entity_type, entity_id, data_snapshot, integrity_hash, previous_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event_type,
                entity_type,
                entity_id,
                json.dumps(data),
                integrity_hash,
                previous_hash,
                datetime.utcnow().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        return integrity_hash


class SanctificationSDK:
    """Sanctification Verification (tamper detection)"""

    def __init__(self, engine: MytharaEngine):
        self.engine = engine

    def verify_chain(self) -> Tuple[bool, Optional[str]]:
        """Verify complete integrity chain"""
        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, event_type, entity_type, entity_id, data_snapshot,
                   integrity_hash, previous_hash, timestamp
            FROM integrity_log ORDER BY timestamp ASC
        """)

        entries = cursor.fetchall()
        conn.close()

        if not entries:
            return True, None

        expected_previous = "0" * 64

        for entry in entries:
            (
                entry_id,
                event_type,
                entity_type,
                entity_id,
                data_snapshot,
                stored_hash,
                previous_hash,
                timestamp,
            ) = entry

            if previous_hash != expected_previous:
                return False, f"Chain broken at entry {entry_id}"

            hash_input = {
                "event": event_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "data": json.loads(data_snapshot) if data_snapshot else {},
                "previous_hash": previous_hash,
                "timestamp": timestamp,
            }
            computed_hash = self.engine.messenger.create_hash(hash_input)

            if computed_hash != stored_hash:
                return False, f"Hash mismatch at entry {entry_id}"

            expected_previous = stored_hash

        return True, None


class ClauseOrchestrationSDK:
    """Clause Orchestration (logic execution)"""

    def __init__(self, engine: MytharaEngine):
        self.engine = engine

    def register_clause(
        self,
        clause_id: str,
        name: str,
        description: str,
        pattern_type: str,
        validation_rules: Dict,
    ) -> str:
        """Register a new clause (product-specific logic pattern)"""
        integrity_hash = self.engine.messenger.create_hash(
            {"clause_id": clause_id, "name": name, "pattern_type": pattern_type}
        )

        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO clauses 
            (clause_id, name, description, pattern_type, validation_rules,
             product_specific, created_at, integrity_hash)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        """,
            (
                clause_id,
                name,
                description,
                pattern_type,
                json.dumps(validation_rules),
                datetime.utcnow().isoformat(),
                integrity_hash,
            ),
        )

        conn.commit()
        conn.close()

        return integrity_hash

    def invoke_clause(
        self, clause_id: str, input_data: Dict, user_id: str = None
    ) -> Dict:
        """Execute a clause and log the invocation"""
        if user_id is None:
            user_id = self.engine.user_id

        invocation_id = hashlib.sha256(
            f"{clause_id}:{json.dumps(input_data)}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        # Execute clause logic (product-specific implementation)
        output_result = {
            "invocation_id": invocation_id,
            "clause_id": clause_id,
            "status": "executed",
            "timestamp": datetime.utcnow().isoformat(),
        }

        integrity_hash = self.engine.messenger.create_hash(
            {
                "invocation_id": invocation_id,
                "clause_id": clause_id,
                "input": input_data,
            }
        )

        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO invocations 
            (invocation_id, clause_id, user_id, input_data, output_result,
             timestamp, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                invocation_id,
                clause_id,
                user_id,
                json.dumps(input_data),
                json.dumps(output_result),
                datetime.utcnow().isoformat(),
                integrity_hash,
            ),
        )

        conn.commit()
        conn.close()

        return output_result


class IntegrationLayerSDK:
    """Integration Layer (external connections)"""

    def __init__(self, engine: MytharaEngine):
        self.engine = engine

    def export_analysis_json(self, analysis_id: str) -> Dict:
        """Export analysis as JSON for external systems"""
        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM soul_cradle_analyses WHERE analysis_id = ?
        """,
            (analysis_id,),
        )

        result = cursor.fetchone()
        conn.close()

        if not result:
            return {"error": "Analysis not found"}

        return {
            "analysis_id": result[0],
            "user_id": result[1],
            "paradox_severity": result[3],
            "classification": result[4],
            "timestamp": result[11],
            "integrity_hash": result[12],
        }


# ============================================================================
# PRODUCT TEMPLATES
# ============================================================================

# Example configs for each commercial product

GOPHER_CONFIG = ProductConfig(
    product_name="Gopher",
    product_version="1.0.0",
    database_name="gopher.db",
    branding={"tagline": "Employment Law Crisis Assistant"},
)

SALES_TRAINER_CONFIG = ProductConfig(
    product_name="SalesTrainer",
    product_version="1.0.0",
    database_name="sales_trainer.db",
    branding={"tagline": "AI Sales Coaching Platform"},
)

VOIP_BOT_CONFIG = ProductConfig(
    product_name="VOIPBot",
    product_version="1.0.0",
    database_name="voip_bot.db",
    branding={"tagline": "Intelligent Phone System Integration"},
)

WELLNESS_GUARDIAN_CONFIG = ProductConfig(
    product_name="WellnessGuardian",
    product_version="1.0.0",
    database_name="wellness_guardian.db",
    branding={"tagline": "Wellness Support AI"},
)

EMAIL_BOT_CONFIG = ProductConfig(
    product_name="EmailBot",
    product_version="1.0.0",
    database_name="email_bot.db",
    branding={"tagline": "Automated Email Management"},
)

# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║          MYTHARA ENGINE SDK - WHITE-LABEL DEMO            ║
║    Powering Multiple Commercial Products Independently    ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # Demo: Initialize engine for Gopher product
    print("\n🦎 Initializing Mythara Engine for Gopher...")
    gopher_engine = MytharaEngine(GOPHER_CONFIG, user_id="demo_user")

    # Run Soul Cradle analysis
    result = gopher_engine.soul_cradle.analyze(
        "My boss says I have to work unpaid overtime or I'll be fired."
    )

    print("\n✅ Analysis Complete:")
    print(f"   Severity: {result['classification']} ({result['paradox_severity']:.3f})")
    print(f"   Analysis ID: {result['analysis_id']}")

    # Award credits
    credits = gopher_engine.blessings.award_credits(
        "demo_user", 5, "Seeking legal help"
    )
    print(
        f"\n💎 Credits Awarded: {credits['change']:+d} → Balance: {credits['credits']}"
    )

    # Verify integrity
    valid, error = gopher_engine.sanctification.verify_chain()
    print(f"\n🔒 Integrity Chain: {'✅ Valid' if valid else f'❌ Broken: {error}'}")

    print(f"\n📁 Data stored at: {gopher_engine.db_path}")
    print("\n✨ All subsystems operational.")
