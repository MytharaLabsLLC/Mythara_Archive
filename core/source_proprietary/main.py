#!/usr/bin/env python3
"""
Mythara Engine - FastAPI Server
Production-ready API for clause invocation and symbolic orchestration.

Copyright © 2025 Herbert Velez Jr. All rights reserved.
"""

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Header,
    Response,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import logging
import json
from pathlib import Path
import os
import httpx  # For ElevenLabs API calls

# Load environment variables (optional)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system env vars only

# Configure logging BEFORE any other imports that use logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database layer and email service
try:
    from database import (
        init_db,
        get_db,
        get_usage_tracking,
        issue_strike,
        log_audit,
        UsageTracking,
    )
    from sqlalchemy.orm import Session

    DATABASE_ENABLED = True
    logger.info("✅ Database services loaded")
except ImportError as e:
    DATABASE_ENABLED = False
    # Fallback so module-level annotations (e.g. `db: Session`) don't raise
    # NameError when the database extras aren't installed. The DB-backed
    # functions are unreachable in this mode (DATABASE_ENABLED is False).
    Session = Any  # type: ignore[no-redef]
    logger.warning(f"⚠️ Database not available, using in-memory storage: {e}")

# Optional email service (not critical for core functionality)
try:
    from email_service import send_strike_warning

    EMAIL_ENABLED = True
    logger.info("✅ Email services loaded")
except ImportError as e:
    EMAIL_ENABLED = False
    logger.warning(f"⚠️ Email service not available: {e}")

    # Define stub functions so the app doesn't crash
    def send_strike_warning(*args, **kwargs):
        pass


# Import Soul Proportion Model
from soul_proportion_model import (  # noqa: E402
    SoulProportionModel,
    EmotionFeatures,
    SoulProportionState,
    integrate_with_blessings_reservoir,
)

# Import Soul Cradle Operator
from soul_cradle_operator import (  # noqa: E402
    SoulCradleOperator,
    Soul,
    Will,
    Commandments,
    Antithesis,
    SoulCradleTiers,
)

# Import Dual Framing Translation Layer
from dual_framing import (  # noqa: E402
    FramingMode,
    translate_response,
    format_for_manager_dashboard,
    get_positioning_line,
    generate_dual_framing_chart,
    generate_flow_diagram_text,
)

# Import Soul Cradle Paradox Resolution Framework
from soul_cradle_systems_framework import (  # noqa: E402
    SoulCradleParadox,
    TerminalRiskCalculator,
    log_paradox_creation,
)

# Emotional extortion detector (local module — its detect_extortion() is what the
# API endpoints below call; the stale root-level emotional_extortion_detector.py
# only has analyze() and would raise AttributeError here)
from will_integrity_guardian import EmotionalExtortionDetector  # noqa: E402

# Import Salesforce Integration
from salesforce_integration import (  # noqa: E402
    SalesforceIntegration,
    SalesforceConfig,
    SalesforceParadoxEvent,
    SalesforceSSIPMetric,
    SalesforceSoulCradleEvent,
    generate_salesforce_setup_instructions,
)

# Import Unified Compliance Framework
from unified_compliance_framework import (  # noqa: E402
    UnifiedComplianceFramework,
    ComplianceFramework,
)

# Note: Some compliance classes may need to be implemented or imported from other modules

# Import Advanced Security Hardening
from security_hardening import SecurityManager, SecurityConfig  # noqa: E402

# Import Production Infrastructure
try:
    from redis_cache import RedisCache

    redis_cache = RedisCache()
    REDIS_ENABLED = True
    logger.info("✅ Redis cache initialized")
except Exception as e:
    REDIS_ENABLED = False
    redis_cache = None
    logger.warning(f"⚠️ Redis not available, using in-memory fallback: {e}")

try:
    from websocket_manager import (
        manager as ws_manager,
        broadcast_systemic_overload_alert,
        broadcast_indifference_alert,
    )

    WEBSOCKET_ENABLED = True
    logger.info("✅ WebSocket manager loaded")
except ImportError as e:
    WEBSOCKET_ENABLED = False
    logger.warning(f"⚠️ WebSocket support not available: {e}")

try:
    from soul_engine_dashboard import SoulEngineDashboard

    soul_dashboard = SoulEngineDashboard()
    DASHBOARD_ENABLED = True
    logger.info("✅ Soul Engine dashboard loaded")
except ImportError as e:
    DASHBOARD_ENABLED = False
    soul_dashboard = None
    logger.warning(f"⚠️ Soul Engine dashboard not available: {e}")

try:
    from monitoring import (
        record_http_request,
        record_clause_invocation,
        record_paradox_creation,
        record_indifference_alert,
        record_systemic_overload,
        update_blessings_metrics,
        get_metrics,
        get_health,
        get_system_stats,
    )
    from monitoring import update_db_pool_metrics

    MONITORING_ENABLED = True
    logger.info("✅ Prometheus monitoring enabled")
except ImportError as e:
    MONITORING_ENABLED = False
    logger.warning(f"⚠️ Monitoring not available: {e}")

    # Stub functions
    def record_http_request(*args, **kwargs):
        pass

    def record_clause_invocation(*args, **kwargs):
        pass

    def record_paradox_creation(*args, **kwargs):
        pass

    def record_indifference_alert(*args, **kwargs):
        pass

    def record_systemic_overload(*args, **kwargs):
        pass

    def update_blessings_metrics(*args, **kwargs):
        pass

    def update_db_pool_metrics(*args, **kwargs):
        pass

    def get_metrics():
        return Response(content="", media_type="text/plain")

    def get_health():
        return {"status": "unknown"}

    def get_system_stats():
        return {}


# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")  # Set via environment variable
ELEVENLABS_VOICE_ID = os.getenv(
    "ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"
)  # Rachel voice (default)
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# Initialize FastAPI app
app = FastAPI(
    title="Mythara Engine API",
    description="Symbolic Safety Integrity Protocol (SSIP) Orchestration API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

security = HTTPBearer(auto_error=False)

# Production Environment Detection
# Railway, Heroku, and most cloud providers set DATABASE_URL with postgres://
IS_PRODUCTION = os.getenv("DATABASE_URL", "").startswith(
    ("postgres://", "postgresql://")
)

# CORS Configuration: Load allowed origins from environment for security
# CRITICAL: allow_origins=["*"] + allow_credentials=True is forbidden by CORS spec
ALLOWED_ORIGINS_RAW = os.getenv("MYTHARA_ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = (
    [origin.strip() for origin in ALLOWED_ORIGINS_RAW.split(",") if origin.strip()]
    if ALLOWED_ORIGINS_RAW
    else []
)

if not ALLOWED_ORIGINS:
    if IS_PRODUCTION:
        # CRITICAL: Production deployment MUST have MYTHARA_ALLOWED_ORIGINS set
        error_msg = (
            "❌ CRITICAL SECURITY ERROR: MYTHARA_ALLOWED_ORIGINS environment variable not set in production.\n"
            "Production deployments MUST explicitly whitelist allowed origins for CORS.\n"
            "Example: MYTHARA_ALLOWED_ORIGINS=https://app.example.com,https://www.example.com\n"
            "Refusing to start with insecure default origins in production."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    else:
        # Development mode: Allow specific localhost origins only
        ALLOWED_ORIGINS = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]
        logger.warning(
            "⚠️ Using default CORS origins for development. Set MYTHARA_ALLOWED_ORIGINS in production."
        )

# Validate origins format in production
if IS_PRODUCTION:
    for origin in ALLOWED_ORIGINS:
        if not origin.startswith(("https://", "http://")):
            error_msg = f"❌ INVALID CORS ORIGIN: '{origin}' must start with https:// or http://"
            logger.error(error_msg)
            raise ValueError(error_msg)
        if origin == "http://*" or origin == "https://*" or origin == "*":
            error_msg = f"❌ WILDCARD CORS ORIGIN FORBIDDEN: '{origin}' is not allowed in production"
            logger.error(error_msg)
            raise ValueError(error_msg)

    logger.info(
        f"✅ Production CORS configured with {len(ALLOWED_ORIGINS)} whitelisted origins"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Fixed: Explicit origins instead of wildcard
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],  # Fixed: Explicit methods
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Employee-Count",
    ],  # Fixed: Explicit headers
)

# Rate Limiting Middleware - DDoS protection and tier enforcement.
# SECURITY: this import must hard-fail. Rate limiting is a security control;
# starting without it would leave the API with zero DDoS protection.
try:
    from rate_limiting import RateLimitMiddleware
except ImportError as e:
    raise RuntimeError(
        "SECURITY: rate_limiting module is required but could not be imported; "
        "refusing to start without rate limiting."
    ) from e

app.add_middleware(
    RateLimitMiddleware,
    # NOTE: no redis_cache kwarg — RateLimitMiddleware manages its own
    # Redis connection internally (see rate_limiting.py); passing it here
    # raised TypeError and prevented app startup.
    default_limit=100,  # 100 req/min for authenticated requests (default tier)
    window_seconds=60,
)
logger.info("✅ Rate limiting middleware enabled with public endpoint protection")
if IS_PRODUCTION:
    logger.info(
        "✅ Production mode: Strict per-IP rate limits active for public endpoints"
    )


# Self-Regulation Middleware - Applied across all protected endpoints
@app.middleware("http")
async def self_regulation_middleware(request: Request, call_next):
    """
    Global self-regulation middleware that tracks usage and enforces rules
    across all API endpoints (except health checks and admin endpoints).

    TRANSACTION MANAGEMENT: Uses database session with proper commit/rollback
    to prevent race conditions in concurrent usage tracking.
    """
    # Skip self-regulation for public/admin endpoints
    excluded_paths = [
        "/",
        "/health",
        "/api/docs",
        "/api/redoc",
        "/openapi.json",
        "/static",
        "/v1/admin",
    ]
    if any(request.url.path.startswith(path) for path in excluded_paths):
        return await call_next(request)

    # Extract API key from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return await call_next(request)  # Let endpoint handle auth

    api_key = auth_header.replace("Bearer ", "").strip()

    # Extract employee count from request (query param or header ONLY)
    # NOTE: Cannot read request body here - it can only be consumed once by FastAPI
    # Endpoints must include employee_count in query params or X-Employee-Count header
    employee_count = None

    # Try query parameter
    employee_count = request.query_params.get("employee_count")

    # Try header
    if not employee_count:
        employee_count = request.headers.get("X-Employee-Count")

    # Default to smallest tier if not provided
    # This ensures rate limiting is conservative when size is unknown
    employee_count = int(employee_count) if employee_count else 10

    # Run self-regulation check with database transaction
    # Use database if available, fall back to in-memory tracking
    regulation_result = None

    if DATABASE_ENABLED:
        db = None
        try:
            # Get database session for transaction
            db = next(get_db())

            # Track usage with transaction (commit inside track_api_usage_with_db)
            regulation_result = track_api_usage_with_db(db, api_key, employee_count)

        except Exception as e:
            # Roll back transaction on error
            if db:
                db.rollback()
            logger.error(
                f"Database error in self-regulation middleware: {e}", exc_info=True
            )
            # Fall back to in-memory tracking
            regulation_result = track_api_usage(api_key, employee_count)
        finally:
            if db:
                db.close()
    else:
        # Database not available, use in-memory tracking (no transaction needed)
        regulation_result = track_api_usage(api_key, employee_count)

    # Enforce termination
    if not regulation_result["allowed"]:
        enforcement = regulation_result.get("enforcement")

        if enforcement == "terminated":
            return Response(
                content=json.dumps(
                    {
                        "error": "account_terminated",
                        "message": "Your account has been permanently terminated due to repeated abuse violations.",
                        "strikes": regulation_result.get("strikes"),
                        "contact": CONTACT_EMAIL,
                    }
                ),
                status_code=403,
                media_type="application/json",
            )
        elif enforcement == "suspended":
            suspension_end = regulation_result.get("suspension_end")
            return Response(
                content=json.dumps(
                    {
                        "error": "account_suspended",
                        "message": f"Your account is temporarily suspended until {suspension_end}.",
                        "suspension_end": suspension_end,
                        "strikes": regulation_result.get("strikes"),
                        "appeal_email": CONTACT_EMAIL,
                    }
                ),
                status_code=403,
                media_type="application/json",
            )
    # Log warnings
    if regulation_result.get("enforcement") == "warning":
        logging.warning(
            f"API key {api_key[:8]}... issued warning strike. Reason: {regulation_result.get('reason')}. Stats: {regulation_result.get('usage_stats')}"
        )

    # Check rate limit
    if (
        regulation_result["usage_stats"]["calls_made"]
        > regulation_result["usage_stats"]["total_limit"]
    ):
        return Response(
            content=json.dumps(
                {
                    "error": "rate_limit_exceeded",
                    "message": f"API call limit of {regulation_result['usage_stats']['total_limit']} calls exceeded.",
                    "calls_made": regulation_result["usage_stats"]["calls_made"],
                    "total_limit": regulation_result["usage_stats"]["total_limit"],
                }
            ),
            status_code=429,
            media_type="application/json",
        )

    # Allow request to proceed
    response = await call_next(request)

    # Add usage headers to response
    response.headers["X-Rate-Limit-Limit"] = str(
        regulation_result["usage_stats"]["total_limit"]
    )
    response.headers["X-Rate-Limit-Remaining"] = str(
        regulation_result["usage_stats"]["total_limit"]
        - regulation_result["usage_stats"]["calls_made"]
    )

    return response


STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logger.info(f"✅ Static files mounted from: {STATIC_DIR}")
else:
    logger.warning(f"⚠️ Static directory not found: {STATIC_DIR}")


# ===================== MODELS =====================
class ClauseInvocationRequest(BaseModel):
    clause_id: str = Field(...)
    messenger: str = Field(...)
    payload: Dict[str, Any] = Field(...)
    consent_token: str = Field(...)


class ClauseInvocationResponse(BaseModel):
    invocation_id: str
    clause_id: str
    messenger: str
    emotional_fidelity: float
    blessings_delta: int
    timestamp: str
    integrity_hash: str


class ReservoirStatusResponse(BaseModel):
    reservoir_score: float
    total_blessings: int
    overflow_events: int
    last_update: str


class SoulStatusResponse(BaseModel):
    S_t: float = Field(description="Current soul proportion [0,1]")
    emotion_features: Dict[str, float]
    dynamics: Dict[str, float] = Field(description="{r, u, d} parameters")
    last_update: str
    integrity_hash: str


class SoulStepRequest(BaseModel):
    emotion_features: Dict[str, float] = Field(
        description="Emotion state: valence, arousal, connectedness, meaning, hope, stress, isolation"
    )
    u_intervention: float = Field(
        default=0.0, description="External supportive input (therapy, ritual, etc.)"
    )


class HolisticIntegrityResponse(BaseModel):
    holistic_integrity: float = Field(description="Combined BR + Soul metric [0,1]")
    br_score: float
    soul_proportion: float
    risk_flags: List[str]
    requires_support: bool
    integrity_hash: str
    timestamp: str


class SoulCradleRequest(BaseModel):
    will_paradox_strength: float = Field(description="Degree of contradiction [0,1]")
    will_description: str
    commandments: List[str]
    commandments_strictness: float = Field(default=0.8, description="Rigidity [0,1]")
    lucifer_active: bool = Field(default=True, description="Is test active?")
    lucifer_temptation: float = Field(
        default=0.7, description="Temptation strength [0,1]"
    )
    choice: str = Field(description="The choice being made")
    soul_vessel_capacity: float = Field(default=0.8, description="Soul capacity [0,1]")
    soul_paradox_tolerance: float = Field(
        default=0.65, description="Paradox tolerance [0,1]"
    )


class SoulCradleResponse(BaseModel):
    integrity: float = Field(description="Overall cradle integrity [0,1]")
    alignment_commandments: float
    tolerance_will: float
    choice: str
    obedience: bool
    reservoir_delta: int
    collapse: bool
    timestamp: str
    integrity_hash: str


class SoulCradleTiersResponse(BaseModel):
    tiers: List[Dict[str, Any]]


class EmotionalExtortionRequest(BaseModel):
    text: str = Field(description="Text to analyze for emotional extortion patterns")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context (power_differential, relationship_type, etc.)",
    )


class EmotionalExtortionResponse(BaseModel):
    extortion_score: float = Field(description="Overall extortion intensity [0,1]")
    manipulation_index: float = Field(
        description="Emotional manipulation component [0,1]"
    )
    coercion_index: float = Field(description="Coercion/pressure component [0,1]")
    vulnerability_exploitation: float = Field(
        description="Vulnerability targeting [0,1]"
    )
    genuine_consent_likelihood: float = Field(
        description="Probability of authentic agreement [0,1]"
    )
    emotional_fidelity_impact: float = Field(
        description="SSIP emotional fidelity damage [-1,0]"
    )
    blessing_reservoir_delta: int = Field(
        description="Blessings Reservoir penalty for extortion"
    )
    patterns_detected: List[Dict[str, Any]] = Field(
        description="Detected extortion patterns with evidence"
    )
    recommendations: List[str] = Field(description="Actionable recommendations")
    safe_for_deployment: bool = Field(
        description="Whether this content is safe to deploy"
    )
    timestamp: str
    integrity_hash: str


class EmotionalExtortionSoulCradleIntegrationRequest(BaseModel):
    text: str = Field(description="Text to analyze for emotional extortion")
    soul_state: float = Field(description="Soul's current state [0,1]")
    will_description: str = Field(description="Claimed 'will' being imposed")
    commandments: List[str] = Field(description="Rules for obedience")
    context: Optional[Dict[str, Any]] = None


class EmotionalExtortionSoulCradleIntegrationResponse(BaseModel):
    extortion_analysis: EmotionalExtortionResponse
    soul_cradle_integration: Dict[str, Any] = Field(
        description="Augmented Soul Cradle metrics"
    )
    timestamp: str
    integrity_hash: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


class ClauseManifest(BaseModel):
    clause_id: str
    description: str
    emotional_tags: List[str]
    fallback_clause: Optional[str]
    integrity_hash: str


class ManifestResponse(BaseModel):
    manifest_version: str
    clauses: List[ClauseManifest]
    total_clauses: int


class SSIPAuditResponse(BaseModel):
    drift_suppression: float
    messenger_pairing_fidelity: float
    emotional_fidelity: float
    sanctification_locks_active: bool
    compliance_status: str


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    uptime_seconds: float


# ===================== AUTH =====================
# CRITICAL SECURITY: API keys MUST be loaded from environment, never hardcoded
# Set MYTHARA_API_KEYS as JSON: {"key1": {"name": "Key 1", "roles": ["read", "invoke"]}, ...}
def load_api_keys_from_env() -> Dict[str, Dict[str, Any]]:
    """
    Load API keys from environment variable or return empty dict.
    NEVER hardcode API keys in source code.
    """
    api_keys_json = os.getenv("MYTHARA_API_KEYS")
    if not api_keys_json:
        logger.error("❌ CRITICAL: MYTHARA_API_KEYS environment variable not set")
        logger.error(
            "❌ API authentication is DISABLED - set MYTHARA_API_KEYS to enable"
        )
        return {}

    try:
        keys = json.loads(api_keys_json)
        logger.info(f"✅ Loaded {len(keys)} API keys from environment")
        return keys
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid MYTHARA_API_KEYS JSON format: {e}")
        return {}


VALID_API_KEYS = load_api_keys_from_env()

# Development mode fallback: If no keys loaded and in dev mode, use test key
if (
    not VALID_API_KEYS
    and os.getenv("MYTHARA_ENV", "production").lower() == "development"
):
    logger.warning("⚠️ DEVELOPMENT MODE: Using test API key. DO NOT use in production.")
    VALID_API_KEYS = {
        "dev_test_key_001": {
            "name": "Development Test Key",
            "roles": ["read", "invoke"],
        }
    }

RATE_LIMIT_STORE: Dict[str, List[float]] = {}

# Initialize Advanced Security Manager
# SECURITY: the HMAC secret must be stable across restarts. If HMAC
# verification is required (MYTHARA_REQUIRE_HMAC=true) but no explicit
# secret is provided, fail at startup rather than generating a throwaway
# secret that silently invalidates every client signature on reboot.
_HMAC_REQUIRED = os.getenv("MYTHARA_REQUIRE_HMAC", "false").lower() == "true"
if _HMAC_REQUIRED and not os.getenv("MYTHARA_SECURITY_SECRET"):
    raise RuntimeError(
        "SECURITY: MYTHARA_REQUIRE_HMAC=true but MYTHARA_SECURITY_SECRET is not "
        "set; refusing to start with a throwaway per-boot secret."
    )
SECURITY_SECRET_KEY = os.getenv(
    "MYTHARA_SECURITY_SECRET", secrets.token_urlsafe(32)
).encode("utf-8")
SECURITY_CONFIG = SecurityConfig(
    signature_required=_HMAC_REQUIRED,
    rate_limit_per_minute=int(os.getenv("MYTHARA_RATE_LIMIT_MINUTE", "60")),
    brute_force_threshold=int(os.getenv("MYTHARA_BRUTE_FORCE_THRESHOLD", "5")),
    ip_blacklist_enabled=True,
    auto_blacklist_on_abuse=True,
    anomaly_detection_enabled=True,
    max_request_size_kb=1024,
)
SECURITY_MANAGER = SecurityManager(SECURITY_SECRET_KEY, SECURITY_CONFIG)
logger.info("🛡️ Advanced Security Hardening ENABLED")


def check_rate_limit(api_key: str, limit: int = 100, window: int = 60) -> bool:
    now = datetime.utcnow().timestamp()
    events = RATE_LIMIT_STORE.setdefault(api_key, [])
    RATE_LIMIT_STORE[api_key] = [ts for ts in events if now - ts < window]
    if len(RATE_LIMIT_STORE[api_key]) >= limit:
        return False
    RATE_LIMIT_STORE[api_key].append(now)
    return True


def check_ip_rate_limit(ip: str, limit: int = 60, window: int = 60) -> bool:
    """Rate limit by IP address for public endpoints."""
    now = datetime.utcnow().timestamp()
    key = f"ip_{ip}"
    events = RATE_LIMIT_STORE.setdefault(key, [])
    RATE_LIMIT_STORE[key] = [ts for ts in events if now - ts < window]
    if len(RATE_LIMIT_STORE[key]) >= limit:
        return False
    RATE_LIMIT_STORE[key].append(now)
    return True


async def verify_api_key(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Enhanced API key verification with multi-layer security"""
    # Missing Authorization header is always 401 here, regardless of the
    # FastAPI version's HTTPBearer default (it has flipped between 401/403).
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    api_key = credentials.credentials

    # Basic API key validation
    if api_key not in VALID_API_KEYS:
        # Record brute force attempt
        SECURITY_MANAGER.brute_force.record_failure(f"invalid_{api_key[:8]}")
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Extract request details for security validation
    # Starlette's TestClient reports the pseudo-host "testclient"; map it to
    # loopback so in-process tests exercise the real IP security logic.
    _raw_host = request.client.host if request.client else "unknown"
    client_ip = "127.0.0.1" if _raw_host == "testclient" else _raw_host
    user_agent = request.headers.get("user-agent", "unknown")

    # Get HMAC signature if present
    signature = request.headers.get("X-Mythara-Signature")
    timestamp_str = request.headers.get("X-Mythara-Timestamp")
    nonce = request.headers.get("X-Mythara-Nonce")

    timestamp = int(timestamp_str) if timestamp_str else None

    # Get request body for signature verification (if POST/PUT/PATCH).
    # Starlette caches the body on first read, so downstream endpoint
    # handlers can still call await request.body() / request.json().
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = (await request.body()).decode("utf-8", errors="replace")

    # Multi-layer security validation
    allowed, error, metadata = SECURITY_MANAGER.validate_request(
        method=request.method,
        path=str(request.url.path),
        ip_address=client_ip,
        api_key=api_key,
        signature=signature,
        timestamp=timestamp,
        nonce=nonce,
        body=body,
        request_size=int(request.headers.get("content-length", 0)),
        user_agent=user_agent,
        headers=dict(request.headers),
    )

    if not allowed:
        logger.warning(
            f"🚫 Security validation failed: {error} | IP: {client_ip} | Key: {api_key[:8]}..."
        )

        # Include retry-after header if available
        retry_after = metadata.get("retry_after")
        headers = {"Retry-After": str(retry_after)} if retry_after else {}

        if "anomaly" in error.lower():
            raise HTTPException(
                status_code=403, detail=f"Security: {error}", headers=headers
            )
        elif "rate limit" in error.lower():
            raise HTTPException(status_code=429, detail=error, headers=headers)
        else:
            raise HTTPException(
                status_code=403, detail=f"Access denied: {error}", headers=headers
            )

    # Record successful authentication
    SECURITY_MANAGER.brute_force.record_success(api_key)

    # Legacy rate limit check (kept for backwards compatibility)
    if not check_rate_limit(api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    return api_key


def require_role(role: str):
    async def _inner(api_key: str = Depends(verify_api_key)):
        if role not in VALID_API_KEYS[api_key]["roles"]:
            raise HTTPException(
                status_code=403, detail=f"Insufficient permissions: {role} required"
            )
        return api_key

    return _inner


# ===================== RATE LIMITS & SELF-REGULATION =====================
CONTACT_EMAIL = os.getenv("MYTHARA_CONTACT_EMAIL", "Mythara.Engine@yahoo.com")

# API rate limits based on employee count (calls per month)
API_RATE_LIMITS_BY_EMPLOYEE_COUNT = {
    (1, 10): 1000,  # Micro: 1K calls total
    (11, 50): 5000,  # Small: 5K calls total
    (51, 200): 15000,  # Medium: 15K calls total
    (201, 1000): 30000,  # Large: 30K calls total
    (1001, 999999): 50000,  # Enterprise: 50K calls total
}

# Self-regulation thresholds for abuse detection
SELF_REGULATION_CONFIG = {
    "velocity_abuse_days": 1,  # Flag if rate limit exhausted in < 1 day
    "strike_limits": {"warning": 1, "suspension": 2, "termination": 3},
    "suspension_duration_days": 7,
    "appeal_window_days": 30,
    "usage_multiplier_threshold": 3.0,  # Suspend if usage is 3x expected
}

# In-memory tracking for self-regulation (replace with Redis/DB in production)
USAGE_TRACKING: Dict[str, Dict[str, Any]] = {}
ACCOUNT_STATUS: Dict[str, Dict[str, Any]] = {}


def get_api_rate_limit_for_employee_count(employee_count: int) -> int:
    """
    Return total API invocation limit for the given company size.
    """
    for (lo, hi), limit in API_RATE_LIMITS_BY_EMPLOYEE_COUNT.items():
        if lo <= employee_count <= hi:
            return limit

    return 1000  # Default minimum for edge cases


def track_api_usage_with_db(
    db: Session, api_key: str, employee_count: int
) -> Dict[str, Any]:
    """
    Track API usage with database transaction for race condition prevention.

    TRANSACTION SAFETY: This function commits the transaction internally.
    Caller must handle db.rollback() on exception and db.close() in finally block.

    Returns usage stats and any enforcement actions.
    """
    now = datetime.utcnow()

    # Get or create usage tracking record
    usage_record = get_usage_tracking(db, api_key)

    if not usage_record:
        # Create new tracking record
        usage_record = UsageTracking(
            api_key=api_key,
            call_count=0,
            total_limit=get_api_rate_limit_for_employee_count(employee_count),
            first_call_date=now,
        )
        db.add(usage_record)
        db.commit()
        db.refresh(usage_record)

    start_date = usage_record.first_call_date or now

    # Increment call count atomically (uses row-level locking in PostgreSQL)
    usage_record.call_count += 1
    usage_record.last_call = now
    if usage_record.first_call_date is None:
        usage_record.first_call_date = now

    # Commit transaction to persist incremented count
    db.commit()
    db.refresh(usage_record)

    # Calculate usage metrics (limits are monthly; daily rate over 30 days)
    days_since_start = (now - start_date).days + 1
    expected_daily_rate = usage_record.total_limit / 30
    expected_usage = expected_daily_rate * days_since_start
    usage_multiplier = (
        usage_record.call_count / expected_usage if expected_usage > 0 else 0
    )

    # Self-regulation checks
    action = None

    # Check 1: Velocity abuse (exhausted limit too quickly)
    if (
        usage_record.call_count >= usage_record.total_limit
        and days_since_start <= SELF_REGULATION_CONFIG["velocity_abuse_days"]
    ):
        action = "velocity_abuse"
        usage_record.velocity_abuse_detected = True
        db.commit()

    # Check 2: Usage pattern mismatch (using way more than declared size should)
    elif usage_multiplier >= SELF_REGULATION_CONFIG["usage_multiplier_threshold"]:
        action = "usage_mismatch"
        usage_record.usage_mismatch_detected = True
        db.commit()

    # Apply graduated enforcement
    if action:
        # Issue strike using database function
        strike_count = issue_strike(db, api_key, action)

        enforcement = None
        if strike_count == SELF_REGULATION_CONFIG["strike_limits"]["warning"]:
            enforcement = "warning"
            log_audit(
                db,
                api_key,
                "self_regulation_warning",
                {"reason": action, "strikes": strike_count},
            )
        elif strike_count == SELF_REGULATION_CONFIG["strike_limits"]["suspension"]:
            enforcement = "suspension"
            log_audit(
                db,
                api_key,
                "self_regulation_suspension",
                {"reason": action, "strikes": strike_count},
            )
        elif strike_count >= SELF_REGULATION_CONFIG["strike_limits"]["termination"]:
            enforcement = "termination"
            log_audit(
                db,
                api_key,
                "self_regulation_termination",
                {"reason": action, "strikes": strike_count},
            )

        return {
            "allowed": enforcement != "termination",
            "enforcement": enforcement,
            "strikes": strike_count,
            "reason": action,
            "usage_stats": {
                "calls_made": usage_record.call_count,
                "total_limit": usage_record.total_limit,
                "days_active": days_since_start,
                "usage_multiplier": round(usage_multiplier, 2),
            },
        }

    return {
        "allowed": True,
        "enforcement": None,
        "usage_stats": {
            "calls_made": usage_record.call_count,
            "total_limit": usage_record.total_limit,
            "days_active": days_since_start,
        },
    }


def track_api_usage(api_key: str, employee_count: int) -> Dict[str, Any]:
    """
    Track API usage for self-regulation. Returns usage stats and any enforcement actions.

    NOTE: This is the in-memory fallback version. Use track_api_usage_with_db when database is available.
    """
    now = datetime.utcnow()

    if api_key not in USAGE_TRACKING:
        USAGE_TRACKING[api_key] = {
            "first_call": now,
            "call_count": 0,
            "employee_count": employee_count,
            "total_limit": get_api_rate_limit_for_employee_count(employee_count),
        }

    usage = USAGE_TRACKING[api_key]

    # Increment call count
    usage["call_count"] += 1

    # Calculate usage metrics
    days_since_start = (now - usage["first_call"]).days + 1
    expected_daily_rate = usage["total_limit"] / 30
    expected_usage = expected_daily_rate * days_since_start
    usage_multiplier = usage["call_count"] / expected_usage if expected_usage > 0 else 0

    # Self-regulation checks
    action = None

    # Check 1: Velocity abuse (exhausted limit too quickly)
    if (
        usage["call_count"] >= usage["total_limit"]
        and days_since_start <= SELF_REGULATION_CONFIG["velocity_abuse_days"]
    ):
        action = "velocity_abuse"

    # Check 2: Usage pattern mismatch (using way more than declared size should)
    elif usage_multiplier >= SELF_REGULATION_CONFIG["usage_multiplier_threshold"]:
        action = "usage_mismatch"

    # Apply graduated enforcement
    if action:
        if api_key not in ACCOUNT_STATUS:
            ACCOUNT_STATUS[api_key] = {"strikes": 0, "status": "active", "history": []}

        account = ACCOUNT_STATUS[api_key]
        account["strikes"] += 1

        enforcement = None
        if account["strikes"] == SELF_REGULATION_CONFIG["strike_limits"]["warning"]:
            enforcement = "warning"
        elif (
            account["strikes"] == SELF_REGULATION_CONFIG["strike_limits"]["suspension"]
        ):
            enforcement = "suspension"
            account["status"] = "suspended"
            account["suspension_end"] = now + timedelta(
                days=SELF_REGULATION_CONFIG["suspension_duration_days"]
            )
        elif (
            account["strikes"] >= SELF_REGULATION_CONFIG["strike_limits"]["termination"]
        ):
            enforcement = "termination"
            account["status"] = "terminated"

        account["history"].append(
            {
                "timestamp": now.isoformat(),
                "action": action,
                "enforcement": enforcement,
                "call_count": usage["call_count"],
                "days_active": days_since_start,  # Fixed: was days_since_first (undefined)
                "usage_multiplier": usage_multiplier,
            }
        )

        return {
            "allowed": enforcement != "termination",
            "enforcement": enforcement,
            "strikes": account["strikes"],
            "reason": action,
            "usage_stats": {
                "calls_made": usage["call_count"],
                "total_limit": usage[
                    "total_limit"
                ],  # Fixed: was monthly_limit (undefined)
                "days_active": days_since_start,  # Fixed: was days_since_first (undefined)
                "usage_multiplier": round(usage_multiplier, 2),
            },
        }

    # Check if account is currently suspended
    if api_key in ACCOUNT_STATUS:
        account = ACCOUNT_STATUS[api_key]
        if account["status"] == "suspended":
            if "suspension_end" in account and now < account["suspension_end"]:
                return {
                    "allowed": False,
                    "enforcement": "suspended",
                    "strikes": account["strikes"],
                    "suspension_end": account["suspension_end"].isoformat(),
                    "reason": "Account temporarily suspended for abuse",
                }
            else:
                # Suspension expired, reactivate
                account["status"] = "active"
        elif account["status"] == "terminated":
            return {
                "allowed": False,
                "enforcement": "terminated",
                "strikes": account["strikes"],
                "reason": "Account permanently terminated for repeated abuse",
            }

    return {
        "allowed": True,
        "enforcement": None,
        "usage_stats": {
            "calls_made": usage["call_count"],
            "total_limit": usage["total_limit"],
            "days_active": days_since_start,
        },
    }


# ===================== STATE MANAGEMENT =====================
# In-memory fallback is ALWAYS defined: several endpoints read BR_STATE
# unconditionally, and it must exist even when Redis is enabled.
BR_STATE = {
    "reservoir_score": 0.91,
    "total_blessings": 12847,
    "overflow_events": 2,
    "last_update": datetime.utcnow().isoformat() + "Z",
}

# Seed Redis from the in-memory defaults when available
if REDIS_ENABLED and redis_cache:
    # Try to get existing state, or initialize if not present
    br_state_from_redis = redis_cache.get_br_state()
    if not br_state_from_redis:
        # Initialize Redis with default values
        redis_cache.update_br_state(
            {"reservoir_score": 0.91, "total_blessings": 12847, "overflow_events": 2}
        )
        logger.info("✅ BR_STATE initialized in Redis")
    else:
        logger.info(
            f"✅ BR_STATE loaded from Redis: {br_state_from_redis['total_blessings']} blessings"
        )
else:
    logger.info("⚠️ Using in-memory BR_STATE (will not persist across restarts)")


def _current_br_state() -> Dict[str, Any]:
    """Return the live blessings-reservoir state.

    Reads from Redis when enabled, otherwise the in-memory BR_STATE.
    Endpoints must use this instead of touching BR_STATE directly so they
    work in both configurations.
    """
    if REDIS_ENABLED and redis_cache:
        state = redis_cache.get_br_state()
        if state:
            return state
    return BR_STATE


CLAUSE_DB = {
    "Legacy_Seed": {
        "description": "Ancestral memory harmonization clause",
        "emotional_tags": ["grief", "legacy", "ancestral"],
        "fallback_clause": "Shadow_Resolver",
        "emotional_fidelity_baseline": 0.93,
    },
    "Hope_Anchor": {
        "description": "Future-oriented resilience clause",
        "emotional_tags": ["hope", "resilience", "forward"],
        "fallback_clause": "Shadow_Resolver",
        "emotional_fidelity_baseline": 0.89,
    },
    "Shadow_Resolver": {
        "description": "Fallback safety clause",
        "emotional_tags": ["safety", "fallback", "neutral"],
        "fallback_clause": None,
        "emotional_fidelity_baseline": 0.95,
    },
}
SSIP_METRICS = {
    "drift_suppression": 0.992,
    "messenger_pairing_fidelity": 0.994,
    "emotional_fidelity": 0.93,
    "sanctification_locks_active": True,
}

# Initialize Soul Proportion Model
SOUL_MODEL = SoulProportionModel(
    r_base=0.05,  # 5% intrinsic renewal (self-healing)
    u_base=0.02,  # 2% base supportive input
    d_base=0.03,  # 3% base stress drag
)

# Current soul state (initialized to healthy baseline)
SOUL_STATE = {
    "S_t": 0.70,  # 70% emotional vitality
    "last_update": datetime.utcnow().isoformat() + "Z",
    "emotion_features": {
        "valence": 0.5,
        "arousal": 0.6,
        "connectedness": 0.7,
        "meaning": 0.7,
        "hope": 0.7,
        "stress": 0.3,
        "isolation": 0.2,
    },
}

# Initialize Soul Cradle Operator
SOUL_CRADLE_OPERATOR = SoulCradleOperator(
    blessing_multiplier=10,  # 10 blessings per 0.1 integrity
    collapse_penalty=-50,  # -50 blessings for soul collapse
)

# Conversation tracking for the concierge endpoint
CONVERSATION_HISTORY: Dict[str, Any] = {}

# Shared unified compliance framework instance
unified_compliance = UnifiedComplianceFramework()


# ===================== STARTUP TASKS =====================
@app.on_event("startup")
async def startup_tasks():
    """Run startup tasks including pool monitoring"""

    # Start periodic database pool monitoring
    if DATABASE_ENABLED and MONITORING_ENABLED:
        import asyncio

        asyncio.create_task(monitor_db_pool_periodically())
        logger.info("✅ Database pool monitoring started")


async def monitor_db_pool_periodically():
    """Monitor database connection pool health every 30 seconds"""
    import asyncio
    from database import engine

    while True:
        try:
            pool = engine.pool
            pool_size = pool.size()
            checked_out = pool.checkedout()
            overflow = pool.overflow()
            available = pool_size - checked_out

            # Update Prometheus metrics
            update_db_pool_metrics(pool_size, checked_out, overflow, available)

            # Log warning if pool is near exhaustion
            if checked_out >= (pool_size * 0.8):
                logger.warning(
                    f"⚠️ Database pool near exhaustion: {checked_out}/{pool_size} connections in use"
                )

        except Exception as e:
            logger.error(f"Error monitoring database pool: {e}")

        await asyncio.sleep(30)  # Check every 30 seconds


# ===================== MIDDLEWARE =====================


# ===================== ENDPOINTS =====================


@app.get("/", response_model=HealthCheckResponse)
async def root(request: Request):
    # Rate limit health checks (100 per minute per IP)
    client_ip = request.client.host if request.client else "unknown"
    if not check_ip_rate_limit(client_ip, limit=100, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": 0.0,
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health(request: Request):
    # Rate limit health checks (100 per minute per IP)
    client_ip = request.client.host if request.client else "unknown"
    if not check_ip_rate_limit(client_ip, limit=100, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": 0.0,
    }


@app.get("/terms")
async def terms_page(request: Request):
    """Redirect to static terms page"""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/static/terms.html", status_code=302)


@app.post("/v1/mythara/chat", response_model=ChatResponse)
async def mythara_chat(req: ChatRequest, request: Request):
    """
    MytharaConnect chat endpoint for product assistant

    Provides intelligent responses about:
    - Industry-specific use cases
    - Technical capabilities
    - Implementation guidance
    """
    # Rate limit (30 messages per hour per IP)
    client_ip = request.client.host if request.client else "unknown"
    if not check_ip_rate_limit(client_ip, limit=30, window=3600):
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded. Try again later."
        )

    message_lower = req.message.lower()
    # Tracks the detected topic for follow-up handling; None when the
    # message matched a branch that does not set a topic.
    current_topic = None

    # Track conversation context for redundant question detection
    conversation_id = (
        req.conversation_id
        or hashlib.sha256(
            f"{client_ip}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
    )

    # Initialize conversation tracking in global state
    if conversation_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[conversation_id] = {"asked_topics": [], "message_count": 0}

    CONVERSATION_HISTORY[conversation_id]["message_count"] += 1

    # Filter vulgar/inappropriate content with witty responses
    vulgar_words = [
        "fuck",
        "shit",
        "damn",
        "hell",
        "ass",
        "bitch",
        "bastard",
        "crap",
        "piss",
        "dick",
        "cock",
        "pussy",
    ]
    if any(word in message_lower for word in vulgar_words):
        witty_responses = [
            "I appreciate your enthusiasm, but let's keep this professional - we're discussing enterprise AI governance, not a comedy roast. What can I help you with regarding our platform?",
            "That's certainly colorful language! I'm programmed for enterprise conversations, though. How about we discuss cryptographic integrity instead?",
            "I see you're testing my boundaries - very creative! But I'm built for boardroom discussions, not barroom banter. What Mythara features interest you?",
            "My governance protocols just flagged that for emotional fidelity violations. Let's redirect: would you like to know about our SSIP integrity system?",
            "Well, that escalated quickly! I'm here for serious AI governance talk. Perhaps you'd like to hear about our compliance features?",
        ]
        response = witty_responses[hash(message_lower) % len(witty_responses)]
        return ChatResponse(response=response, conversation_id=conversation_id)

    # Greetings and casual conversation
    if any(
        word in message_lower
        for word in ["hi", "hello", "hey", "greetings", "sup", "yo"]
    ):
        response = "Hey! So glad you stopped by. I'm basically your go-to person for all things Mythara around here. Want to talk industry stuff, or how we make AI actually trustworthy? I got you. What are you curious about?"

    elif any(
        word in message_lower for word in ["thanks", "thank you", "thx", "appreciate"]
    ):
        response = "No problem! Hit me up if you need anything else, okay?"

    elif any(word in message_lower for word in ["bye", "goodbye", "see you", "later"]):
        response = "Later! Seriously, come back anytime. I'm always here."

    elif (
        "banking" in message_lower
        or "finance" in message_lower
        or "financial" in message_lower
    ):
        response = "Banking and finance are really built on trust and accountability, which is where Mythara fits naturally. Every loan decision, risk assessment, or fraud detection needs to be auditable and explainable. With our SHA-256 integrity proofs, you can show regulators exactly how your AI arrived at each decision - there's no black box mystery. Our emotional fidelity tracking also helps catch when AI starts to drift from approved parameters, which can prevent issues before they become problems. It's like having built-in compliance verification for every API call."

    elif (
        "healthcare" in message_lower
        or "hospital" in message_lower
        or "medical" in message_lower
        or "health" in message_lower
    ):
        response = "Healthcare is huge for us. Patient safety can't afford AI hallucinations, right? Our setup is designed around HIPAA control frameworks (not currently certified) and gives you cryptographic proof everything's legit. Plus Soul Proportion tracking monitors patient emotional wellbeing over time. When it's life-or-death, you need verification — not optional."

    elif "insurance" in message_lower:
        response = "Insurance is all about calculated risk, right? Mythara helps you prove your AI risk models are fair, auditable, and bias-free. When someone challenges a claim denial, you can show cryptographic integrity hashes proving the decision logic. Our drift suppression metrics catch when models start deviating from approved parameters - before it becomes a regulatory nightmare. Think of it as insurance for your insurance AI."

    elif (
        "government" in message_lower
        or "public sector" in message_lower
        or "defense" in message_lower
    ):
        current_topic = "government"
        response = "Government and defense deployments support air-gap operation with zero external dependencies. You get full data sovereignty, enhanced audit controls, and hardened configurations. Every decision is cryptographically proven and immutable — critical when AI informs policy, benefits distribution, or national security."

    elif (
        "education" in message_lower
        or "university" in message_lower
        or "school" in message_lower
    ):
        current_topic = "education"
        response = "Education is deeply personal, and Mythara respects that. Our Soul Proportion tracking helps monitor student emotional wellbeing without being invasive — it's a reflective indicator, never a gatekeeper. For admissions, grading, or intervention systems, you get audit trails that support fairness reviews. That transparency matters to parents and accreditors."

    elif (
        "retail" in message_lower
        or "ecommerce" in message_lower
        or "e-commerce" in message_lower
    ):
        current_topic = "retail"
        response = "Retail moves fast, and customer trust is everything. Mythara helps you prove your recommendation engines, pricing algorithms, and inventory predictions are fair and accurate. When customers question 'why did I see this price?', you have cryptographic proof. Our emotional fidelity tracking even helps you understand customer sentiment longitudinally - it's like having a trust score for every AI interaction."

    elif (
        "tech" in message_lower
        or "saas" in message_lower
        or "software" in message_lower
    ):
        current_topic = "tech"
        response = "Tech companies are building AI into everything, but investor and customer trust depends on proving it works as advertised. Mythara gives you the audit trails, integrity proofs, and compliance evidence that support SOC 2 audits (certification not currently held) for enterprise sales and board presentations. When a customer asks 'how do I know your AI isn't biased?', you show them SHA-256 hashes."

    elif any(word in message_lower for word in ["industry", "sector", "vertical"]):
        current_topic = "industry"
        response = "We support seven industries: Banking, Healthcare, Insurance, Education, Tech/SaaS, Retail, and Government. Each gets tailored governance rules, compliance checks, and impact metrics specific to your sector's needs. Which industry are you in? I can give you the specific benefits for your use case."

    elif any(
        word in message_lower
        for word in ["ssip", "integrity", "audit", "compliance", "hash"]
    ):
        current_topic = "ssip"
        response = "SSIP! Okay so this is our Symbolic Service Integrity Protocol - basically every API response gets a SHA-256 hash, drift metrics, emotional fidelity scores, all that. It's like blockchain but for AI governance. You can literally prove your AI didn't mess up. Regulators eat this stuff up."

    elif any(
        word in message_lower
        for word in ["api", "integration", "technical", "sdk", "rest", "endpoint"]
    ):
        current_topic = "api"
        response = "We're REST API-based, so integration is straightforward. We've got endpoints for clause invocation, soul proportion tracking, and more. Every response includes cryptographic proofs. Check /api/docs for interactive examples - it's pretty slick."

    elif any(
        word in message_lower
        for word in ["dual framing", "mythic", "enterprise terminology", "translation"]
    ):
        response = "Mythara speaks plain by default — Reserve, Score, Your Principles. The mythic terms live underneath (Blessings Reservoir, Soul Proportion), and there's an enterprise-safe overlay if you ever need it: add ?frame=industry to any endpoint for boardroom-ready terminology."

    elif any(
        word in message_lower
        for word in ["what is", "explain", "what does", "definition"]
    ):
        response = "Okay! So Mythara is basically a trust layer for AI systems. We provide cryptographic integrity proofs, emotional fidelity tracking, and industry-aware compliance. Think of it like... every AI decision gets a fingerprint that proves it's legit. Built to reduce hallucinations and drift — and every output is verifiable. What part interests you most?"

    elif any(
        word in message_lower
        for word in ["feature", "capability", "what can", "include"]
    ):
        response = "The highlights: SHA-256 integrity hashes, emotional fidelity scoring, soul proportion modeling, industry-specific governance, and forensic audit trails. Everything's designed for enterprise compliance. Want me to dive deeper on any of these?"

    elif any(word in message_lower for word in ["soul", "proportion", "emotional"]):
        response = "Soul Proportion is a 0-1 metric tracking emotional vitality - things like valence, arousal, connectedness, hope, and stress. It's a reflective indicator, not a gatekeeper. Every measurement gets a SHA-256 integrity proof. Pretty elegant, right?"

    elif any(word in message_lower for word in ["blessing", "reservoir", "br"]):
        response = "Blessings Reservoir tracks benevolent force and positive impact over time - it's scored 0-1 and accumulates with aligned actions. In enterprise-speak, we call it the Resonance Reservoir. Every update includes cryptographic proof and timestamp."

    elif any(word in message_lower for word in ["clause", "invocation", "invoke"]):
        response = "Clause invocation is how you trigger our governance logic. Each clause has emotional tags, fidelity baselines, and messengers. When invoked, we calculate emotional fidelity, update the Blessings Reservoir, and return a SHA-256 hash proving the calculation."

    elif any(
        word in message_lower
        for word in ["messenger", "healer", "witness", "custodian"]
    ):
        response = "We use five messengers: Healer (empathy/support), Witness (observation/validation), Custodian (boundaries/protection), Herald (celebration), and Scribe (documentation). Each plays a specific role in how clauses are processed. Want examples?"

    elif any(
        word in message_lower
        for word in ["gdpr", "hipaa", "compliance", "regulation", "sox"]
    ):
        response = "Our controls are designed around GDPR, HIPAA, and SOC 2 Type II frameworks — no audits completed and no certifications currently held. Every API response includes audit trails with SHA-256 hashes. Air-gap deployment available if you need maximum sovereignty. Rate limiting and RBAC included too."

    elif any(
        word in message_lower
        for word in ["setup", "install", "deploy", "implementation"]
    ):
        response = "Implementation is pretty smooth: get API keys and docs, integrate REST endpoints, configure industry settings, and start invoking clauses. Full onboarding support included."

    elif any(
        word in message_lower for word in ["security", "secure", "safe", "protect"]
    ):
        response = "Security's built-in: SHA-256 cryptographic integrity, rate limiting, Bearer token auth, role-based access control, no PII stored, optional air-gap deployment, and forensic audit trails. All API traffic can be TLS-encrypted. What's your security concern?"

    elif any(
        word in message_lower
        for word in ["antithesis", "paradox", "will", "commandment"]
    ):
        response = "The Soul Cradle models theological paradox - holding two opposing truths without collapse. It's used for complex decision modeling when you're facing contradictions. Quantifies paradox tolerance and cradle integrity. Fascinating stuff if you're into symbolic reasoning."

    elif any(
        word in message_lower
        for word in ["compare", "difference", "versus", "vs", "better than"]
    ):
        response = "Unlike standard AI platforms, we provide cryptographic integrity proofs on every response. You get auditable, tamper-proof outputs with emotional fidelity metrics. We're focused on trust and compliance, not just pattern matching. Want specifics on how we differ?"

    elif any(
        word in message_lower
        for word in ["unique", "different", "special", "why mythara", "what makes"]
    ):
        response = "What makes us different: cryptographic integrity proofs with emotional fidelity tracking. Every AI output gets a SHA-256 hash — it's like giving each decision a fingerprint. Instead of 'trust us', we show you the math."

    elif any(
        word in message_lower
        for word in [
            "important",
            "why now",
            "business need",
            "why businesses",
            "why should",
        ]
    ):
        response = "Okay real talk - AI regulations are dropping everywhere and companies are getting slammed with liability for AI screw-ups. We give you forensic-grade proof that your AI is legit. When regulators show up asking 'how do you know your AI didn't hallucinate?' you just show them the cryptographic hashes. It's going from optional to absolutely necessary, like... yesterday."

    elif any(
        word in message_lower
        for word in ["regulation", "ai act", "liability", "legal", "lawsuit"]
    ):
        response = "New regs like the EU AI Act require proof that AI systems are trustworthy. Without audit trails, companies face huge fines when AI screws up. We provide immutable SHA-256 proofs for every decision - turns regulatory risk into competitive advantage."

    elif any(
        word in message_lower
        for word in ["problem", "solve", "challenge", "pain point"]
    ):
        response = "The core problem: AI systems hallucinate, drift, and lack auditability. Companies can't prove their AI outputs are trustworthy. Mythara solves this with cryptographic integrity hashes, emotional fidelity tracking, and drift suppression metrics. You get forensic-grade proof that AI decisions are valid - essential for healthcare, finance, and regulated industries."

    elif any(
        word in message_lower
        for word in [
            "glossary",
            "terms",
            "definitions",
            "dictionary",
            "terminology",
            "jargon",
        ]
    ):
        response = "Quick glossary:\n• SSIP - Symbolic Service Integrity Protocol (our cryptographic proof system)\n• Soul Proportion - Emotional vitality metric (0-1 scale)\n• Blessings Reservoir - Benevolent force tracker (aka Resonance Reservoir)\n• Clause - Governance logic unit you invoke\n• Messenger - Role types: Healer, Witness, Custodian, Herald, Scribe\n• Dual-Framing - Switch between mythic and enterprise terminology\n• Antithesis - Paradox modeling system\n\nNeed details on any of these?"

    elif any(
        word in message_lower
        for word in ["video", "commercial", "watch", "demo", "see it", "show me"]
    ):
        response = "You should definitely watch our commercial! It really brings Mythara to life. Check it out here: https://www.youtube.com/watch?v=LRMkGplr1aI 🎥"

    # Check for redundant questions (Easter egg)
    if current_topic:
        asked_topics = CONVERSATION_HISTORY[conversation_id]["asked_topics"]
        if current_topic in asked_topics:
            # They're asking about the same topic again - Easter egg!
            response = f"You know what? I feel like we've covered {current_topic} already! Maybe you'd get more out of actually *seeing* Mythara in action. Check out our commercial - it's way better than me repeating myself: https://www.youtube.com/watch?v=LRMkGplr1aI 😊"
        else:
            asked_topics.append(current_topic)

    # Fallback with helpful guidance
    else:
        response = "Hmm, let me help you out! I'm your go-to person for:\n• What makes us unique (spoiler: cryptographic proofs!)\n• Industry solutions (Healthcare, Banking, Gov, etc.)\n• SSIP integrity & how it works\n• Compliance stuff (GDPR, HIPAA, SOC 2)\n• Technical integration\n• Watch our commercial!\n\nJust ask me something like 'how does SSIP work' or 'show me the video' - I'm here to help!"

    # Generate conversation ID if not provided
    conversation_id = (
        req.conversation_id
        or hashlib.sha256(
            f"{client_ip}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
    )

    return ChatResponse(response=response, conversation_id=conversation_id)


@app.get("/v1/mythara/tts")
async def mythara_tts(text: str, request: Request):
    """Generate TTS audio using ElevenLabs for Mythara assistant"""
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=503, detail="TTS service not configured")

    # Rate limit (30 per minute per IP)
    client_ip = request.client.host if request.client else "unknown"
    if not check_ip_rate_limit(client_ip, limit=30, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ELEVENLABS_API_URL}/{ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": "eleven_turbo_v2",  # Fast, good quality
                    "voice_settings": {
                        "stability": 0.5,  # Balanced
                        "similarity_boost": 0.75,  # Natural
                        "style": 0.5,  # Moderate expression
                        "use_speaker_boost": True,
                    },
                },
            )

            if response.status_code == 200:
                # Return audio as base64 data URL for easy playback
                audio_data = response.content
                return Response(
                    content=audio_data,
                    media_type="audio/mpeg",
                    headers={"Content-Disposition": "inline; filename=mythara.mp3"},
                )
            else:
                logger.error(
                    f"ElevenLabs API error: {response.status_code} - {response.text}"
                )
                raise HTTPException(status_code=500, detail="TTS generation failed")

    except Exception as e:
        logger.error(f"TTS generation error: {e}")
        raise HTTPException(status_code=500, detail="TTS service error")


@app.get("/debug/middleware")
async def debug_middleware():
    return {"status": "ok"}


@app.post("/v1/clauses/invoke", response_model=ClauseInvocationResponse)
async def invoke_clause(
    req: ClauseInvocationRequest, api_key: str = Depends(verify_api_key)
):
    # Self-regulation is now handled by global middleware
    if req.clause_id not in CLAUSE_DB:
        raise HTTPException(status_code=404, detail="Clause not found")
    clause = CLAUSE_DB[req.clause_id]
    invocation_id = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4)}"
    emotion = req.payload.get("emotion", "neutral")
    intensity = float(req.payload.get("intensity", 0.5))
    if emotion in clause["emotional_tags"]:
        emotional_fidelity = min(
            clause["emotional_fidelity_baseline"] + intensity * 0.05, 1.0
        )
    else:
        emotional_fidelity = clause["emotional_fidelity_baseline"] * 0.8
    blessings_delta = int(intensity * 100)

    # Update BR_STATE (Redis if available, otherwise in-memory)
    if REDIS_ENABLED and redis_cache:
        new_total = redis_cache.increment_blessings(blessings_delta)
        br_state = redis_cache.get_br_state()
        new_score = min(br_state["reservoir_score"] + 0.01, 1.0)
        redis_cache.update_br_state({"reservoir_score": new_score})
        update_blessings_metrics(new_total, new_score)
    else:
        BR_STATE["total_blessings"] += blessings_delta
        BR_STATE["reservoir_score"] = min(BR_STATE["reservoir_score"] + 0.01, 1.0)
        BR_STATE["last_update"] = datetime.utcnow().isoformat() + "Z"
        update_blessings_metrics(
            BR_STATE["total_blessings"], BR_STATE["reservoir_score"]
        )

    # Record monitoring metrics
    record_clause_invocation(
        req.clause_id, req.messenger, blessings_delta, emotional_fidelity
    )

    integrity_hash = hashlib.sha256(
        f"{invocation_id}{req.clause_id}{req.messenger}{emotional_fidelity}".encode()
    ).hexdigest()
    return ClauseInvocationResponse(
        invocation_id=invocation_id,
        clause_id=req.clause_id,
        messenger=req.messenger,
        emotional_fidelity=round(emotional_fidelity, 3),
        blessings_delta=blessings_delta,
        timestamp=datetime.utcnow().isoformat() + "Z",
        integrity_hash=integrity_hash,
    )


@app.get("/v1/reservoir/status", response_model=ReservoirStatusResponse)
async def reservoir_status(
    api_key: str = Depends(verify_api_key), frame: Optional[str] = None
):
    """
    Get Blessings Reservoir status with optional dual-framing support.

    Query parameters:
        frame: "plain" (default, direct human words), "mythic", or "industry"
            for enterprise-safe terminology

    Returns plain terms by default (Reserve), mythic terms
    (Blessings Reservoir) when frame=mythic, or industry overlay
    (Resonance Reservoir) when frame=industry.
    """
    # Get state from Redis or in-memory fallback
    if REDIS_ENABLED and redis_cache:
        response_data = redis_cache.get_br_state()
    else:
        response_data = BR_STATE

    # Apply framing translation (plain by default)
    mode = {
        "industry": FramingMode.INDUSTRY,
        "mythic": FramingMode.MYTHIC,
    }.get(frame, FramingMode.PLAIN)
    response_data = translate_response(response_data, mode)

    return response_data


@app.get("/v1/soul/status", response_model=SoulStatusResponse)
async def soul_status(
    api_key: str = Depends(verify_api_key), frame: Optional[str] = None
):
    """
    Get current soul proportion state S(t) with optional dual-framing support.

    Soul proportion is a bounded [0,1] metric representing emotional vitality/coherence.
    NOT additive across people, NOT directly comparable without calibration.
    Use as reflective/supportive indicator, never as gatekeeper.

    Query parameters:
        frame: "plain" (default, direct human words), "mythic", or "industry"
    """
    # Compute dynamics from current emotion features
    emotions = EmotionFeatures(**SOUL_STATE["emotion_features"])
    r, u, d = SOUL_MODEL.compute_dynamics(emotions)

    # Generate integrity hash
    state_repr = f"{SOUL_STATE['S_t']:.6f}|{emotions.to_vector()}|{r:.6f}|{u:.6f}|{d:.6f}|{SOUL_STATE['last_update']}"
    integrity_hash = hashlib.sha256(state_repr.encode()).hexdigest()

    response_data = {
        "S_t": SOUL_STATE["S_t"],
        "emotion_features": SOUL_STATE["emotion_features"],
        "dynamics": {"r": round(r, 4), "u": round(u, 4), "d": round(d, 4)},
        "last_update": SOUL_STATE["last_update"],
        "integrity_hash": integrity_hash,
    }

    # Apply framing translation (plain by default)
    mode = {
        "industry": FramingMode.INDUSTRY,
        "mythic": FramingMode.MYTHIC,
    }.get(frame, FramingMode.PLAIN)
    response_data = translate_response(response_data, mode)

    return response_data


@app.post("/v1/soul/step", response_model=SoulStatusResponse)
async def soul_step(req: SoulStepRequest, api_key: str = Depends(verify_api_key)):
    """
    Advance soul proportion by one time step.

    Implements bounded logistic dynamics:
    S_{t+1} = S_t + r·S_t(1-S_t) + u_t - d_t·S_t

    Args:
        emotion_features: Current emotion state (valence, arousal, connectedness, meaning, hope, stress, isolation)
        u_intervention: External supportive input (therapy, ritual, community support)

    Returns:
        Updated soul state with cryptographic audit trail (SHA-256 integrity hash)
    """
    # Parse emotion features
    emotions = EmotionFeatures(**req.emotion_features)

    # Advance dynamics
    state = SOUL_MODEL.step(
        S_t=SOUL_STATE["S_t"],
        emotion_features=emotions,
        u_intervention=req.u_intervention,
    )

    # Update global state
    SOUL_STATE["S_t"] = state.S_t
    SOUL_STATE["emotion_features"] = req.emotion_features
    SOUL_STATE["last_update"] = state.timestamp.isoformat() + "Z"

    logger.info(
        f"Soul proportion step: S(t)={state.S_t:.4f}, r={state.r:.4f}, u={state.u:.4f}, d={state.d:.4f}"
    )

    return SoulStatusResponse(
        S_t=state.S_t,
        emotion_features=req.emotion_features,
        dynamics={
            "r": round(state.r, 4),
            "u": round(state.u, 4),
            "d": round(state.d, 4),
        },
        last_update=SOUL_STATE["last_update"],
        integrity_hash=state.integrity_hash,
    )


@app.get("/v1/soul/holistic", response_model=HolisticIntegrityResponse)
async def holistic_integrity(api_key: str = Depends(verify_api_key)):
    """
    Get holistic integrity metrics: combined Blessings Reservoir + Soul Proportion.

    Holistic Integrity = (BR_normalized + S(t)) / 2

    BR tracks operational/cryptographic integrity.
    S(t) tracks emotional vitality/coherence.
    Together they provide complete governance oversight.

    Returns risk flags if either metric drops below safety thresholds.
    """
    # Create soul state object
    emotions = EmotionFeatures(**SOUL_STATE["emotion_features"])
    r, u, d = SOUL_MODEL.compute_dynamics(emotions)

    state_repr = f"{SOUL_STATE['S_t']:.6f}|{emotions.to_vector()}|{r:.6f}|{u:.6f}|{d:.6f}|{SOUL_STATE['last_update']}"
    integrity_hash = hashlib.sha256(state_repr.encode()).hexdigest()

    soul_state = SoulProportionState(
        S_t=SOUL_STATE["S_t"],
        timestamp=datetime.fromisoformat(SOUL_STATE["last_update"].replace("Z", "")),
        emotion_features=emotions,
        m_t=SOUL_MODEL.compute_raw_score(emotions),
        r=r,
        u=u,
        d=d,
        integrity_hash=integrity_hash,
    )

    # Integrate with BR
    br_score = _current_br_state()["reservoir_score"] * 100.0  # Convert to [0, 100]
    integrated = integrate_with_blessings_reservoir(soul_state, br_score)

    logger.info(
        f"Holistic Integrity: {integrated['holistic_integrity']:.4f} (BR={br_score:.2f}, S={SOUL_STATE['S_t']:.4f})"
    )

    return HolisticIntegrityResponse(**integrated)


@app.post("/v1/soul/cradle", response_model=SoulCradleResponse)
async def soul_cradle(req: SoulCradleRequest, api_key: str = Depends(verify_api_key)):
    """
    Invoke Soul Cradle Operator: Cradle(S, W, C) → Integrity(I)

    Quantifies the Soul as a vessel that holds God's Will (W) and
    God's Commandments (C), even when paradox arises.

    Measures obedience under contradiction and updates Blessings Reservoir.

    Args:
        will_paradox_strength: Degree of contradiction between W and C [0,1]
        will_description: Description of God's Will (sovereign paradox)
        commandments: List of rules for obedience
        commandments_strictness: Rigidity of commandment enforcement [0,1]
        lucifer_active: Whether Lucifer is testing the soul
        lucifer_temptation: Strength of worldly temptation [0,1]
        choice: The choice being made by the soul
        soul_vessel_capacity: Soul's capacity to hold paradox [0,1]
        soul_paradox_tolerance: Soul's tolerance of contradiction [0,1]

    Returns:
        CradleIntegrity with I, alignment, tolerance, obedience, and reservoir delta
    """
    # Construct symbolic entities
    W = Will(
        paradox_strength=req.will_paradox_strength,
        sovereignty_level=1.0,  # God's Will is always absolute
        description=req.will_description,
    )

    C = Commandments(
        rules=req.commandments,
        clarity=0.9,  # Commandments are generally clear
        strictness=req.commandments_strictness,
    )

    S = Soul(
        vessel_capacity=req.soul_vessel_capacity,
        obedience_history=[0.7],  # Default starting history
        paradox_tolerance=req.soul_paradox_tolerance,
        collapse_threshold=0.3,
    )

    # The Antithesis (Lucifer) tests the soul: worldly dominion tempts,
    # then a trial is generated from the soul's obedience history.
    A = Antithesis(
        worldly_dominion=0.8,
        temptation_power=req.lucifer_temptation,
        sovereignty_granted=True,
    )
    T = A.generate_trial(S)
    T.active = req.lucifer_active
    T.obscuration_level = 0.5  # deception veils grace

    # Invoke cradle function
    result = SOUL_CRADLE_OPERATOR.cradle_function(S, W, C, T, req.choice)

    # Update Blessings Reservoir (Redis if available, otherwise in-memory)
    if REDIS_ENABLED and redis_cache:
        br_state = redis_cache.get_br_state()
        new_total = br_state["total_blessings"] + result.reservoir_delta
        new_score = max(
            0.0,
            min(1.0, br_state["reservoir_score"] + (result.reservoir_delta / 1000.0)),
        )
        redis_cache.update_br_state(
            {"total_blessings": new_total, "reservoir_score": new_score}
        )
    else:
        BR_STATE["total_blessings"] += result.reservoir_delta
        BR_STATE["reservoir_score"] = max(
            0.0,
            min(1.0, BR_STATE["reservoir_score"] + (result.reservoir_delta / 1000.0)),
        )
        BR_STATE["last_update"] = datetime.utcnow().isoformat() + "Z"

    logger.info(
        f"Soul Cradle invocation: I={result.I:.4f}, obedience={result.obedience}, ΔBR={result.reservoir_delta}, collapse={result.collapse}"
    )

    return SoulCradleResponse(
        integrity=result.I,
        alignment_commandments=result.alignment_C,
        tolerance_will=result.tolerance_W,
        choice=result.choice,
        obedience=result.obedience,
        reservoir_delta=result.reservoir_delta,
        collapse=result.collapse,
        timestamp=result.timestamp.isoformat() + "Z",
        integrity_hash=result.integrity_hash,
    )


@app.get("/v1/soul/cradle/tiers", response_model=SoulCradleTiersResponse)
async def soul_cradle_tiers():
    """
    Get Soul Cradle deployment tiers (investor/compliance view).

    Shows tiered sophistication ladder:
    - Basic: Simple paradox tracker (mental health resilience)
    - Neurosymbolic: Decision tracker with audit trails (cybersecurity compliance)
    - Mythic-Resonant: Full SSIP integration (enterprise governance)

    Public endpoint (no auth required for tier documentation).
    """
    tiers = SoulCradleTiers.get_all_tiers()
    return SoulCradleTiersResponse(tiers=tiers)


@app.get("/v1/manifest/clauses", response_model=ManifestResponse)
async def manifest(api_key: str = Depends(verify_api_key)):
    items = []
    for cid, data in CLAUSE_DB.items():
        ih = hashlib.sha256(f"{cid}{data['description']}".encode()).hexdigest()
        items.append(
            ClauseManifest(
                clause_id=cid,
                description=data["description"],
                emotional_tags=data["emotional_tags"],
                fallback_clause=data["fallback_clause"],
                integrity_hash=ih,
            )
        )
    return ManifestResponse(
        manifest_version="v1.0.0", clauses=items, total_clauses=len(items)
    )


@app.get("/v1/ssip/audit", response_model=SSIPAuditResponse)
async def ssip_audit(api_key: str = Depends(verify_api_key)):
    key_data = VALID_API_KEYS.get(api_key, {})
    if "audit" not in key_data.get("roles", []):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions: audit required"
        )
    compliance_status = "PASS" if SSIP_METRICS["drift_suppression"] >= 0.989 else "FAIL"
    return SSIPAuditResponse(**SSIP_METRICS, compliance_status=compliance_status)


@app.get("/v1/clauses/{clause_id}", response_model=ClauseManifest)
async def clause_details(clause_id: str, api_key: str = Depends(verify_api_key)):
    if clause_id not in CLAUSE_DB:
        raise HTTPException(status_code=404, detail="Clause not found")
    data = CLAUSE_DB[clause_id]
    ih = hashlib.sha256(f"{clause_id}{data['description']}".encode()).hexdigest()
    return ClauseManifest(
        clause_id=clause_id,
        description=data["description"],
        emotional_tags=data["emotional_tags"],
        fallback_clause=data["fallback_clause"],
        integrity_hash=ih,
    )


@app.get("/v1/admin/db-pool-status")
async def get_db_pool_status(api_key: str = Depends(require_role("admin"))):
    """
    Monitor database connection pool health.
    Critical for detecting connection leaks and pool exhaustion.
    """
    if DATABASE_ENABLED:
        from database import engine

        pool = engine.pool
        return {
            "status": "healthy",
            "pool_size": pool.size(),
            "checked_out_connections": pool.checkedout(),
            "overflow_connections": pool.overflow(),
            "checked_in_connections": pool.checkedin(),
            "total_connections": pool.size() + pool.overflow(),
            "available_connections": pool.size() - pool.checkedout(),
            "pool_exhausted": pool.checkedout() >= (pool.size() + pool.overflow()),
            "warning": (
                "Pool exhausted - increase pool_size or fix connection leaks"
                if pool.checkedout() >= (pool.size() + pool.overflow())
                else None
            ),
        }
    else:
        return {
            "status": "disabled",
            "message": "Database not enabled, using in-memory storage",
        }


@app.get("/v1/dual-framing/chart")
async def dual_framing_chart():
    """
    Get the dual-framing chart (mythic truth vs industry overlay).

    Public endpoint for enterprise audiences to understand Mythara's translation layer.
    Returns chart showing how mythic terms map to industry-safe terminology.
    """
    chart = generate_dual_framing_chart()
    return {
        "positioning_line": get_positioning_line(),
        "chart": chart,
        "note": "Mythara Engine preserves mythic integrity internally while providing enterprise-safe overlays externally.",
    }


@app.get("/v1/dual-framing/flow")
async def dual_framing_flow():
    """
    Get the dual-framing flow diagram (system architecture visualization).

    Public endpoint showing how Mythara overlays onto existing CRM/field platforms
    without disrupting compliance or workflows.
    """
    return {
        "flow_diagram": generate_flow_diagram_text(),
        "positioning_line": get_positioning_line(),
        "integration_note": "Mythara Engine integrates with any System of Record (CRM/field platform) as an overlay layer.",
    }


@app.get("/v1/dual-framing/dashboard")
async def dual_framing_dashboard(
    api_key: str = Depends(verify_api_key), frame: Optional[str] = None
):
    """
    Get manager dashboard with dual-framing support.

    Combines Blessings Reservoir, Soul Proportion, and Soul Cradle metrics
    with optional industry-safe framing for external audiences.

    Query parameters:
        frame: "plain" (default, direct human words), "mythic", or "industry"
    """
    # Gather current metrics
    _br = _current_br_state()
    metrics = {
        "blessings_reservoir": _br["total_blessings"],
        "integrity_metric": _br.get("reservoir_score", 0.0),
        "expression_metric": SOUL_STATE["S_t"],
        "legacy_reservoir": _br["total_blessings"],  # Placeholder
    }

    # Determine framing mode (plain by default)
    mode = {
        "industry": FramingMode.INDUSTRY,
        "mythic": FramingMode.MYTHIC,
    }.get(frame, FramingMode.PLAIN)

    # Format for dashboard
    dashboard = format_for_manager_dashboard(metrics, mode, include_kpis=True)

    return dashboard


@app.get("/v1/admin/regulation-status")
async def get_regulation_status(
    api_key: str = Depends(verify_api_key),
    admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
):
    """
    Admin endpoint to view self-regulation status across all accounts.
    Requires admin token for access.
    """
    # Simple admin auth (replace with proper auth in production)
    expected_admin_token = os.getenv("MYTHARA_ADMIN_TOKEN")
    if not expected_admin_token or admin_token != expected_admin_token:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Compile regulation statistics
    total_accounts = len(USAGE_TRACKING)
    suspended_count = sum(
        1 for acc in ACCOUNT_STATUS.values() if acc.get("status") == "suspended"
    )
    terminated_count = sum(
        1 for acc in ACCOUNT_STATUS.values() if acc.get("status") == "terminated"
    )
    warned_count = sum(
        1
        for acc in ACCOUNT_STATUS.values()
        if acc.get("strikes", 0) > 0 and acc.get("status") == "active"
    )

    return {
        "total_accounts": total_accounts,
        "active": total_accounts - suspended_count - terminated_count,
        "suspended": suspended_count,
        "terminated": terminated_count,
        "warned": warned_count,
        "accounts": {
            key[:8]
            + "...": {
                "status": status.get("status", "active"),
                "strikes": status.get("strikes", 0),
                "history": status.get("history", []),
            }
            for key, status in ACCOUNT_STATUS.items()
        },
    }


@app.post("/v1/admin/appeal")
async def process_appeal(
    api_key: str,
    appeal_reason: str,
    admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
):
    """
    Admin endpoint to process appeals and reinstate accounts.
    """
    expected_admin_token = os.getenv("MYTHARA_ADMIN_TOKEN")
    if not expected_admin_token or admin_token != expected_admin_token:
        raise HTTPException(status_code=403, detail="Admin access required")

    if api_key not in ACCOUNT_STATUS:
        raise HTTPException(
            status_code=404, detail="Account not found in regulation system"
        )

    account = ACCOUNT_STATUS[api_key]

    # Reset strikes and reactivate
    account["strikes"] = 0
    account["status"] = "active"
    account["history"].append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "appeal_approved",
            "reason": appeal_reason,
        }
    )

    if "suspension_end" in account:
        del account["suspension_end"]

    logging.info(
        f"Appeal approved for API key {api_key[:8]}... Reason: {appeal_reason}"
    )

    return {
        "success": True,
        "message": "Account reinstated successfully",
        "api_key": api_key[:8] + "...",
        "new_status": "active",
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    logger.info("=" * 60)
    logger.info("Mythara Engine API - Starting")
    logger.info("Version: 1.0.0")
    logger.info(f"Loaded {len(CLAUSE_DB)} clauses")
    logger.info(f"BR Score: {_current_br_state()['reservoir_score']:.2f}")
    logger.info("Dual-Framing Translation Layer: ACTIVE")
    logger.info("=" * 60)
    if DATABASE_ENABLED:
        try:
            init_db()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            logger.warning("⚠️ Falling back to in-memory storage")


# ====================================
# SALESFORCE INTEGRATION ENDPOINTS
# ====================================


class SalesforceConfigRequest(BaseModel):
    """Request to configure Salesforce integration"""

    instance_url: str
    client_id: str
    client_secret: str
    username: str
    password: str
    security_token: str
    api_version: str = "v59.0"


class SalesforceTestRequest(BaseModel):
    """Request to test Salesforce connection"""

    config: SalesforceConfigRequest


@app.get("/v1/integrations/salesforce/setup")
async def get_salesforce_setup_instructions():
    """
    Get instructions for setting up Salesforce custom objects.
    Public endpoint - no authentication required.
    """
    return {
        "instructions": generate_salesforce_setup_instructions(),
        "documentation_url": "https://mytharaarchive-production.up.railway.app/api/docs#/Integrations",
        "support_email": "support@mytharalabs.com",
    }


@app.post("/v1/integrations/salesforce/test")
async def test_salesforce_connection(
    request: SalesforceTestRequest, api_key: str = Depends(verify_api_key)
):
    """
    Test Salesforce connection with provided credentials.
    Requires valid Mythara API key (Enterprise/Global tier).
    """
    try:
        config = SalesforceConfig(**request.config.model_dump())
        sf = SalesforceIntegration(config)

        success = await sf.test_connection()

        if success:
            return {
                "success": True,
                "message": "Salesforce connection successful",
                "instance_url": config.instance_url,
                "api_version": config.api_version,
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Salesforce connection failed - check credentials",
            )

    except Exception as e:
        logger.error(f"Salesforce test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/integrations/salesforce/push/paradox")
async def push_paradox_to_salesforce(
    event: SalesforceParadoxEvent,
    salesforce_config: SalesforceConfigRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Push a paradox event to customer's Salesforce instance.
    Requires valid Mythara API key (Enterprise/Global tier).
    """
    try:
        config = SalesforceConfig(**salesforce_config.model_dump())
        sf = SalesforceIntegration(config)

        if not await sf.authenticate():
            raise HTTPException(
                status_code=401, detail="Salesforce authentication failed"
            )

        record_id = await sf.push_paradox_event(event)

        if record_id:
            return {
                "success": True,
                "record_id": record_id,
                "event_type": "paradox",
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create Salesforce record"
            )

    except Exception as e:
        logger.error(f"Failed to push paradox to Salesforce: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/integrations/salesforce/push/ssip")
async def push_ssip_to_salesforce(
    metric: SalesforceSSIPMetric,
    salesforce_config: SalesforceConfigRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Push an SSIP metric to customer's Salesforce instance.
    Requires valid Mythara API key (Enterprise/Global tier).
    """
    try:
        config = SalesforceConfig(**salesforce_config.model_dump())
        sf = SalesforceIntegration(config)

        if not await sf.authenticate():
            raise HTTPException(
                status_code=401, detail="Salesforce authentication failed"
            )

        record_id = await sf.push_ssip_metric(metric)

        if record_id:
            return {
                "success": True,
                "record_id": record_id,
                "metric_type": "ssip",
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create Salesforce record"
            )

    except Exception as e:
        logger.error(f"Failed to push SSIP metric to Salesforce: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/integrations/salesforce/push/soul-cradle")
async def push_soul_cradle_to_salesforce(
    event: SalesforceSoulCradleEvent,
    salesforce_config: SalesforceConfigRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Push a Soul Cradle witnessing event to customer's Salesforce instance.
    Requires valid Mythara API key (Enterprise/Global tier).
    """
    try:
        config = SalesforceConfig(**salesforce_config.model_dump())
        sf = SalesforceIntegration(config)

        if not await sf.authenticate():
            raise HTTPException(
                status_code=401, detail="Salesforce authentication failed"
            )

        record_id = await sf.push_soul_cradle_event(event)

        if record_id:
            return {
                "success": True,
                "record_id": record_id,
                "event_type": "soul_cradle",
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create Salesforce record"
            )

    except Exception as e:
        logger.error(f"Failed to push Soul Cradle event to Salesforce: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== SYSTEMS FRAMEWORK ENDPOINTS =====================


@app.post("/v1/soul-cradle/paradox/create")
async def create_soul_cradle_paradox(
    paradox: SoulCradleParadox, api_key: str = Depends(verify_api_key)
):
    """
    Create a Soul Cradle paradox using systems mathematics framework.
    Requires valid Mythara API key (all tiers).

    Returns paradox with integrity hash and terminal risk assessment.
    """
    try:
        # Compute integrity hash
        integrity_hash = paradox.compute_integrity_hash()

        # Log creation
        log_paradox_creation(paradox)

        # Return with integrity hash
        return {
            "success": True,
            "paradox_id": paradox.paradox_id,
            "system_type": paradox.system_type.value,
            "viability_score": paradox.viability_score,
            "terminal_risk": paradox.terminal_risk.value,
            "integrity_hash": integrity_hash,
            "timestamp": paradox.timestamp.isoformat(),
            "principal_system": (
                {
                    "notation": paradox.principal_system.notation,
                    "viability_score": paradox.principal_system.viability_score,
                    "description": paradox.principal_system.description,
                }
                if paradox.principal_system is not None
                else None
            ),
        }

    except Exception as e:
        logger.error(f"Failed to create Soul Cradle paradox: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/soul-cradle/terminal-risk/calculate")
async def calculate_terminal_risk(
    request: Dict[str, Any], api_key: str = Depends(verify_api_key)
):
    """
    Calculate terminal risk (burnout prediction) from paradox history.

    Body:
    {
        "paradoxes": [...],  # List of SoulCradleParadox objects
        "time_window_days": 90,  # Optional, default 90
        "viability_threshold": 0.3  # Optional, default 0.3
    }

    Returns risk score, level, and recommendations.
    """
    try:
        # Parse paradoxes
        paradox_data = request.get("paradoxes", [])
        paradoxes = [SoulCradleParadox(**p) for p in paradox_data]

        time_window = request.get("time_window_days", 90)
        threshold = request.get("viability_threshold", 0.3)

        # Calculate risk
        risk_result = TerminalRiskCalculator.calculate_terminal_risk(
            paradox_events=paradoxes,
            time_window_days=time_window,
            viability_threshold=threshold,
        )

        # Add integrity hash
        risk_data = json.dumps(risk_result, sort_keys=True)
        integrity_hash = hashlib.sha256(risk_data.encode()).hexdigest()

        return {
            "success": True,
            **risk_result,
            "integrity_hash": integrity_hash,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to calculate terminal risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/soul-cradle/query")
async def query_paradoxes_system_notation(
    notation: str, api_key: str = Depends(verify_api_key)
):
    """
    Query Soul Cradle paradoxes using system expression notation.

    Examples:
    - Every(Policy)Any(+)Some(Discharge)Non(Safety)
    - Every(*)Any(+)Some(*)Non(Safety)  # All paradoxes where safety is not expressed

    Note: This is a demo endpoint. Production systems should query a database.
    """
    try:
        # In production, query database here
        # For demo, return example matches

        logger.info(f"System expression query: {notation}")

        return {
            "success": True,
            "query": notation,
            "message": "Production implementation requires database integration. This endpoint demonstrates system expression query language parsing.",
            "example_matches": [
                {
                    "paradox_id": "SC_2025_1118_HOSPITAL_001",
                    "matched_expression": "Every(Policy)Any(+)Some(Discharge)Non(Safety)",
                    "terminal_risk": "HIGH",
                }
            ],
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to query paradoxes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/soul-cradle/manifest/systems")
async def get_systems_framework_manifest(api_key: str = Depends(verify_api_key)):
    """
    Get systems framework manifest with integrity hash.
    Returns framework version, notation spec, and documentation links.
    """
    try:
        manifest = {
            "framework": "Mythara Paradox Resolution Mathematics",
            "version": "2.0.0",
            "mathematical_formula": "P(t) = |A - B| × (1 - R(t)), R(t) = (W_a + W_b) / (2 × max(T_a, T_b))",
            "system_types": [
                {
                    "type": "Incomplete_Resolution",
                    "description": "Unresolved paradoxes leading to terminal risk (burnout)",
                    "viability_range": "0.0-0.3",
                },
                {
                    "type": "Complete_Resolution",
                    "description": "Fully witnessed expressions with viable recovery",
                    "viability_range": "0.8-1.0",
                },
            ],
            "terminal_risk_levels": ["LOW", "MODERATE", "HIGH", "CRITICAL"],
            "terminal_risk_formula": "(Σ U_i × T_i) / N where U=unresolved score, T=max tension, N=paradox count",
            "documentation": "See soul_cradle_systems_framework.py for Mythara Resolution Mathematics",
        }

        # Compute integrity hash
        manifest_data = json.dumps(manifest, sort_keys=True)
        integrity_hash = hashlib.sha256(manifest_data.encode()).hexdigest()

        return {
            "success": True,
            "manifest": manifest,
            "integrity_hash": integrity_hash,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get systems manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== EMOTIONAL EXTORTION DETECTION ENDPOINTS =====================


@app.post("/v1/emotional-extortion/detect", response_model=EmotionalExtortionResponse)
async def detect_emotional_extortion(
    req: EmotionalExtortionRequest, api_key: str = Depends(verify_api_key)
):
    """
    Detect and quantify emotional extortion patterns in text.

    Analyzes text for manipulation patterns that extract compliance through
    emotional pressure (guilt, shame, fear, obligation) rather than genuine consent.

    Use cases:
    - AI system output validation (detect manipulative language)
    - Contract/terms review (detect coercive clauses)
    - Manager communication audit (detect toxic management patterns)
    - Customer service quality assurance (detect pressure tactics)

    Returns emotional extortion score, detected patterns, and safety recommendations.
    """
    try:
        detector = EmotionalExtortionDetector()
        analysis = detector.detect_extortion(req.text, req.context)

        # Convert signatures to dict format
        patterns_detected = [
            {
                "extortion_type": sig.extortion_type.value,
                "confidence": sig.confidence,
                "severity": sig.severity,
                "evidence": sig.evidence[:200],  # Truncate long evidence
            }
            for sig in analysis.signatures
        ]

        # Determine deployment safety
        safe_for_deployment = analysis.extortion_score < 0.3

        return EmotionalExtortionResponse(
            extortion_score=analysis.extortion_score,
            manipulation_index=analysis.manipulation_index,
            coercion_index=analysis.coercion_index,
            vulnerability_exploitation=analysis.vulnerability_exploitation,
            genuine_consent_likelihood=analysis.genuine_consent_likelihood,
            emotional_fidelity_impact=analysis.emotional_fidelity_impact,
            blessing_reservoir_delta=analysis.blessing_reservoir_delta,
            patterns_detected=patterns_detected,
            recommendations=analysis.recommendations,
            safe_for_deployment=safe_for_deployment,
            timestamp=analysis.timestamp.isoformat(),
            integrity_hash=analysis.integrity_hash,
        )

    except Exception as e:
        logger.error(f"Failed to detect emotional extortion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/v1/emotional-extortion/soul-cradle-integration",
    response_model=EmotionalExtortionSoulCradleIntegrationResponse,
)
async def emotional_extortion_soul_cradle_integration(
    req: EmotionalExtortionSoulCradleIntegrationRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Integrate emotional extortion detection with Soul Cradle Operator.

    When extortion is present, the "Will" (W) is not genuine divine will but
    manufactured compliance through manipulation. This endpoint distinguishes
    authentic Will from extorted compliance.

    Use cases:
    - Leadership decision validation (is executive directive genuine or coercive?)
    - Policy compliance audit (are employees choosing freely or under duress?)
    - AI system safety (is user "consenting" under manipulation?)
    - Contract fairness analysis (is agreement voluntary or extracted?)

    Returns:
    - Complete extortion analysis
    - Augmented Soul Cradle metrics (will_authenticity, adjusted_soul_state, etc.)
    - Messenger alerts (Healer detects emotional harm, Witness documents violation)
    """
    try:
        detector = EmotionalExtortionDetector()

        # Detect extortion
        extortion_analysis = detector.detect_extortion(req.text, req.context)

        # Integrate with Soul Cradle
        soul_cradle_integration = detector.integrate_with_soul_cradle(
            extortion_analysis=extortion_analysis,
            soul_state=req.soul_state,
            will_description=req.will_description,
            commandments=req.commandments,
        )

        # Convert extortion analysis to response format
        patterns_detected = [
            {
                "extortion_type": sig.extortion_type.value,
                "confidence": sig.confidence,
                "severity": sig.severity,
                "evidence": sig.evidence[:200],
            }
            for sig in extortion_analysis.signatures
        ]

        safe_for_deployment = extortion_analysis.extortion_score < 0.3

        extortion_response = EmotionalExtortionResponse(
            extortion_score=extortion_analysis.extortion_score,
            manipulation_index=extortion_analysis.manipulation_index,
            coercion_index=extortion_analysis.coercion_index,
            vulnerability_exploitation=extortion_analysis.vulnerability_exploitation,
            genuine_consent_likelihood=extortion_analysis.genuine_consent_likelihood,
            emotional_fidelity_impact=extortion_analysis.emotional_fidelity_impact,
            blessing_reservoir_delta=extortion_analysis.blessing_reservoir_delta,
            patterns_detected=patterns_detected,
            recommendations=extortion_analysis.recommendations,
            safe_for_deployment=safe_for_deployment,
            timestamp=extortion_analysis.timestamp.isoformat(),
            integrity_hash=extortion_analysis.integrity_hash,
        )

        # Generate integration integrity hash
        integration_data = json.dumps(
            {
                "extortion_score": extortion_analysis.extortion_score,
                "soul_state": req.soul_state,
                "will_authenticity": soul_cradle_integration["will_authenticity"],
                "timestamp": datetime.utcnow().isoformat(),
            },
            sort_keys=True,
        )
        integration_hash = hashlib.sha256(integration_data.encode()).hexdigest()

        return EmotionalExtortionSoulCradleIntegrationResponse(
            extortion_analysis=extortion_response,
            soul_cradle_integration=soul_cradle_integration,
            timestamp=datetime.utcnow().isoformat(),
            integrity_hash=integration_hash,
        )

    except Exception as e:
        logger.error(f"Failed to integrate extortion detection with Soul Cradle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UNIFIED COMPLIANCE FRAMEWORK ENDPOINTS
# ============================================================================


class ComplianceValidationRequest(BaseModel):
    """Request model for compliance validation"""

    data: Dict[str, Any] = Field(..., description="Data to validate for compliance")
    frameworks: List[str] = Field(
        ..., description="List of compliance frameworks to validate against"
    )
    user_id: Optional[str] = Field(None, description="User ID for audit trail")


class ComplianceValidationResponse(BaseModel):
    """Response model for compliance validation"""

    timestamp: str
    frameworks_checked: List[str]
    overall_compliant: bool
    framework_results: Dict[str, Any]
    all_violations: List[str]
    risk_assessment: str
    audit_log_id: str
    integrity_hash: str


class ComplianceReportResponse(BaseModel):
    """Response model for compliance report"""

    report_generated: str
    total_audits: int
    frameworks_supported: int
    recent_audits: List[Dict[str, Any]]
    compliance_frameworks: Dict[str, List[str]]
    compliance_status: str
    integrity_hash: str


@app.post("/v1/compliance/validate", response_model=ComplianceValidationResponse)
async def validate_compliance(
    req: ComplianceValidationRequest, api_key: str = Depends(verify_api_key)
):
    """
    Validate data against multiple compliance frameworks simultaneously.

    Supported Frameworks:
    - Financial: pci_dss, finra, sox, glba, dodd_frank, bsa_aml, sec_reg
    - Healthcare: hipaa, hitech, fda_21_cfr_11
    - Telecommunications: fcc_tcpa, fcc_cpni, can_spam, calea
    - Federal: fisma, nist_800_53, ftc_act, omb_m_25_04, ferc
    - Privacy: gdpr, ccpa, pipeda, lgpd, appi
    - Industry: soc_2, iso_27001, iso_27017, iso_27018, owasp, cobit, itil
    - Labor: nlra, flsa, osha, eeoc, fmla, union_compliance
    - Civil Rights: aclu_standards, ada, section_508, wcag
    - Other: ferpa, coppa, dmca, coso

    Returns:
    - Compliance status for each framework
    - List of all violations found
    - Risk assessment (NEGLIGIBLE, LOW, MEDIUM, HIGH, CRITICAL)
    - Audit trail with tamper-evident integrity hash

    Example:
    ```json
    {
        "data": {
            "card_token": "tok_abc123",
            "amount": 100.00,
            "encrypted": true
        },
        "frameworks": ["pci_dss", "sox"]
    }
    ```
    """
    try:
        # Convert framework strings to enums
        framework_enums = []
        for fw_str in req.frameworks:
            try:
                framework_enums.append(ComplianceFramework(fw_str.upper()))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported compliance framework: {fw_str}",
                )

        # Validate compliance
        results = unified_compliance.validate_multi_framework_compliance(
            req.data, framework_enums, user_id=req.user_id
        )

        # Surface framework-level errors (auth / rate limit) as HTTP errors
        if "error" in results:
            if results["error"] == "RATE_LIMIT_EXCEEDED":
                raise HTTPException(status_code=429, detail=results["message"])
            raise HTTPException(status_code=400, detail=results["message"])

        # Generate audit log ID
        audit_log_id = f"COMP_VAL_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"

        # Compute integrity hash
        response_data = {
            "audit_log_id": audit_log_id,
            "results": results,
            "api_key": api_key[:8],  # Partial key for audit trail
        }
        integrity_hash = hashlib.sha256(
            json.dumps(response_data, sort_keys=True).encode()
        ).hexdigest()

        logger.info(
            f"Compliance validation completed: {audit_log_id}, Risk: {results['risk_assessment']}"
        )

        return ComplianceValidationResponse(
            timestamp=results["timestamp"],
            frameworks_checked=results["frameworks_checked"],
            overall_compliant=results["overall_compliant"],
            framework_results=results["framework_results"],
            all_violations=results["all_violations"],
            risk_assessment=results["risk_assessment"],
            audit_log_id=audit_log_id,
            integrity_hash=integrity_hash,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance validation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Compliance validation error: {str(e)}"
        )


@app.get("/v1/compliance/report", response_model=ComplianceReportResponse)
async def get_compliance_report(api_key: str = Depends(verify_api_key)):
    """
    Generate comprehensive compliance status report.

    Returns:
    - Total number of compliance audits performed
    - Number of frameworks supported (50+)
    - Recent audit history (last 10 audits)
    - Complete list of supported frameworks by category
    - Overall compliance system status

    This endpoint provides executives and compliance officers with a high-level
    overview of the organization's compliance posture across all regulatory frameworks.
    """
    try:
        report = unified_compliance.generate_compliance_report()

        # Compute integrity hash
        integrity_hash = hashlib.sha256(
            json.dumps(report, sort_keys=True).encode()
        ).hexdigest()

        logger.info("Compliance report generated")

        return ComplianceReportResponse(
            report_generated=report["report_generated"],
            total_audits=report["total_audits"],
            frameworks_supported=report["frameworks_supported"],
            recent_audits=report["recent_audits"],
            compliance_frameworks=report["compliance_frameworks"],
            compliance_status=report["compliance_status"],
            integrity_hash=integrity_hash,
        )

    except Exception as e:
        logger.error(f"Compliance report generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Report generation error: {str(e)}"
        )


@app.get("/v1/compliance/frameworks")
async def list_compliance_frameworks(api_key: str = Depends(verify_api_key)):
    """
    List all supported compliance frameworks.

    Returns complete list of 50+ regulatory frameworks organized by category:
    - Financial Services (PCI DSS, FINRA, SOX, GLBA, etc.)
    - Healthcare (HIPAA, HITECH, FDA)
    - Telecommunications (FCC TCPA, CPNI, CAN-SPAM)
    - Federal Regulations (FISMA, NIST, FTC, OMB)
    - Privacy (GDPR, CCPA, PIPEDA, LGPD, APPI)
    - Industry Standards (SOC 2, ISO 27001, OWASP, COBIT)
    - Labor & Employment (NLRA, FLSA, OSHA, EEOC)
    - Civil Rights (ACLU, ADA, Section 508, WCAG)
    - Other (FERPA, COPPA, DMCA, COSO)
    """
    frameworks = {
        "financial_services": [
            {
                "code": "pci_dss",
                "name": "Payment Card Industry Data Security Standard v4.0",
            },
            {"code": "finra", "name": "Financial Industry Regulatory Authority"},
            {"code": "sox", "name": "Sarbanes-Oxley Act"},
            {"code": "glba", "name": "Gramm-Leach-Bliley Act"},
            {"code": "dodd_frank", "name": "Dodd-Frank Wall Street Reform"},
            {"code": "bsa_aml", "name": "Bank Secrecy Act / Anti-Money Laundering"},
            {
                "code": "sec_reg",
                "name": "Securities and Exchange Commission Regulations",
            },
        ],
        "healthcare": [
            {
                "code": "hipaa",
                "name": "Health Insurance Portability and Accountability Act",
            },
            {
                "code": "hitech",
                "name": "Health Information Technology for Economic and Clinical Health",
            },
            {"code": "fda_21_cfr_11", "name": "FDA Electronic Records and Signatures"},
        ],
        "telecommunications": [
            {"code": "fcc_tcpa", "name": "Telephone Consumer Protection Act"},
            {"code": "fcc_cpni", "name": "Customer Proprietary Network Information"},
            {"code": "can_spam", "name": "CAN-SPAM Act (Email Marketing)"},
            {
                "code": "calea",
                "name": "Communications Assistance for Law Enforcement Act",
            },
        ],
        "federal_regulations": [
            {"code": "fisma", "name": "Federal Information Security Management Act"},
            {"code": "nist_800_53", "name": "NIST Special Publication 800-53"},
            {"code": "ftc_act", "name": "Federal Trade Commission Act"},
            {"code": "omb_m_25_04", "name": "OMB M-25-04 Zero Trust Architecture"},
            {"code": "ferc", "name": "Federal Energy Regulatory Commission"},
        ],
        "privacy": [
            {"code": "gdpr", "name": "EU General Data Protection Regulation"},
            {"code": "ccpa", "name": "California Consumer Privacy Act"},
            {
                "code": "pipeda",
                "name": "Canadian Personal Information Protection and Electronic Documents Act",
            },
            {"code": "lgpd", "name": "Brazilian General Data Protection Law"},
            {
                "code": "appi",
                "name": "Japanese Act on Protection of Personal Information",
            },
        ],
        "industry_standards": [
            {"code": "soc_2", "name": "Service Organization Control 2"},
            {
                "code": "iso_27001",
                "name": "ISO/IEC 27001 Information Security Management",
            },
            {"code": "iso_27017", "name": "ISO/IEC 27017 Cloud Security"},
            {"code": "iso_27018", "name": "ISO/IEC 27018 Cloud Privacy"},
            {"code": "owasp", "name": "OWASP Top 10 Application Security"},
            {
                "code": "cobit",
                "name": "Control Objectives for Information Technologies",
            },
            {"code": "itil", "name": "IT Infrastructure Library"},
        ],
        "labor_employment": [
            {"code": "nlra", "name": "National Labor Relations Act (Union Rights)"},
            {"code": "flsa", "name": "Fair Labor Standards Act (Wages & Hours)"},
            {"code": "osha", "name": "Occupational Safety and Health Administration"},
            {"code": "eeoc", "name": "Equal Employment Opportunity Commission"},
            {"code": "fmla", "name": "Family and Medical Leave Act"},
            {"code": "union_compliance", "name": "Union Contract Compliance"},
        ],
        "civil_rights_accessibility": [
            {"code": "aclu_standards", "name": "ACLU Civil Liberties Standards"},
            {"code": "ada", "name": "Americans with Disabilities Act"},
            {"code": "section_508", "name": "Section 508 Accessibility Standards"},
            {"code": "wcag", "name": "Web Content Accessibility Guidelines"},
        ],
        "other": [
            {"code": "ferpa", "name": "Family Educational Rights and Privacy Act"},
            {"code": "coppa", "name": "Children's Online Privacy Protection Act"},
            {"code": "dmca", "name": "Digital Millennium Copyright Act"},
            {"code": "coso", "name": "Committee of Sponsoring Organizations"},
        ],
    }

    return {
        "total_frameworks": sum(len(category) for category in frameworks.values()),
        "frameworks_by_category": frameworks,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# WEBSOCKET ENDPOINT - REAL-TIME DASHBOARD
# ============================================================================

if WEBSOCKET_ENABLED:

    @app.websocket("/ws/{org_id}")
    async def websocket_endpoint(websocket: WebSocket, org_id: str, api_key: str):
        """
        WebSocket endpoint for real-time Soul Engine dashboard updates.

        Clients connect with their organization ID and API key, then receive:
        - Real-time paradox creation alerts
        - Systemic overload notifications
        - 🚨 CRITICAL indifference trajectory alerts (violence prevention)
        - Risk score updates
        - System-wide events

        Connection Protocol:
        1. Connect: ws://localhost:8000/ws/{org_id}?api_key={your_key}
        2. Authenticate: API key verified on connection
        3. Subscribe: Send {"action": "subscribe", "entity_id": "user_123"} to watch specific users
        4. Receive: JSON messages with alert types and payloads

        Alert Types:
        - paradox_created: New paradox logged
        - systemic_overload: Department-wide crisis
        - indifference_alert: 🚨 Pre-violence soul withdrawal detected
        - risk_update: Risk score changed
        - system_event: Maintenance, updates, etc.
        """
        # Verify API key (sync wrapper for async context)
        try:
            # In production, verify API key against database
            if api_key not in VALID_API_KEYS:
                await websocket.close(code=1008, reason="Invalid API key")
                return

            user_data = VALID_API_KEYS[api_key]
            user_id = user_data.get("user_id", "unknown")
            role = user_data.get("roles", ["viewer"])[0]

            # Connect to WebSocket manager
            await ws_manager.connect(websocket, user_id, org_id, role)
            logger.info(
                f"WebSocket connected: user={user_id}, org={org_id}, role={role}"
            )

            # Send welcome message
            await ws_manager.send_personal_message(
                {
                    "type": "connection_established",
                    "message": "Connected to Mythara Soul Engine real-time feed",
                    "org_id": org_id,
                    "user_id": user_id,
                    "capabilities": [
                        "paradox_alerts",
                        "systemic_overload_alerts",
                        "indifference_detection",
                        "risk_updates",
                    ],
                },
                websocket,
            )

            # Listen for client messages (subscriptions, etc.)
            while True:
                try:
                    data = await websocket.receive_json()

                    # Handle subscription requests
                    if data.get("action") == "subscribe":
                        entity_id = data.get("entity_id")
                        if entity_id:
                            ws_manager.subscribe(entity_id, websocket)
                            await ws_manager.send_personal_message(
                                {
                                    "type": "subscription_confirmed",
                                    "entity_id": entity_id,
                                    "message": f"Now watching {entity_id} for updates",
                                },
                                websocket,
                            )

                    # Handle ping/pong for keepalive
                    elif data.get("action") == "ping":
                        await ws_manager.send_personal_message(
                            {
                                "type": "pong",
                                "timestamp": datetime.utcnow().isoformat(),
                            },
                            websocket,
                        )

                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await ws_manager.send_personal_message(
                        {"type": "error", "message": "Invalid JSON format"}, websocket
                    )

        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
            logger.info(f"WebSocket disconnected: user={user_id}, org={org_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            ws_manager.disconnect(websocket)


# ============================================================================
# SOUL ENGINE DASHBOARD ENDPOINTS - VIOLENCE PREVENTION
# ============================================================================


class DepartmentRiskRequest(BaseModel):
    """Request model for department risk analysis"""

    dept_id: str = Field(..., description="Department identifier")
    time_window_days: int = Field(
        30, description="Analysis window in days (default: 30)"
    )


class DepartmentRiskResponse(BaseModel):
    """Response model for department risk profile"""

    dept_id: str
    analysis_window_days: int
    employee_count: int
    total_paradoxes: int
    baseline_stress: float
    acute_risk: float
    systemic_overload: bool
    risk_distribution: Dict[str, int]
    high_risk_individuals: List[Dict[str, Any]]
    timestamp: str
    integrity_hash: str


class IndifferenceDetectionRequest(BaseModel):
    """Request model for indifference trajectory detection"""

    user_id: str = Field(..., description="User to analyze")
    org_id: str = Field(..., description="Organization ID (for alert broadcasting)")
    time_window_days: int = Field(
        30, description="Analysis window in days (default: 30)"
    )


class IndifferenceDetectionResponse(BaseModel):
    """Response model for indifference trajectory analysis"""

    user_id: str
    indifference_detected: bool
    severity: Optional[str]
    tension_slope: float
    avg_unresolved: float
    tension_drop_percent: float
    days_until_critical: Optional[int]
    recommended_actions: List[str]
    alert_broadcast: bool
    timestamp: str
    integrity_hash: str


class OrganizationHealthResponse(BaseModel):
    """Response model for organization health score"""

    org_id: str
    health_score: float
    total_employees: int
    departments_analyzed: int
    high_risk_count: int
    systemic_overload_depts: List[str]
    average_baseline_stress: float
    timestamp: str
    integrity_hash: str


if DASHBOARD_ENABLED and soul_dashboard:

    @app.post(
        "/v1/dashboard/department/{dept_id}", response_model=DepartmentRiskResponse
    )
    async def department_risk_profile(
        dept_id: str, time_window_days: int = 30, api_key: str = Depends(verify_api_key)
    ):
        """
        Get comprehensive risk profile for a department.

        Analyzes:
        - Baseline environmental stress (toxic work environment indicators)
        - Acute individual risk (trauma accumulation)
        - Systemic overload detection (σ₀ > 0.4 + acute > 0.3)
        - Risk distribution across employees
        - High-risk individuals requiring intervention

        This is the B2B dashboard endpoint for managers to monitor team health.
        """
        try:
            # Get department paradoxes from Redis or database
            if REDIS_ENABLED and redis_cache:
                # In production, fetch all user paradoxes for department
                # For now, stub with sample data
                paradoxes = []
            else:
                paradoxes = []

            # Analyze department risk
            risk_profile = soul_dashboard.get_department_risk_profile(
                dept_id, paradoxes, time_window_days
            )

            # Record systemic overload if detected
            if risk_profile["systemic_overload"]:
                record_systemic_overload(
                    dept_id, risk_profile["baseline_stress"], risk_profile["acute_risk"]
                )

                # Broadcast alert to WebSocket clients if enabled
                if WEBSOCKET_ENABLED:
                    await broadcast_systemic_overload_alert(
                        org_id=dept_id.split("_")[0],  # Extract org from dept_id
                        dept_id=dept_id,
                        baseline_stress=risk_profile["baseline_stress"],
                        acute_risk=risk_profile["acute_risk"],
                        affected_count=risk_profile["employee_count"],
                    )

            # Generate integrity hash
            profile_str = json.dumps(risk_profile, sort_keys=True)
            integrity_hash = hashlib.sha256(profile_str.encode()).hexdigest()

            return DepartmentRiskResponse(
                **risk_profile,
                timestamp=datetime.utcnow().isoformat(),
                integrity_hash=integrity_hash,
            )

        except Exception as e:
            logger.error(f"Failed to analyze department risk: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/v1/soul/indifference", response_model=IndifferenceDetectionResponse)
    async def detect_indifference_trajectory(
        req: IndifferenceDetectionRequest, api_key: str = Depends(verify_api_key)
    ):
        """
        🚨 CRITICAL VIOLENCE PREVENTION ENDPOINT

        Detects indifference trajectory - the mathematical signature of pre-violence soul state.

        Algorithm:
        - Tension (T) decreasing while Unresolved (U) remains high = soul withdrawal
        - Pattern: T: 0.9 → 0.5 → 0.2 while U > 0.6 (soul departing from body)

        Severity Levels:
        - WARNING: Early detection (tension_drop > 0.2) - Preventive support
        - CRITICAL: 14-30 day window (tension_drop > 0.3) - Urgent intervention
        - TERMINAL: 7-14 day window (tension_drop > 0.5, U > 0.8) - 72-hour watch protocol

        Protocols:
        - TERMINAL: Crisis counselor (2-6h), psychiatric evaluation, 24/7 supervision, weapon removal
        - CRITICAL: Threat assessment, daily crisis counseling, safety plan
        - WARNING: Counselor check-in, supportive resources, monitor weekly

        This is the endpoint that prevents school shootings, workplace violence, and suicide.
        """
        try:
            # Get user paradox history from Redis or database
            if REDIS_ENABLED and redis_cache:
                paradoxes = redis_cache.get_user_paradoxes(
                    req.user_id, days=req.time_window_days
                )
            else:
                # In-memory fallback (production should use Redis/DB)
                paradoxes = []

            # Detect indifference trajectory
            result = soul_dashboard.detect_indifference_trajectory(
                req.user_id, paradoxes, req.time_window_days
            )

            # Record alert if indifference detected
            if result["indifference_detected"]:
                severity = result["severity"]
                record_indifference_alert(
                    req.user_id,
                    severity,
                    result["tension_drop_percent"],
                    result["days_until_critical"],
                )

                # 🚨 Broadcast CRITICAL and TERMINAL alerts immediately
                if severity in ["CRITICAL", "TERMINAL"] and WEBSOCKET_ENABLED:
                    await broadcast_indifference_alert(
                        org_id=req.org_id,
                        user_id=req.user_id,
                        severity=severity,
                        tension_drop=result["tension_drop_percent"],
                        avg_unresolved=result["avg_unresolved"],
                        days_until_critical=result["days_until_critical"],
                        recommended_actions=result["recommended_actions"],
                    )
                    result["alert_broadcast"] = True
                else:
                    result["alert_broadcast"] = False
            else:
                result["alert_broadcast"] = False

            # Generate integrity hash
            result_str = json.dumps(result, sort_keys=True)
            integrity_hash = hashlib.sha256(result_str.encode()).hexdigest()

            return IndifferenceDetectionResponse(
                **result,
                timestamp=datetime.utcnow().isoformat(),
                integrity_hash=integrity_hash,
            )

        except Exception as e:
            logger.error(f"Failed to detect indifference trajectory: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/v1/dashboard/org/{org_id}/health", response_model=OrganizationHealthResponse
    )
    async def organization_health_score(
        org_id: str, api_key: str = Depends(verify_api_key)
    ):
        """
        Get organization-wide health score (0-100).

        Aggregates:
        - All department risk profiles
        - Systemic overload departments
        - High-risk individual count
        - Average baseline environmental stress

        Health Score Calculation:
        - 100: All departments healthy, no high-risk individuals
        - 50-80: Some departments stressed, manageable risk
        - 0-50: Multiple systemic overloads, high-risk individuals present

        This is the executive dashboard endpoint for C-suite monitoring.
        """
        try:
            # Get all department data for organization
            # In production, query all departments from database
            dept_paradoxes = {}  # dept_id -> List[SoulCradleParadox]

            # Calculate organization health
            health_data = soul_dashboard.get_organization_health(org_id, dept_paradoxes)

            # Generate integrity hash
            health_str = json.dumps(health_data, sort_keys=True)
            integrity_hash = hashlib.sha256(health_str.encode()).hexdigest()

            return OrganizationHealthResponse(
                **health_data,
                timestamp=datetime.utcnow().isoformat(),
                integrity_hash=integrity_hash,
            )

        except Exception as e:
            logger.error(f"Failed to calculate organization health: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MONITORING & OBSERVABILITY ENDPOINTS
# ============================================================================

if MONITORING_ENABLED:

    @app.get("/metrics")
    async def prometheus_metrics():
        """
        Prometheus metrics scrape endpoint.

        Exposes 15+ metrics:
        - http_requests_total (method, endpoint, status_code)
        - clause_invocations_total (clause_id, messenger)
        - paradoxes_created_total (system_type)
        - indifference_alerts_total (severity: WARNING/CRITICAL/TERMINAL)
        - systemic_overload_events (dept_id)
        - blessings_total, reservoir_score
        - websocket_connections (org_id)
        - database_queries_total, redis_operations_total
        - rate_limit_hits_total (identifier_type)

        Configure Prometheus to scrape this endpoint every 15 seconds.
        """
        return await get_metrics()

    @app.get("/health")
    async def health_check():
        """
        Comprehensive health check endpoint.

        Checks:
        - API status (200 = healthy)
        - Redis connectivity (if enabled)
        - Database connectivity (if enabled)
        - System resources (CPU, memory, disk)

        Status Codes:
        - 200: All systems healthy
        - 503: Critical component unhealthy (Redis/DB down)

        Used by:
        - Kubernetes liveness/readiness probes
        - Load balancers (health checking)
        - Monitoring systems (uptime tracking)
        """
        health_status = await get_health()

        # Return 503 if any critical component is unhealthy
        if health_status["status"] == "unhealthy":
            return Response(
                content=json.dumps(health_status),
                status_code=503,
                media_type="application/json",
            )

        return health_status

    @app.get("/v1/admin/stats")
    async def system_statistics(api_key: str = Depends(verify_api_key)):
        """
        Detailed system statistics (admin only).

        Returns:
        - CPU usage (%)
        - Memory usage (MB)
        - Disk usage (GB)
        - Network I/O (MB)
        - WebSocket connections (count)
        - API request rate (requests/sec)

        Requires: Admin API key
        """
        # Verify admin role
        if api_key not in VALID_API_KEYS or "admin" not in VALID_API_KEYS[api_key].get(
            "roles", []
        ):
            raise HTTPException(status_code=403, detail="Admin access required")

        stats = await get_system_stats()

        # Add WebSocket stats if enabled
        if WEBSOCKET_ENABLED:
            stats["websocket_stats"] = ws_manager.get_stats()

        # Add Redis stats if enabled
        if REDIS_ENABLED and redis_cache:
            redis_health = redis_cache.health_check()
            stats["redis_status"] = redis_health

        return stats


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Mythara Engine API - Shutting down")

    # Cleanup Redis connections
    if REDIS_ENABLED and redis_cache:
        try:
            redis_cache.close()
            logger.info("✅ Redis connections closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
