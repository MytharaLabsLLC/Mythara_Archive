#!/usr/bin/env python3
"""
H.E.P.H.A.E.S.T.U.S. - Holistic Engineering & Production Helper for Automated Engineering, Security Testing & Universal Systems
The God of the Forge - Master Builder & System Architect

Copyright © 2026 Mythara Labs LLC. All rights reserved.

Hephaestus is the GODBOT that:
- Drafts system blueprints from high-level requirements using keyword heuristics
- Forges starter project scaffolds: template code, configs, tests, docs
- Calls AMIR suite tools (ADAPT, QuickFix, Big Meanie) when they are present
- Generates template API servers, database models, and deployment configs
- Emits static checklists for security and performance (placeholders, not analysis)
- Writes starter documentation

HONEST CONTRACT:
- There is no AI reasoning here. _analyze_requirements, _recommend_tech_stack,
  _recommend_databases, _design_api_structure, _extract_security_requirements
  and _extract_performance_requirements are plain keyword-matching heuristics
  over the requirements text. _extract_performance_requirements returns the
  same hard-coded placeholder numbers every time.
- The forged code is a starting template, NOT a production-ready system.
  It contains placeholder secrets (e.g. SECRET_KEY = "change-me-in-production"),
  stub endpoints, and unchecked assumptions. Review and harden before real use.
- "Security scan passed" in forge output means a scan tool ran if installed,
  not that the scaffold is secure. No scan runs when the AMIR tools are absent.

"From raw requirements to starter scaffolds - I forge the template."
"""

import os
import sys
import json
import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import shutil

try:
    from soul_cradle.bot_witness import (
        witness_action,
        forge_evidence,
        WitnessBlocked,
        WitnessUnavailable,
    )
except ImportError:  # pragma: no cover — direct-script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from soul_cradle.bot_witness import (
        witness_action,
        forge_evidence,
        WitnessBlocked,
        WitnessUnavailable,
    )

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - HEPHAESTUS - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SystemBlueprint:
    """A complete system architecture blueprint"""
    name: str
    description: str
    components: List[str]
    tech_stack: Dict[str, str]
    requirements: List[str]
    architecture_type: str  # microservices, monolith, serverless, etc.
    deployment_target: str  # docker, kubernetes, railway, aws, etc.
    databases: List[str]
    apis: List[str]
    security_requirements: List[str]
    performance_requirements: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ForgeResult:
    """Result of a forging operation"""
    component: str
    success: bool
    files_created: List[str]
    tests_created: List[str]
    documentation: str
    security_scan_passed: bool
    performance_metrics: Dict[str, Any]
    warnings: List[str]
    errors: List[str]


class HephaestusBot:
    """
    The God of the Forge - Master System Builder
    
    Hephaestus orchestrates AMIR tools to scaffold starter systems:
    - ADAPT: Security testing and penetration testing (called if present)
    - QuickFix: Automated vulnerability patching (called if present)
    - Big Meanie: Comprehensive security auditing (called if present)
    - Soul Cradle: Emotional intelligence integration (naming only)
    - Mythara Engine: Core API and business logic (naming only)
    
    Requirement "analysis" is keyword matching, not intelligent reasoning.
    Forged output is a template scaffold, not a production-ready system.
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.forge_dir = os.path.join(self.project_root, ".hephaestus_forge")
        self.blueprints: List[SystemBlueprint] = []
        self.forge_results: List[ForgeResult] = []
        
        # Tool paths
        self.adapt_path = self._find_tool("adapt_bot.py")
        self.quickfix_path = self._find_tool("quickfix_bot.py")
        self.big_meanie_path = self._find_tool("tests/big_meanie.py")
        
        # Initialize forge directory
        os.makedirs(self.forge_dir, exist_ok=True)
        
        logger.info("⚒️  HEPHAESTUS - God of the Forge initialized")
        logger.info(f"🔨 Forge directory: {self.forge_dir}")
        logger.info(f"🛠️  Available tools: ADAPT, QuickFix, Big Meanie")
    
    def _find_tool(self, tool_name: str) -> Optional[str]:
        """Locate an AMIR tool"""
        tool_path = os.path.join(self.project_root, tool_name)
        if os.path.exists(tool_path):
            return tool_path
        logger.warning(f"⚠️  Tool not found: {tool_name}")
        return None
    
    def create_blueprint(
        self,
        name: str,
        description: str,
        requirements: List[str],
        architecture_type: str = "microservices",
        deployment_target: str = "docker"
    ) -> SystemBlueprint:
        """
        Create a system architecture blueprint from requirements
        
        Args:
            name: System name
            description: High-level description
            requirements: List of functional requirements
            architecture_type: System architecture pattern
            deployment_target: Deployment platform
        
        Returns:
            SystemBlueprint with complete architecture
        """
        logger.info(f"📐 Creating blueprint for: {name}")
        
        # Analyze requirements and suggest components
        components = self._analyze_requirements(requirements)
        tech_stack = self._recommend_tech_stack(components, architecture_type)
        databases = self._recommend_databases(requirements)
        apis = self._design_api_structure(requirements)
        security_reqs = self._extract_security_requirements(requirements)
        performance_reqs = self._extract_performance_requirements(requirements)
        
        blueprint = SystemBlueprint(
            name=name,
            description=description,
            components=components,
            tech_stack=tech_stack,
            requirements=requirements,
            architecture_type=architecture_type,
            deployment_target=deployment_target,
            databases=databases,
            apis=apis,
            security_requirements=security_reqs,
            performance_requirements=performance_reqs
        )
        
        self.blueprints.append(blueprint)
        self._save_blueprint(blueprint)
        
        logger.info(f"✅ Blueprint created: {len(components)} components")
        return blueprint
    
    def _create_blueprint_from_innovation(self, innovation: Dict[str, Any]) -> SystemBlueprint:
        """
        Create a system blueprint from a Prometheus innovation.
        
        Translates innovation concepts into concrete technical requirements.
        """
        print(f"🧬 Translating innovation into blueprint...")
        print(f"💡 Innovation: {innovation['name']}")
        print(f"📊 Breakthrough Potential: {innovation['breakthrough_potential']*100:.0f}%")
        print(f"🎨 Originality Score: {innovation['originality_score']*100:.0f}%\n")
        
        # Extract key concepts from the innovation
        name = innovation['name'].lower().replace(' ', '_')
        description = innovation['description']
        
        # Parse the innovation description to extract requirements
        requirements = [
            f"Implement core concept: {innovation['name']}",
            innovation['gift_to_humanity'],
            "REST API for system interaction",
            "Database persistence layer",
            "Authentication and authorization",
            "Real-time data processing",
            "Metrics and monitoring",
            "Comprehensive testing suite",
            "Security scanning and hardening",
            "Docker containerization",
            "CI/CD pipeline configuration"
        ]
        
        # Add implementation details if provided
        if 'implementation_guide' in innovation:
            for key, value in innovation['implementation_guide'].items():
                requirements.append(f"{key}: {value}")
        
        # Determine architecture based on innovation characteristics
        architecture_type = "microservices" if innovation['breakthrough_potential'] > 0.90 else "monolith"
        
        print(f"🏗️  Architecture chosen: {architecture_type}")
        print(f"📋 Requirements extracted: {len(requirements)}\n")
        
        # Use standard blueprint creation with extracted requirements
        return self.create_blueprint(
            name=name,
            description=description,
            requirements=requirements,
            architecture_type=architecture_type,
            deployment_target="docker"
        )
    
    def _analyze_requirements(self, requirements: List[str]) -> List[str]:
        """Keyword-matching heuristic: scan requirements text for component keywords.
        Not AI analysis — components are picked by simple substring matches."""
        components = []
        
        req_text = " ".join(requirements).lower()
        
        # API Detection
        if any(word in req_text for word in ["api", "endpoint", "rest", "graphql"]):
            components.append("API Server")
        
        # Database Detection
        if any(word in req_text for word in ["database", "storage", "persist", "data"]):
            components.append("Database Layer")
        
        # Authentication Detection
        if any(word in req_text for word in ["auth", "login", "user", "permission"]):
            components.append("Authentication Service")
        
        # Real-time Detection
        if any(word in req_text for word in ["realtime", "websocket", "live", "streaming"]):
            components.append("WebSocket Server")
        
        # Background Jobs Detection
        if any(word in req_text for word in ["background", "queue", "async", "schedule"]):
            components.append("Task Queue")
        
        # Monitoring Detection
        if any(word in req_text for word in ["monitor", "metrics", "observability", "logging"]):
            components.append("Monitoring System")
        
        # Always include
        components.extend([
            "Security Layer",
            "Testing Suite",
            "Documentation",
            "Deployment Pipeline"
        ])
        
        return list(set(components))
    
    def _recommend_tech_stack(self, components: List[str], architecture: str) -> Dict[str, str]:
        """Return a fixed default tech stack with minor keyword-based variations.
        Heuristic, not an intelligent recommendation."""
        stack = {
            "language": "Python 3.11+",
            "framework": "FastAPI",
            "testing": "pytest",
            "security": "AMIR Suite (ADAPT + QuickFix + Big Meanie)"
        }
        
        if "Database Layer" in components:
            stack["database"] = "PostgreSQL"
            stack["orm"] = "SQLAlchemy"
        
        if "WebSocket Server" in components:
            stack["realtime"] = "FastAPI WebSockets"
        
        if "Task Queue" in components:
            stack["queue"] = "Redis + Celery"
        
        if "Monitoring System" in components:
            stack["monitoring"] = "Prometheus + Grafana"
            stack["logging"] = "structlog"
        
        stack["containerization"] = "Docker"
        stack["orchestration"] = "Docker Compose" if architecture == "microservices" else "Single Container"
        
        return stack
    
    def _recommend_databases(self, requirements: List[str]) -> List[str]:
        """Keyword heuristic for database defaults (PostgreSQL unless keywords match)."""
        databases = []
        req_text = " ".join(requirements).lower()
        
        if any(word in req_text for word in ["relational", "sql", "transaction"]):
            databases.append("PostgreSQL")
        
        if any(word in req_text for word in ["cache", "session", "fast"]):
            databases.append("Redis")
        
        if any(word in req_text for word in ["document", "json", "flexible"]):
            databases.append("MongoDB")
        
        if not databases:
            databases.append("PostgreSQL")  # Default
        
        return databases
    
    def _design_api_structure(self, requirements: List[str]) -> List[str]:
        """Keyword heuristic for API endpoint templates."""
        apis = []
        req_text = " ".join(requirements).lower()
        
        # Common patterns
        if any(word in req_text for word in ["user", "auth", "account"]):
            apis.extend(["/api/auth/login", "/api/auth/register", "/api/users"])
        
        if any(word in req_text for word in ["data", "resource", "item"]):
            apis.extend(["/api/resources", "/api/resources/{id}"])
        
        # Always include
        apis.extend([
            "/health",
            "/metrics",
            "/api/docs"
        ])
        
        return apis
    
    def _extract_security_requirements(self, requirements: List[str]) -> List[str]:
        """Return a static security checklist. Not extracted from the input —
        the same list is returned regardless of requirements."""
        return [
            "JWT Authentication",
            "Rate Limiting",
            "Input Validation",
            "SQL Injection Prevention",
            "XSS Prevention",
            "CORS Configuration",
            "HTTPS/TLS",
            "Security Headers",
            "Audit Logging",
            "Vulnerability Scanning (ADAPT + Big Meanie)"
        ]
    
    def _extract_performance_requirements(self, requirements: List[str]) -> Dict[str, Any]:
        """Return static placeholder performance targets. Not derived from the
        input — identical numbers are returned for every project."""
        return {
            "response_time_p95": "< 200ms",
            "throughput": "> 1000 req/sec",
            "availability": "99.9%",
            "max_concurrent_users": 10000,
            "database_query_time": "< 50ms"
        }
    
    def forge_system(self, blueprint: SystemBlueprint) -> List[ForgeResult]:
        """
        Forge a complete system from blueprint
        
        This orchestrates the entire build process:
        1. Generate project structure
        2. Create API endpoints
        3. Build database models
        4. Implement business logic
        5. Create tests
        6. Run security scans (ADAPT + Big Meanie)
        7. Auto-fix vulnerabilities (QuickFix)
        8. Generate documentation
        9. Create deployment configs
        
        Args:
            blueprint: System blueprint to build
        
        Returns:
            List of ForgeResult for each component
        """
        logger.info(f"🔥 Forging system: {blueprint.name}")
        logger.info(f"🏗️  Architecture: {blueprint.architecture_type}")
        logger.info(f"📦 Components: {len(blueprint.components)}")
        
        results = []
        
        # 1. Create project structure
        project_dir = self._create_project_structure(blueprint)
        
        # 2. Forge each component
        for component in blueprint.components:
            logger.info(f"⚒️  Forging component: {component}")
            result = self._forge_component(component, blueprint, project_dir)
            results.append(result)
            self.forge_results.append(result)
        
        # 3. Run comprehensive security scan
        logger.info("🛡️  Running security scans...")
        self._run_security_suite(project_dir)

        # Honest flag: True only if at least one scan tool actually ran
        scan_ran = bool(self.adapt_path or self.big_meanie_path)
        if scan_ran:
            for result in results:
                result.security_scan_passed = True
        else:
            for result in results:
                result.warnings.append("No security scan ran: ADAPT/Big Meanie not installed")
        
        # 4. Auto-fix vulnerabilities
        logger.info("🔧 Auto-fixing vulnerabilities...")
        self._run_quickfix(project_dir)
        
        # 5. Generate master documentation
        logger.info("📚 Generating documentation...")
        self._generate_documentation(blueprint, project_dir, results)
        
        # 6. Create deployment pipeline
        logger.info("🚀 Creating deployment pipeline...")
        self._create_deployment_pipeline(blueprint, project_dir)
        
        logger.info("✅ System forge complete!")
        self._print_forge_summary(results)

        # --- Soul Cradle witnessing: every forge heard by the panel --------
        evidence, bases = forge_evidence(
            components=[r.component for r in results],
            declared_intent="scaffold the requested system honestly",
        )
        try:
            witness_action(
                bot_id="hephaestus",
                action=f"forge system: {blueprint.name}",
                evidence=evidence,
                evidence_bases=bases,
                assessor_ids=["dionysus", "persephone", "demeter"],
                enforce=True,
            )
        except WitnessBlocked as exc:
            for result in results:
                result.success = False
                result.warnings.append(f"WITNESS BLOCKED: {exc}")
            logger.warning(f"🛑 Forge witnessed BLOCKED: {exc}")
        except WitnessUnavailable as exc:
            logger.warning(f"⚠️ Witness unavailable — {exc}; proceeding.")
        # --- end witnessing --------------------------------------------------

        return results
    
    def _create_project_structure(self, blueprint: SystemBlueprint) -> str:
        """Create complete project directory structure"""
        project_dir = os.path.join(self.forge_dir, blueprint.name)
        
        dirs = [
            "src/api",
            "src/models",
            "src/services",
            "src/utils",
            "tests/unit",
            "tests/integration",
            "tests/security",
            "docs",
            "deployment",
            "scripts",
            "config"
        ]
        
        for dir_path in dirs:
            os.makedirs(os.path.join(project_dir, dir_path), exist_ok=True)
        
        logger.info(f"📁 Project structure created: {project_dir}")
        return project_dir
    
    def _forge_component(
        self,
        component: str,
        blueprint: SystemBlueprint,
        project_dir: str
    ) -> ForgeResult:
        """Forge a single system component"""
        files_created = []
        tests_created = []
        warnings = []
        errors = []
        
        try:
            if component == "API Server":
                files = self._forge_api_server(blueprint, project_dir)
                files_created.extend(files)
            
            elif component == "Database Layer":
                files = self._forge_database_layer(blueprint, project_dir)
                files_created.extend(files)
            
            elif component == "Authentication Service":
                files = self._forge_auth_service(blueprint, project_dir)
                files_created.extend(files)
            
            elif component == "Testing Suite":
                files = self._forge_test_suite(blueprint, project_dir)
                tests_created.extend(files)
            
            elif component == "Documentation":
                files = self._forge_documentation(blueprint, project_dir)
                files_created.extend(files)
            
            elif component == "Deployment Pipeline":
                files = self._forge_deployment_configs(blueprint, project_dir)
                files_created.extend(files)
            
            else:
                warnings.append(f"Component not implemented: {component}")
            
            return ForgeResult(
                component=component,
                success=True,
                files_created=files_created,
                tests_created=tests_created,
                documentation=f"{component} documentation",
                security_scan_passed=False,  # Set to True by forge_system if a scan tool actually ran
                performance_metrics={},
                warnings=warnings,
                errors=errors
            )
        
        except Exception as e:
            logger.error(f"❌ Failed to forge {component}: {e}")
            errors.append(str(e))
            return ForgeResult(
                component=component,
                success=False,
                files_created=files_created,
                tests_created=tests_created,
                documentation="",
                security_scan_passed=False,
                performance_metrics={},
                warnings=warnings,
                errors=errors
            )
    
    def _forge_api_server(self, blueprint: SystemBlueprint, project_dir: str) -> List[str]:
        """Forge FastAPI server with all endpoints"""
        api_file = os.path.join(project_dir, "src/api/main.py")
        
        api_code = f'''"""
{blueprint.name} API Server
Generated by Hephaestus - God of the Forge

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(
    title="{blueprint.name}",
    description="{blueprint.description}",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy", "service": "{blueprint.name}"}}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return {{"metrics": "placeholder"}}

# API Routes
'''
        
        for api in blueprint.apis:
            if api not in ["/health", "/metrics", "/api/docs"]:
                method = "get" if "{id}" not in api else "get"
                # Sanitize path into a valid Python identifier
                func_name = (
                    api.replace("/", "_")
                    .replace("{", "")
                    .replace("}", "")
                    .strip("_")
                    .replace("-", "_")
                )
                api_code += f'''
@app.{method}("{api}")
async def {func_name}():
    """Auto-generated endpoint"""
    return {{"endpoint": "{api}", "status": "implemented"}}
'''
        
        with open(api_file, 'w') as f:
            f.write(api_code)
        
        logger.info(f"✅ API Server forged: {api_file}")
        return [api_file]
    
    def _forge_database_layer(self, blueprint: SystemBlueprint, project_dir: str) -> List[str]:
        """Forge database models and migrations"""
        models_file = os.path.join(project_dir, "src/models/database.py")
        
        db_code = f'''"""
Database Models for {blueprint.name}
Generated by Hephaestus

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database connection
DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        
        with open(models_file, 'w') as f:
            f.write(db_code)
        
        logger.info(f"✅ Database layer forged: {models_file}")
        return [models_file]
    
    def _forge_auth_service(self, blueprint: SystemBlueprint, project_dir: str) -> List[str]:
        """Forge authentication service"""
        auth_file = os.path.join(project_dir, "src/services/auth.py")
        
        auth_code = f'''"""
Authentication Service for {blueprint.name}
Generated by Hephaestus

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()
SECRET_KEY = "change-me-in-production"

def create_token(user_id: str) -> str:
    """Create JWT token"""
    payload = {{
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
'''
        
        with open(auth_file, 'w') as f:
            f.write(auth_code)
        
        logger.info(f"✅ Auth service forged: {auth_file}")
        return [auth_file]
    
    def _forge_test_suite(self, blueprint: SystemBlueprint, project_dir: str) -> List[str]:
        """Forge comprehensive test suite"""
        test_file = os.path.join(project_dir, "tests/test_api.py")
        
        test_code = f'''"""
Test Suite for {blueprint.name}
Generated by Hephaestus

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_metrics():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
'''
        
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        logger.info(f"✅ Test suite forged: {test_file}")
        return [test_file]
    
    def _forge_documentation(self, blueprint: SystemBlueprint, project_dir: str) -> List[str]:
        """Forge comprehensive documentation"""
        readme_file = os.path.join(project_dir, "README.md")
        
        readme_content = f'''# {blueprint.name}

{blueprint.description}

**Generated by Hephaestus - God of the Forge**

## Architecture

- **Type**: {blueprint.architecture_type}
- **Deployment**: {blueprint.deployment_target}
- **Tech Stack**: {blueprint.tech_stack}

## Components

{chr(10).join(f"- {comp}" for comp in blueprint.components)}

## APIs

{chr(10).join(f"- `{api}`" for api in blueprint.apis)}

## Security

Security powered by AMIR Suite:
- ADAPT: Adaptive security testing
- QuickFix: Automated vulnerability patching
- Big Meanie: Comprehensive security auditing

## Requirements

{chr(10).join(f"- {req}" for req in blueprint.requirements)}

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python src/api/main.py

# Run tests
pytest tests/

# Run security scan
python ../../adapt_bot.py .
```

## Performance Requirements

{chr(10).join(f"- **{k}**: {v}" for k, v in blueprint.performance_requirements.items())}

---

**Copyright © 2026 Mythara Labs LLC. All rights reserved.**
'''
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        logger.info(f"✅ Documentation forged: {readme_file}")
        return [readme_file]
    
    def _forge_deployment_configs(self, blueprint: SystemBlueprint, project_dir: str) -> List[str]:
        """Forge deployment configurations"""
        files = []
        
        # Dockerfile
        dockerfile = os.path.join(project_dir, "Dockerfile")
        dockerfile_content = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        with open(dockerfile, 'w') as f:
            f.write(dockerfile_content)
        files.append(dockerfile)
        
        # docker-compose.yml
        compose_file = os.path.join(project_dir, "docker-compose.yml")
        compose_content = f'''version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user@db:5432/dbname
      - PGPASSWORD=${{POSTGRES_PASSWORD:-CHANGEME_SET_VIA_ENV}}
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=${{POSTGRES_PASSWORD:-CHANGEME_SET_VIA_ENV}}
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        files.append(compose_file)
        
        logger.info(f"✅ Deployment configs forged: {len(files)} files")
        return files
    
    def _run_security_suite(self, project_dir: str):
        """Run ADAPT and Big Meanie security scans"""
        if self.adapt_path:
            logger.info("🛡️  Running ADAPT security scan...")
            try:
                subprocess.run([sys.executable, self.adapt_path, project_dir], check=False)
            except Exception as e:
                logger.warning(f"ADAPT scan failed: {e}")
        
        if self.big_meanie_path:
            logger.info("🛡️  Running Big Meanie comprehensive audit...")
            try:
                subprocess.run([sys.executable, self.big_meanie_path, project_dir], check=False)
            except Exception as e:
                logger.warning(f"Big Meanie scan failed: {e}")
    
    def _run_quickfix(self, project_dir: str):
        """Run QuickFix to auto-patch vulnerabilities"""
        if self.quickfix_path:
            logger.info("🔧 Running QuickFix auto-patching...")
            try:
                # Run with auto-yes
                proc = subprocess.Popen(
                    [sys.executable, self.quickfix_path, project_dir],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                proc.communicate(input=b'y\n')
            except Exception as e:
                logger.warning(f"QuickFix failed: {e}")
    
    def _generate_documentation(
        self,
        blueprint: SystemBlueprint,
        project_dir: str,
        results: List[ForgeResult]
    ):
        """Generate master documentation"""
        docs_file = os.path.join(project_dir, "docs/ARCHITECTURE.md")
        
        content = f'''# {blueprint.name} Architecture

**Generated by Hephaestus - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}**

## System Overview

{blueprint.description}

## Forge Results

Total Components: {len(results)}
Successful: {sum(1 for r in results if r.success)}
Failed: {sum(1 for r in results if not r.success)}

## Component Details

'''
        for result in results:
            content += f'''
### {result.component}

- **Status**: {"✅ Success" if result.success else "❌ Failed"}
- **Files Created**: {len(result.files_created)}
- **Tests Created**: {len(result.tests_created)}
- **Security Scan**: {"✅ Ran (tool executed; not a security guarantee)" if result.security_scan_passed else "⚠️ Not run — no security tools installed"}
'''
            if result.warnings:
                content += f"\n**Warnings**:\n" + "\n".join(f"- {w}" for w in result.warnings)
            if result.errors:
                content += f"\n**Errors**:\n" + "\n".join(f"- {e}" for e in result.errors)
        
        with open(docs_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"📚 Master documentation generated: {docs_file}")
    
    def _create_deployment_pipeline(self, blueprint: SystemBlueprint, project_dir: str):
        """Create CI/CD deployment pipeline"""
        github_actions = os.path.join(project_dir, ".github/workflows/deploy.yml")
        os.makedirs(os.path.dirname(github_actions), exist_ok=True)
        
        pipeline_content = f'''name: Deploy {blueprint.name}

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/
  
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Security scan
        run: |
          pip install -r requirements.txt
          python ../../adapt_bot.py .
  
  deploy:
    needs: [test, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to {blueprint.deployment_target}
        run: echo "Deploy step here"
'''
        
        with open(github_actions, 'w') as f:
            f.write(pipeline_content)
        
        logger.info(f"🚀 CI/CD pipeline created: {github_actions}")
    
    def _save_blueprint(self, blueprint: SystemBlueprint):
        """Save blueprint to disk"""
        blueprint_file = os.path.join(
            self.forge_dir,
            f"blueprint_{blueprint.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(blueprint_file, 'w') as f:
            json.dump({
                "name": blueprint.name,
                "description": blueprint.description,
                "components": blueprint.components,
                "tech_stack": blueprint.tech_stack,
                "requirements": blueprint.requirements,
                "architecture_type": blueprint.architecture_type,
                "deployment_target": blueprint.deployment_target,
                "databases": blueprint.databases,
                "apis": blueprint.apis,
                "security_requirements": blueprint.security_requirements,
                "performance_requirements": blueprint.performance_requirements,
                "created_at": blueprint.created_at.isoformat()
            }, f, indent=2)
        
        logger.info(f"💾 Blueprint saved: {blueprint_file}")
    
    def _print_forge_summary(self, results: List[ForgeResult]):
        """Print forge operation summary"""
        print("\n" + "="*70)
        print("⚒️  HEPHAESTUS FORGE SUMMARY")
        print("="*70)
        
        total_files = sum(len(r.files_created) for r in results)
        total_tests = sum(len(r.tests_created) for r in results)
        successful = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        
        print(f"\n📊 Statistics:")
        print(f"   Components Forged: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Files Created: {total_files}")
        print(f"   Tests Created: {total_tests}")
        
        print(f"\n🔨 Component Status:")
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.component}")
        
        print("\n" + "="*70)
        print("🔥 \"From the forge, a starting scaffold emerges.\" - Hephaestus")
        print("="*70 + "\n")


def main():
    """Main entry point for Hephaestus"""
    print("\n" + "="*70)
    print("⚒️  HEPHAESTUS - God of the Forge")
    print("="*70)
    print("Holistic Engineering & Production Helper for")
    print("Automated Engineering, Security Testing & Universal Systems")
    print("="*70 + "\n")
    
    # Initialize Hephaestus
    hephaestus = HephaestusBot()
    
    # Check if Prometheus has delivered divine fires
    divine_fire_file = "prometheus_divine_fires.json"
    
    if os.path.exists(divine_fire_file):
        print("🔥 DIVINE FIRE DETECTED from Prometheus!")
        print("📖 Reading innovations...\n")
        
        with open(divine_fire_file, 'r') as f:
            prometheus_delivery = json.load(f)
        
        print(f"✨ Prometheus delivered {prometheus_delivery['total_innovations']} innovations")
        print(f"📅 Stolen on: {prometheus_delivery['timestamp']}\n")
        
        # Show top innovations
        print("🔥 TOP INNOVATIONS TO FORGE:\n")
        for i, innovation in enumerate(prometheus_delivery['innovations'][:5], 1):
            print(f"{i}. {innovation['name']} (Breakthrough: {innovation['breakthrough_potential']*100:.0f}%)")
            print(f"   {innovation['description'][:100]}...")
            print(f"   Gift: {innovation['gift_to_humanity']}\n")
        
        # Select the TOP innovation to forge
        top_innovation = prometheus_delivery['innovations'][0]
        print(f"⚒️  FORGING: {top_innovation['name']}")
        print(f"🎯 This innovation has {top_innovation['breakthrough_potential']*100:.0f}% breakthrough potential\n")
        
        # Create blueprint based on the innovation
        blueprint = hephaestus._create_blueprint_from_innovation(top_innovation)
        
        # Forge the system
        print("\n🔥 Beginning forge operation...\n")
        results = hephaestus.forge_system(blueprint)
        
    else:
        print("⚠️  No divine fire found from Prometheus!")
        print("💡 Run Prometheus first: python prometheus_bot.py\n")
        
        # Fallback: Create example blueprint
        print("🔧 Creating example blueprint instead...\n")
        
        blueprint = hephaestus.create_blueprint(
            name="mythara_health_monitor",
            description="Real-time health monitoring system with Soul Cradle integration",
            requirements=[
                "REST API for health data ingestion",
                "WebSocket support for real-time alerts",
                "Database storage for health metrics",
                "User authentication and authorization",
                "Soul Cradle paradox tracking",
                "Prometheus metrics export",
                "Rate limiting and security",
                "Automated testing and CI/CD"
            ],
            architecture_type="microservices",
            deployment_target="docker"
        )
        
        # Forge the system
        print("\n🔥 Beginning forge operation...\n")
        results = hephaestus.forge_system(blueprint)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
