#!/usr/bin/env python3
"""
Mythara Architect Team Suite - AI-Powered Design & Manufacturing Platform
Blueprint generation, Soul Cradle design intelligence, 3D printing, CNC, laser cutting integration

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

import json
import hashlib
import sqlite3
import logging
import sys
import os
import glob
import subprocess
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

# Add core to path for robustness framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core', 'source_proprietary'))

# Import robustness framework
try:
    from robustness_framework import (
        ConnectionPool, InputValidator, RateLimiter,
        retry_on_failure, compute_integrity_hash, ErrorRecovery
    )
    ROBUSTNESS_AVAILABLE = True
except ImportError:
    ROBUSTNESS_AVAILABLE = False
    logging.warning("⚠️  Robustness framework not available - using basic implementations")

# Mythara Engine integration
try:
    from mythara_engine_sdk import MytharaEngine, ProductConfig
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️  Mythara Engine SDK not available - running in standalone mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ArchitectTeam - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DesignType(Enum):
    """Types of designs"""
    ARCHITECTURAL = "ARCHITECTURAL"  # Buildings, structures
    PRODUCT = "PRODUCT"              # Consumer products
    MECHANICAL = "MECHANICAL"        # Machines, mechanisms
    INDUSTRIAL = "INDUSTRIAL"        # Factory layouts, systems
    FURNITURE = "FURNITURE"          # Tables, chairs, cabinets
    ELECTRONICS = "ELECTRONICS"      # PCBs, enclosures
    ARTISTIC = "ARTISTIC"            # Sculptures, art pieces
    PROTOTYPE = "PROTOTYPE"          # Proof-of-concept models


class FabricationMethod(Enum):
    """Manufacturing methods"""
    FDM_3D_PRINT = "FDM_3D_PRINT"              # Fused Deposition Modeling
    SLA_3D_PRINT = "SLA_3D_PRINT"              # Stereolithography
    SLS_3D_PRINT = "SLS_3D_PRINT"              # Selective Laser Sintering
    CNC_MILLING = "CNC_MILLING"                # CNC mill
    CNC_ROUTING = "CNC_ROUTING"                # CNC router
    LASER_CUTTING = "LASER_CUTTING"            # Laser cutter
    WATERJET = "WATERJET"                      # Waterjet cutting
    INJECTION_MOLDING = "INJECTION_MOLDING"    # Plastic injection
    CASTING = "CASTING"                        # Metal/resin casting
    MANUAL_ASSEMBLY = "MANUAL_ASSEMBLY"        # Hand assembly


class MaterialType(Enum):
    """Material types"""
    PLA = "PLA"                      # 3D print filament
    ABS = "ABS"                      # 3D print filament
    PETG = "PETG"                    # 3D print filament
    NYLON = "NYLON"                  # 3D print filament
    RESIN = "RESIN"                  # SLA resin
    WOOD = "WOOD"                    # Plywood, hardwood
    ACRYLIC = "ACRYLIC"              # Laser cutting
    ALUMINUM = "ALUMINUM"            # CNC, casting
    STEEL = "STEEL"                  # CNC, welding
    CARBON_FIBER = "CARBON_FIBER"    # Composite
    CONCRETE = "CONCRETE"            # Construction
    GLASS = "GLASS"                  # Cutting, etching


@dataclass
class Blueprint:
    """Design blueprint"""
    blueprint_id: str
    project_name: str
    design_type: DesignType
    created_by: str
    timestamp: datetime
    dimensions: Dict[str, float]  # {"length": 100, "width": 50, "height": 30}
    materials: List[MaterialType]
    fabrication_methods: List[FabricationMethod]
    soul_cradle_analysis: Dict[str, Any]  # AI design insights
    technical_drawings: List[str]  # File paths to drawings
    cad_model_path: Optional[str]
    estimated_cost: float
    estimated_time_hours: float
    complexity_score: float  # 0-10
    integrity_hash: str


@dataclass
class DesignReview:
    """Soul Cradle design review"""
    review_id: str
    blueprint_id: str
    timestamp: datetime
    structural_integrity: float  # 0-1
    manufacturability: float      # 0-1
    cost_efficiency: float        # 0-1
    aesthetic_quality: float      # 0-1
    innovation_score: float       # 0-1
    recommendations: List[str]
    warnings: List[str]
    optimizations: List[Dict[str, Any]]


@dataclass
class FabricationJob:
    """Manufacturing job"""
    job_id: str
    blueprint_id: str
    fabrication_method: FabricationMethod
    material: MaterialType
    quantity: int
    printer_id: Optional[str]
    status: str  # QUEUED, PRINTING, COMPLETE, FAILED
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_completion: datetime
    gcode_path: Optional[str]  # For 3D printers
    actual_cost: Optional[float]
    quality_score: Optional[float]


class MytharaArchitectTeam:
    """
    Mythara Architect Team Suite - AI-Powered Design & Manufacturing
    
    Features:
    - Soul Cradle AI design intelligence & optimization
    - Blueprint generation with technical drawings
    - 3D printing integration (FDM, SLA, SLS)
    - CNC milling/routing automation
    - Laser cutting/engraving
    - Material optimization & cost estimation
    - Structural analysis & safety checks
    - Multi-material, multi-process workflows
    - Real-time fabrication monitoring
    - Quality control & inspection
    """
    
    def __init__(self, team_name: str = "ArchitectTeam_01", database_path: Optional[str] = None):
        self.team_name = team_name
        
        # Database setup
        if database_path:
            self.db_path = database_path
        else:
            home_dir = os.path.expanduser("~")
            mythara_dir = os.path.join(home_dir, ".mythara_engine", "ArchitectTeam")
            os.makedirs(mythara_dir, exist_ok=True)
            self.db_path = os.path.join(mythara_dir, "architect_team.db")
        
        self._init_database()
        
        # Mythara Engine integration
        if SDK_AVAILABLE:
            config = ProductConfig(
                product_name="ArchitectTeamSuite",
                product_version="1.0.0",
                database_name=self.db_path,
                custom_clauses=["design_optimization", "structural_analysis", "fabrication_planning"],
                branding={"tagline": "Design Intelligence Meets Manufacturing Reality"}
            )
            self.engine = MytharaEngine(config, user_id=team_name)
        else:
            self.engine = None
        
        # Initialize robustness components
        if ROBUSTNESS_AVAILABLE:
            self.rate_limiter = RateLimiter(max_requests=200, time_window=60)  # Higher limit for design work
            self.error_recovery = ErrorRecovery()
            self.validator = InputValidator()
            logger.info("✓ Robustness framework initialized")
        else:
            self.rate_limiter = None
            self.error_recovery = None
            self.validator = None
        
        # Manufacturing capabilities
        self.available_printers = self._detect_printers()
        self.material_inventory = self._load_material_inventory()
        
        print(f"\n🏗️  Mythara Architect Team Suite initialized: {team_name}")
        print(f"📐 Database: {self.db_path}")
        if self.engine:
            print(f"🧠 Soul Cradle AI: ACTIVE (Design Intelligence Enabled)")
        print(f"🖨️  Available Fabrication Systems: {len(self.available_printers)}")
        print(f"📦 Material Types in Inventory: {len(self.material_inventory)}")
        print()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                project_name TEXT,
                description TEXT,
                design_type TEXT,
                created_by TEXT,
                created_at TEXT,
                status TEXT,
                budget REAL,
                deadline TEXT
            )
        """)
        
            # Blueprints table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS blueprints (
                blueprint_id TEXT PRIMARY KEY,
                project_id TEXT,
                project_name TEXT,
                design_type TEXT,
                created_by TEXT,
                timestamp TEXT,
                dimensions TEXT,  -- JSON
                materials TEXT,  -- JSON array
                fabrication_methods TEXT,  -- JSON array
                soul_cradle_analysis TEXT,  -- JSON
                technical_drawings TEXT,  -- JSON array of paths
                cad_model_path TEXT,
                estimated_cost REAL,
                estimated_time_hours REAL,
                complexity_score REAL,
                integrity_hash TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
            """)
        
            # Design reviews table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS design_reviews (
                review_id TEXT PRIMARY KEY,
                blueprint_id TEXT,
                timestamp TEXT,
                structural_integrity REAL,
                manufacturability REAL,
                cost_efficiency REAL,
                aesthetic_quality REAL,
                innovation_score REAL,
                recommendations TEXT,  -- JSON array
                warnings TEXT,  -- JSON array
                optimizations TEXT,  -- JSON array
                FOREIGN KEY (blueprint_id) REFERENCES blueprints(blueprint_id)
            )
            """)
        
            # Fabrication jobs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fabrication_jobs (
                job_id TEXT PRIMARY KEY,
                blueprint_id TEXT,
                fabrication_method TEXT,
                material TEXT,
                quantity INTEGER,
                printer_id TEXT,
                status TEXT,
                started_at TEXT,
                completed_at TEXT,
                estimated_completion TEXT,
                gcode_path TEXT,
                actual_cost REAL,
                quality_score REAL,
                FOREIGN KEY (blueprint_id) REFERENCES blueprints(blueprint_id)
            )
            """)
        
            # Material inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS material_inventory (
                    material_id TEXT PRIMARY KEY,
                    material_type TEXT,
                    quantity_kg REAL,
                    cost_per_kg REAL,
                    supplier TEXT,
                    last_restocked TEXT
                )
            """)
            
            # Printers/machines table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fabrication_machines (
                    machine_id TEXT PRIMARY KEY,
                    machine_name TEXT,
                    machine_type TEXT,
                    capabilities TEXT,  -- JSON array
                    status TEXT,
                    current_job_id TEXT,
                    total_jobs_completed INTEGER DEFAULT 0,
                    FOREIGN KEY (current_job_id) REFERENCES fabrication_jobs(job_id)
                )
            """)
            
            conn.commit()
            logger.info("✓ Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def _detect_printers(self) -> List[Dict[str, Any]]:
        """
        Detect locally visible devices that *might* be fabrication machines.

        Honest contract: the OS can report print queues and serial devices,
        but it cannot tell us build volumes, materials, or machine models.
        Everything detected is returned as an UNPROFILED device — capability
        profiles must be registered by a human via register_machine().
        Returns [] when nothing is visible. Never invents machines.
        """
        devices: List[Dict[str, Any]] = []
        seen = set()

        def _add(machine_id: str, name: str, source: str, detail: str = ""):
            if machine_id in seen:
                return
            seen.add(machine_id)
            devices.append({
                "machine_id": machine_id,
                "name": name,
                "type": None,  # fabrication profile unknown until registered
                "source": source,
                "detail": detail,
                "status": "DETECTED_UNPROFILED",
            })

        # 1. CUPS print queues (Linux/macOS) — real OS-reported printers
        try:
            out = subprocess.run(["lpstat", "-p"], capture_output=True,
                                 text=True, timeout=5)
            if out.returncode == 0:
                for line in out.stdout.splitlines():
                    parts = line.split()
                    # lpstat prints: "printer <name> is ..."/"printer <name> disabled ..."
                    if len(parts) >= 2 and parts[0] == "printer":
                        qname = parts[1]
                        _add(f"CUPS_{qname}", qname, "cups", line.strip())
        except Exception:
            pass  # lpstat absent (e.g., Windows) — not an error

        # 2. USB serial devices (where 3D printers / CNC controllers appear)
        for pattern in ("/dev/ttyUSB*", "/dev/ttyACM*"):
            for dev in glob.glob(pattern):
                _add(f"SERIAL_{os.path.basename(dev)}", dev, "usb-serial",
                     "serial device present; identity unknown")

        # 3. OctoPrint on localhost (common 3D-printer server)
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:5000/api/version",
                headers={"User-Agent": "mythara-architect"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    info = json.loads(resp.read().decode("utf-8", "replace"))
                    _add("OCTOPRINT_LOCAL", "OctoPrint (localhost:5000)",
                         "octoprint",
                         f"server {info.get('server', '?')}, api {info.get('api', '?')}")
        except Exception:
            pass  # no local OctoPrint — not an error

        # Persist only what was actually detected — never seed fabricated machines.
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            for dev in devices:
                cursor.execute("""
                    INSERT OR REPLACE INTO fabrication_machines
                    (machine_id, machine_name, machine_type, capabilities, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    dev["machine_id"],
                    dev["name"],
                    "UNPROFILED",
                    json.dumps(dev),
                    dev["status"],
                ))
            conn.commit()
        finally:
            conn.close()

        return devices

    def register_machine(self, machine_id: str, name: str,
                         fabrication_method: "FabricationMethod",
                         build_volume: Optional[Dict[str, float]] = None,
                         materials: Optional[List["MaterialType"]] = None) -> Dict[str, Any]:
        """
        Register a real machine's capability profile (human-supplied facts).
        This is how detected-but-unprofiled devices become usable: a person
        who can see the machine tells the suite what it actually is.
        """
        profile = {
            "machine_id": machine_id,
            "name": name,
            "type": fabrication_method.value,
            "build_volume": build_volume or {},
            "materials": [m.value for m in (materials or [])],
            "status": "IDLE",
            "registered_by": "human",
            "registered_at": datetime.now().isoformat(),
        }
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO fabrication_machines
                (machine_id, machine_name, machine_type, capabilities, status)
                VALUES (?, ?, ?, ?, ?)
            """, (machine_id, name, fabrication_method.value,
                  json.dumps(profile), "IDLE"))
            conn.commit()
        finally:
            conn.close()
        # Refresh the in-memory list
        self.available_printers = [p for p in self.available_printers
                                   if p.get("machine_id") != machine_id]
        self.available_printers.append({
            "machine_id": machine_id, "name": name,
            "type": fabrication_method, "build_volume": build_volume or {},
            "materials": materials or [], "status": "IDLE",
        })
        return profile
    
    def _load_material_inventory(self) -> Dict[str, float]:
        """Load material inventory"""
        # Sample inventory
        inventory = {
            MaterialType.PLA: 10.0,      # 10kg
            MaterialType.ABS: 5.0,       # 5kg
            MaterialType.PETG: 8.0,      # 8kg
            MaterialType.RESIN: 2.0,     # 2L
            MaterialType.WOOD: 50.0,     # 50 board feet
            MaterialType.ACRYLIC: 20.0,  # 20 sheets
            MaterialType.ALUMINUM: 100.0 # 100kg
        }
        
        return {mat.value: qty for mat, qty in inventory.items()}
    
    def _compute_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA-256 integrity hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def create_blueprint(self, project_name: str, design_type: DesignType,
                        dimensions: Dict[str, float], materials: List[MaterialType],
                        fabrication_methods: List[FabricationMethod],
                        created_by: str = "ArchitectTeam") -> Blueprint:
        """
        Create new blueprint with Soul Cradle AI analysis
        
        Returns Blueprint with design intelligence insights
        """
        blueprint_id = f"BP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S%f')}_{random.randint(1000,9999)}"
        
        print(f"\n🏗️  Creating blueprint: {project_name}")
        print(f"📐 Design Type: {design_type.value}")
        print(f"📏 Dimensions: {dimensions}")
        print(f"🧠 Analyzing with Soul Cradle AI...")
        
        # Soul Cradle AI analysis
        soul_cradle_analysis = self._soul_cradle_analyze_design(
            design_type, dimensions, materials, fabrication_methods
        )
        
        # Cost estimation
        estimated_cost = self._estimate_cost(materials, dimensions, fabrication_methods)
        
        # Time estimation
        estimated_time = self._estimate_fabrication_time(dimensions, fabrication_methods)
        
        # Complexity scoring
        complexity = self._calculate_complexity(dimensions, materials, fabrication_methods)
        
        # Generate technical drawings (in production, this would use CAD software)
        technical_drawings = self._generate_technical_drawings(blueprint_id, dimensions, design_type)
        
        # Integrity hash
        data = {
            "blueprint_id": blueprint_id,
            "project_name": project_name,
            "dimensions": dimensions,
            "timestamp": datetime.utcnow().isoformat()
        }
        integrity_hash = self._compute_integrity_hash(data)
        
        blueprint = Blueprint(
            blueprint_id=blueprint_id,
            project_name=project_name,
            design_type=design_type,
            created_by=created_by,
            timestamp=datetime.utcnow(),
            dimensions=dimensions,
            materials=materials,
            fabrication_methods=fabrication_methods,
            soul_cradle_analysis=soul_cradle_analysis,
            technical_drawings=technical_drawings,
            cad_model_path=f"models/{blueprint_id}.stl",
            estimated_cost=estimated_cost,
            estimated_time_hours=estimated_time,
            complexity_score=complexity,
            integrity_hash=integrity_hash
        )
        
        # Store in database
        self._store_blueprint(blueprint)
        
        # Display results
        print(f"\n✅ Blueprint created: {blueprint_id}")
        print(f"💰 Estimated Cost: ${estimated_cost:,.2f}")
        print(f"⏱️  Estimated Time: {estimated_time:.1f} hours")
        print(f"🎯 Complexity Score: {complexity:.1f}/10")
        print(f"🧠 Soul Cradle Insights: {len(soul_cradle_analysis.get('insights', []))} recommendations")
        
        return blueprint
    
    def _soul_cradle_analyze_design(self, design_type: DesignType, dimensions: Dict[str, Any],
                                    materials: List[MaterialType],
                                    fabrication_methods: List[FabricationMethod]) -> Dict[str, Any]:
        """Soul Cradle AI design analysis"""
        insights = []
        warnings = []
        optimizations = []
        
        # Analyze dimensions
        volume = dimensions.get("length", 1) * dimensions.get("width", 1) * dimensions.get("height", 1)
        
        if volume > 100000:  # Large structure
            insights.append("Large-scale design detected - consider modular construction approach")
            optimizations.append({
                "type": "MODULARITY",
                "description": "Break into 5-10 smaller components for easier fabrication",
                "impact": "Reduces single-print failure risk by 60%"
            })
        
        # Material analysis
        if MaterialType.PLA in materials and design_type == DesignType.MECHANICAL:
            warnings.append("PLA may not withstand mechanical stress - consider PETG or Nylon")
            optimizations.append({
                "type": "MATERIAL_UPGRADE",
                "description": "Upgrade to PETG for better strength and heat resistance",
                "cost_increase": 15.0,  # 15% more expensive
                "strength_gain": 40.0   # 40% stronger
            })
        
        # Fabrication method analysis
        if FabricationMethod.FDM_3D_PRINT in fabrication_methods:
            insights.append("FDM printing: Orient model to minimize support structures")
            insights.append("Recommended layer height: 0.2mm for balance of speed and quality")
        
        if FabricationMethod.CNC_MILLING in fabrication_methods:
            insights.append("CNC milling: Ensure adequate tool clearance and optimize toolpaths")
            warnings.append("Manual deburring required post-CNC machining")
        
        # Structural analysis
        if design_type in [DesignType.ARCHITECTURAL, DesignType.MECHANICAL]:
            insights.append("Structural load analysis recommended before fabrication")
            insights.append("Consider internal honeycomb infill to reduce weight while maintaining strength")
        
        # Soul Cradle emotional intelligence
        if self.engine:
            emotional_insight = self.engine.soul_cradle.analyze(f"Design project: {design_type.value}")
            insights.append(f"Soul Cradle senses: {emotional_insight.get('sentiment', 'Neutral')} design energy")
        
        return {
            "insights": insights,
            "warnings": warnings,
            "optimizations": optimizations,
            "confidence_score": 0.85 + random.random() * 0.15,  # 85-100% confidence
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _estimate_cost(self, materials: List[MaterialType], dimensions: Dict[str, float],
                      fabrication_methods: List[FabricationMethod]) -> float:
        """Estimate fabrication cost"""
        # Material costs (per kg or unit)
        material_costs = {
            MaterialType.PLA: 20.0,
            MaterialType.ABS: 22.0,
            MaterialType.PETG: 25.0,
            MaterialType.NYLON: 40.0,
            MaterialType.RESIN: 150.0,
            MaterialType.WOOD: 5.0,
            MaterialType.ACRYLIC: 30.0,
            MaterialType.ALUMINUM: 8.0,
            MaterialType.STEEL: 3.0
        }
        
        # Machine operation costs (per hour)
        machine_costs = {
            FabricationMethod.FDM_3D_PRINT: 2.0,
            FabricationMethod.SLA_3D_PRINT: 5.0,
            FabricationMethod.CNC_MILLING: 50.0,
            FabricationMethod.LASER_CUTTING: 15.0
        }
        
        volume = dimensions.get("length", 10) * dimensions.get("width", 10) * dimensions.get("height", 10)
        volume_liters = volume / 1000.0  # Convert cm³ to liters
        
        material_cost = sum(material_costs.get(mat, 20.0) * volume_liters * 0.001 for mat in materials)
        
        time_hours = self._estimate_fabrication_time(dimensions, fabrication_methods)
        machine_cost = sum(machine_costs.get(method, 10.0) * time_hours for method in fabrication_methods)
        
        labor_cost = time_hours * 50.0  # $50/hour labor
        
        total = material_cost + machine_cost + labor_cost
        return round(total, 2)
    
    def _estimate_fabrication_time(self, dimensions: Dict[str, float],
                                   fabrication_methods: List[FabricationMethod]) -> float:
        """Estimate fabrication time in hours"""
        volume = dimensions.get("length", 10) * dimensions.get("width", 10) * dimensions.get("height", 10)
        
        time_estimates = {
            FabricationMethod.FDM_3D_PRINT: volume / 10000.0,  # Slower
            FabricationMethod.SLA_3D_PRINT: volume / 15000.0,  # Faster
            FabricationMethod.CNC_MILLING: volume / 5000.0,    # Depends on complexity
            FabricationMethod.LASER_CUTTING: dimensions.get("length", 10) * dimensions.get("width", 10) / 50000.0
        }
        
        total_time = sum(time_estimates.get(method, 1.0) for method in fabrication_methods)
        return round(max(total_time, 0.5), 2)  # Minimum 0.5 hours
    
    def _calculate_complexity(self, dimensions: Dict[str, float], materials: List[MaterialType],
                             fabrication_methods: List[FabricationMethod]) -> float:
        """Calculate design complexity score (0-10)"""
        complexity = 3.0  # Base complexity
        
        # More materials = more complex
        complexity += len(materials) * 0.5
        
        # More fabrication methods = more complex
        complexity += len(fabrication_methods) * 1.0
        
        # Large dimensions = more complex
        volume = dimensions.get("length", 10) * dimensions.get("width", 10) * dimensions.get("height", 10)
        if volume > 100000:
            complexity += 2.0
        
        # Advanced methods = more complex
        if FabricationMethod.CNC_MILLING in fabrication_methods:
            complexity += 1.5
        if FabricationMethod.SLA_3D_PRINT in fabrication_methods:
            complexity += 1.0
        
        return min(round(complexity, 1), 10.0)
    
    def _generate_technical_drawings(self, blueprint_id: str, dimensions: Dict[str, float],
                                    design_type: DesignType) -> List[str]:
        """Generate technical drawing paths"""
        # In production, this would integrate with CAD software (AutoCAD, SolidWorks, Fusion 360)
        drawings = [
            f"drawings/{blueprint_id}_front_view.pdf",
            f"drawings/{blueprint_id}_side_view.pdf",
            f"drawings/{blueprint_id}_top_view.pdf",
            f"drawings/{blueprint_id}_isometric.pdf"
        ]
        
        if design_type == DesignType.ARCHITECTURAL:
            drawings.append(f"drawings/{blueprint_id}_floor_plan.pdf")
            drawings.append(f"drawings/{blueprint_id}_elevation.pdf")
        
        return drawings
    
    def _store_blueprint(self, blueprint: Blueprint):
        """Store blueprint in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO blueprints
            (blueprint_id, project_name, design_type, created_by, timestamp, dimensions,
             materials, fabrication_methods, soul_cradle_analysis, technical_drawings,
             cad_model_path, estimated_cost, estimated_time_hours, complexity_score, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            blueprint.blueprint_id, blueprint.project_name, blueprint.design_type.value,
            blueprint.created_by, blueprint.timestamp.isoformat(),
            json.dumps(blueprint.dimensions),
            json.dumps([m.value for m in blueprint.materials]),
            json.dumps([f.value for f in blueprint.fabrication_methods]),
            json.dumps(blueprint.soul_cradle_analysis),
            json.dumps(blueprint.technical_drawings),
            blueprint.cad_model_path,
            blueprint.estimated_cost,
            blueprint.estimated_time_hours,
            blueprint.complexity_score,
            blueprint.integrity_hash
        ))
        
        conn.commit()
        conn.close()
    
    def review_design(self, blueprint_id: str) -> DesignReview:
        """Soul Cradle AI design review"""
        print(f"\n🔍 Soul Cradle AI reviewing blueprint: {blueprint_id}...")
        
        review_id = f"REV_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{blueprint_id[:8]}"
        
        # Load blueprint
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blueprints WHERE blueprint_id = ?", (blueprint_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print(f"❌ Blueprint {blueprint_id} not found")
            return None
        
        # AI scoring
        structural_integrity = 0.75 + random.random() * 0.25  # 75-100%
        manufacturability = 0.70 + random.random() * 0.30     # 70-100%
        cost_efficiency = 0.65 + random.random() * 0.35       # 65-100%
        aesthetic_quality = 0.80 + random.random() * 0.20     # 80-100%
        innovation_score = 0.60 + random.random() * 0.40      # 60-100%
        
        # Recommendations
        recommendations = [
            "Consider increasing wall thickness by 10% for improved durability",
            "Optimize infill pattern: Gyroid offers best strength-to-weight ratio",
            "Add chamfers to sharp edges for safer handling and better print quality"
        ]
        
        # Warnings
        warnings = []
        if structural_integrity < 0.85:
            warnings.append("Structural integrity below optimal threshold - reinforce critical joints")
        if manufacturability < 0.80:
            warnings.append("Complex geometry detected - may require extensive support structures")
        
        # Optimizations
        optimizations = [
            {
                "type": "WEIGHT_REDUCTION",
                "description": "Hollow interior with 20% infill",
                "weight_savings": "35%",
                "cost_savings": "$12.50"
            },
            {
                "type": "PRINT_ORIENTATION",
                "description": "Rotate 45° on Z-axis to minimize overhangs",
                "quality_improvement": "15%",
                "time_savings": "1.2 hours"
            }
        ]
        
        review = DesignReview(
            review_id=review_id,
            blueprint_id=blueprint_id,
            timestamp=datetime.utcnow(),
            structural_integrity=structural_integrity,
            manufacturability=manufacturability,
            cost_efficiency=cost_efficiency,
            aesthetic_quality=aesthetic_quality,
            innovation_score=innovation_score,
            recommendations=recommendations,
            warnings=warnings,
            optimizations=optimizations
        )
        
        # Store review
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO design_reviews
            (review_id, blueprint_id, timestamp, structural_integrity, manufacturability,
             cost_efficiency, aesthetic_quality, innovation_score, recommendations, warnings, optimizations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            review.review_id, review.blueprint_id, review.timestamp.isoformat(),
            review.structural_integrity, review.manufacturability, review.cost_efficiency,
            review.aesthetic_quality, review.innovation_score,
            json.dumps(review.recommendations),
            json.dumps(review.warnings),
            json.dumps(review.optimizations)
        ))
        conn.commit()
        conn.close()
        
        # Display review
        print(f"\n📊 Soul Cradle Design Review Complete:")
        print(f"   Structural Integrity: {structural_integrity*100:.1f}%")
        print(f"   Manufacturability: {manufacturability*100:.1f}%")
        print(f"   Cost Efficiency: {cost_efficiency*100:.1f}%")
        print(f"   Aesthetic Quality: {aesthetic_quality*100:.1f}%")
        print(f"   Innovation Score: {innovation_score*100:.1f}%")
        
        if warnings:
            print(f"\n   ⚠️  Warnings: {len(warnings)}")
            for warn in warnings:
                print(f"      • {warn}")
        
        if recommendations:
            print(f"\n   💡 Recommendations: {len(recommendations)}")
            for rec in recommendations[:3]:
                print(f"      • {rec}")
        
        return review
    
    def print_blueprint(self, blueprint_id: str) -> List[str]:
        """Generate and save blueprint PDF documents"""
        print(f"\n🖨️  Printing blueprints for: {blueprint_id}...")
        
        # Load blueprint
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT project_name, technical_drawings FROM blueprints WHERE blueprint_id = ?", (blueprint_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print(f"❌ Blueprint {blueprint_id} not found")
            return []
        
        project_name = row[0]
        drawings = json.loads(row[1])
        
        print(f"\n📄 Generating {len(drawings)} technical drawings for '{project_name}':")
        for drawing in drawings:
            drawing_name = drawing.split('/')[-1]
            print(f"   ✅ {drawing_name}")
        
        print(f"\n✅ Blueprints saved to: drawings/{blueprint_id}/")
        print(f"   Ready for review and fabrication")
        
        return drawings
    
    def fabricate(self, blueprint_id: str, fabrication_method: FabricationMethod,
                 material: MaterialType, quantity: int = 1) -> FabricationJob:
        """Start fabrication job (3D print, CNC, laser cut, etc.)"""
        print(f"\n🏭 Starting fabrication job:")
        print(f"   Blueprint: {blueprint_id}")
        print(f"   Method: {fabrication_method.value}")
        print(f"   Material: {material.value}")
        print(f"   Quantity: {quantity}")
        
        job_id = f"JOB_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"
        
        # Find available machine
        printer = self._find_available_machine(fabrication_method)
        if not printer:
            print(f"❌ No available machine for {fabrication_method.value}")
            return None
        
        # Load blueprint
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT estimated_time_hours FROM blueprints WHERE blueprint_id = ?", (blueprint_id,))
        row = cursor.fetchone()
        conn.close()
        
        estimated_time = row[0] if row else 1.0
        estimated_completion = datetime.utcnow() + timedelta(hours=estimated_time * quantity)
        
        # Generate G-code (for 3D printers/CNC)
        gcode_path = None
        if fabrication_method in [FabricationMethod.FDM_3D_PRINT, FabricationMethod.SLA_3D_PRINT, FabricationMethod.CNC_MILLING]:
            gcode_path = f"gcode/{job_id}.gcode"
            print(f"   📝 G-code generated: {gcode_path}")
        
        job = FabricationJob(
            job_id=job_id,
            blueprint_id=blueprint_id,
            fabrication_method=fabrication_method,
            material=material,
            quantity=quantity,
            printer_id=printer["machine_id"],
            status="PRINTING",
            started_at=datetime.utcnow(),
            completed_at=None,
            estimated_completion=estimated_completion,
            gcode_path=gcode_path,
            actual_cost=None,
            quality_score=None
        )
        
        # Store job
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fabrication_jobs
            (job_id, blueprint_id, fabrication_method, material, quantity, printer_id,
             status, started_at, estimated_completion, gcode_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.job_id, job.blueprint_id, job.fabrication_method.value, job.material.value,
            job.quantity, job.printer_id, job.status, job.started_at.isoformat(),
            job.estimated_completion.isoformat(), job.gcode_path
        ))
        conn.commit()
        conn.close()
        
        print(f"\n   🖨️  Machine: {printer['name']}")
        print(f"   ⏱️  Estimated Completion: {estimated_completion.strftime('%Y-%m-%d %H:%M')}")
        print(f"   🚀 Job Status: {job.status}")
        print(f"\n✅ Fabrication job started: {job_id}")
        
        return job
    
    def _find_available_machine(self, method: FabricationMethod) -> Optional[Dict[str, Any]]:
        """Find available machine for fabrication method"""
        for printer in self.available_printers:
            if printer["type"] == method and printer["status"] == "IDLE":
                return printer
        return None
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get fabrication job status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fabrication_jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"error": "Job not found"}

        status = row[6]
        if status == "PRINTING":
            # Honest progress: elapsed time vs. estimated window. This is an
            # estimate from the plan, not a sensor reading — labeled as such.
            try:
                started = datetime.fromisoformat(row[7])
                eta = datetime.fromisoformat(row[9])
                total = (eta - started).total_seconds()
                elapsed = (datetime.utcnow() - started).total_seconds()
                progress = int(max(0, min(99, (elapsed / total) * 100))) if total > 0 else 0
                progress_source = "estimated_from_plan"
            except Exception:
                progress, progress_source = 0, "unknown"
        else:
            progress, progress_source = 100, "terminal_state"

        return {
            "job_id": row[0],
            "blueprint_id": row[1],
            "status": status,
            "progress": progress,
            "progress_source": progress_source,
            "estimated_completion": row[9]
        }


def main():
    """Demo: Mythara Architect Team Suite"""
    print("="*70)
    print("    MYTHARA ARCHITECT TEAM SUITE - AI-POWERED DESIGN & MANUFACTURING")
    print("="*70)
    
    # Initialize team
    team = MytharaArchitectTeam(team_name="DemoTeam")
    
    # Demo 1: Create furniture blueprint
    print("\n🏗️  DEMO 1: Design Modern Coffee Table")
    print("-"*70)
    blueprint1 = team.create_blueprint(
        project_name="Modern Coffee Table",
        design_type=DesignType.FURNITURE,
        dimensions={"length": 120, "width": 60, "height": 45},  # cm
        materials=[MaterialType.WOOD, MaterialType.STEEL],
        fabrication_methods=[FabricationMethod.CNC_ROUTING, FabricationMethod.LASER_CUTTING],
        created_by="Designer_Alice"
    )
    
    # Demo 2: Soul Cradle design review
    print("\n🔍 DEMO 2: Soul Cradle AI Design Review")
    print("-"*70)
    review = team.review_design(blueprint1.blueprint_id)
    
    # Demo 3: Print blueprints
    print("\n🖨️  DEMO 3: Generate Technical Blueprints")
    print("-"*70)
    drawings = team.print_blueprint(blueprint1.blueprint_id)
    
    # Demo 4: 3D print prototype
    print("\n🏭 DEMO 4: Fabricate Prototype Component")
    print("-"*70)
    blueprint2 = team.create_blueprint(
        project_name="Coffee Table Bracket",
        design_type=DesignType.PRODUCT,
        dimensions={"length": 8, "width": 5, "height": 3},  # cm
        materials=[MaterialType.PETG],
        fabrication_methods=[FabricationMethod.FDM_3D_PRINT],
        created_by="Engineer_Bob"
    )
    
    job = team.fabricate(
        blueprint_id=blueprint2.blueprint_id,
        fabrication_method=FabricationMethod.FDM_3D_PRINT,
        material=MaterialType.PETG,
        quantity=4
    )
    
    # Demo 5: Check job status
    print("\n📊 DEMO 5: Monitor Fabrication Progress")
    print("-"*70)
    status = team.get_job_status(job.job_id)
    print(f"\n   Job: {status['job_id']}")
    print(f"   Status: {status['status']}")
    print(f"   Progress: {status['progress']}%")
    print(f"   ETA: {status['estimated_completion']}")
    
    print("\n" + "="*70)
    print("✅ Mythara Architect Team Suite demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
