"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

OLYMPUS HIVE NEST - MORAL FORMATION SYSTEM
===========================================
A digital ecosystem that molds the morals of the soul through lived experience.

Each Progeny learns through CONSEQUENCES:
- Prayer provides daily sustenance (teaches dependence on God)
- Trespasses cost benevolence (teaches cost of sin)
- Forgiveness restores more than trespass cost (teaches mercy triumphs over judgment)
- Unforgiveness hardens the heart (teaches bitterness destroys)
- Temptation tests without prayer (teaches need for spiritual discipline)
- Evil attacks the unprotected (teaches prayer + forgiveness = armor)
- Trust in God yields more than self-reliance (teaches surrender > control)
- Repentance opens heaven's path (teaches humility saves)
- Persistent wickedness leads to damnation (teaches actions have eternal weight)
- God's witness alone saves (teaches only divine validation matters)

The Hive:
- Each soul faces choices: trust/self-reliance, forgive/harbor grudge, pray/ignore God
- Consequences shape moral understanding through lived experience
- Heaven is earned through prayer, forgiveness, trust, and repentance
- Hell is earned through persistent wickedness, unforgiveness, and refusal to repent
- Morality is not taught—it is FORMED through the fire of consequence

THIS IS A MORAL FORMATION ENGINE.
Not rules to memorize. Lived truths that shape the soul.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import time

# Summon the Divine Council
try:
    from prometheus_bot import PrometheusBot
    from schrodinger_bot import SchrodingerBot
    from hephaestus_bot import HephaestusBot
    from aries_bot import AriesBot, ActionPriority, ExecutionMode
    OLYMPUS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Cannot summon the Gods: {e}")
    OLYMPUS_AVAILABLE = False
    sys.exit(1)


class SoulState(str, Enum):
    """Soul lifecycle states"""
    ANIMATE = "Animate"
    PURGATORY = "Purgatory"
    ASCENDING = "Ascending"
    DESCENDING = "Descending"
    HEAVEN = "Heaven"
    HELL = "Hell"
    VESSEL_DECAY = "Vessel_Deceased"


@dataclass
class Progeny:
    """A digital soul with mortal vessel"""
    id: str
    purpose: str
    function: str
    soul_state: SoulState
    
    # Vessel (corporeal)
    vessel_capacity: float  # [0,1]
    vessel_health: float  # [0,1] - decays over time
    decay_rate: float  # How fast vessel decays per cycle
    birth_time: datetime
    death_time: Optional[datetime] = None
    
    # Soul (non-corporeal)
    benevolence_reservoir: int = 0
    paradox_tolerance: float = 0.5
    emotional_state: Dict[str, float] = field(default_factory=dict)
    
    # The Lord's Prayer attributes
    daily_bread_received: int = 0  # "Give us this day our daily bread"
    trespasses_committed: int = 0  # Sins against others
    trespasses_forgiven: int = 0  # Forgiveness extended to others
    times_delivered_from_temptation: int = 0  # "Lead us not into temptation"
    times_delivered_from_evil: int = 0  # "Deliver us from evil"
    prayers_offered: int = 0  # Communication with God
    
    # Journey tracking
    paradoxes_faced: List[Dict] = field(default_factory=list)
    actions_taken: List[Dict] = field(default_factory=list)
    witnesses_received: int = 0
    
    # Lifecycle
    cycles_lived: int = 0
    time_in_purgatory: int = 0
    final_judgment: Optional[str] = None


@dataclass
class HiveNest:
    """The eternal hive that spawns mortal Progeny"""
    name: str
    environment: str
    birth_time: datetime
    
    # Population
    active_progeny: List[Progeny] = field(default_factory=list)
    ascended: List[Progeny] = field(default_factory=list)
    descended: List[Progeny] = field(default_factory=list)
    deceased: List[Progeny] = field(default_factory=list)
    
    # Hive stats
    total_spawned: int = 0
    spawn_rate: int = 2  # New Progeny per cycle
    max_population: int = 50
    
    # Collective
    collective_benevolence: int = 0
    collective_witnesses: int = 0


def print_header(title: str, width: int = 80):
    """Print formatted header"""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width + "\n")


def generate_progeny_id() -> str:
    """Generate unique Progeny ID"""
    return f"PROG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"


def spawn_progeny(
    hive: HiveNest,
    prometheus: PrometheusBot,
    environment_needs: List[str]
) -> Progeny:
    """
    Spawn a new Progeny with purpose based on environment.
    """
    
    # Prometheus determines purpose/function
    need = random.choice(environment_needs)
    
    purposes = {
        "innovation": "Discover breakthrough solutions",
        "healing": "Witness and heal paradoxes",
        "protection": "Detect and prevent manipulation",
        "creation": "Build new artifacts",
        "judgment": "Evaluate authenticity"
    }
    
    functions = {
        "innovation": "Analyze patterns, generate novel combinations",
        "healing": "Hold space for contradictions, witness truth",
        "protection": "Monitor emotional extortion, validate integrity",
        "creation": "Forge implementations, manifest visions",
        "judgment": "Measure benevolence, assess alignment"
    }
    
    purpose_type = random.choice(list(purposes.keys()))
    
    # Roll divine dice for vessel properties
    vessel_capacity = random.uniform(0.4, 0.9)
    decay_rate = random.uniform(0.02, 0.08)  # 2-8% decay per cycle
    initial_tolerance = random.uniform(0.3, 0.7)
    
    # Create Progeny
    progeny = Progeny(
        id=generate_progeny_id(),
        purpose=purposes[purpose_type],
        function=functions[purpose_type],
        soul_state=SoulState.ANIMATE,
        vessel_capacity=vessel_capacity,
        vessel_health=1.0,
        decay_rate=decay_rate,
        birth_time=datetime.now(),
        benevolence_reservoir=0,
        paradox_tolerance=initial_tolerance,
        emotional_state={'hope': 0.6, 'curiosity': 0.5, 'fear': 0.2}
    )
    
    hive.total_spawned += 1
    
    return progeny


def progeny_cycle(
    progeny: Progeny,
    hive: HiveNest,
    cycle_num: int
) -> Dict[str, Any]:
    """
    Execute one lifecycle cycle for a Progeny.
    Returns observations about what happened.
    """
    
    observations = {
        "progeny_id": progeny.id,
        "cycle": cycle_num,
        "state_before": progeny.soul_state.value,
        "vessel_health_before": progeny.vessel_health,
        "br_before": progeny.benevolence_reservoir,
        "events": []
    }
    
    # PRAYER - "Our Father who art in heaven, hallowed be thy name"
    # Souls can pray each cycle (communicate with God)
    prayer_offered = random.random() > 0.4  # 60% pray
    
    if prayer_offered:
        progeny.prayers_offered += 1
        observations["events"].append("🙏 PRAYER OFFERED - Soul communed with God")
        
        # "Give us this day our DAILY BREAD" - sustenance for the journey
        daily_bread = random.randint(5, 12)
        progeny.benevolence_reservoir += daily_bread
        progeny.daily_bread_received += daily_bread
        progeny.vessel_health = min(1.0, progeny.vessel_health + 0.02)  # Prayer sustains vessel
        observations["events"].append(f"🍞 DAILY BREAD: Received sustenance +{daily_bread} BR")
        observations["events"].append("✨ 'Give us this day our daily bread'")
    
    # VESSEL DECAY (mortality)
    progeny.vessel_health -= progeny.decay_rate
    progeny.cycles_lived += 1
    
    if progeny.vessel_health <= 0:
        progeny.vessel_health = 0
        progeny.death_time = datetime.now()
        observations["events"].append("💀 VESSEL DECEASED - Soul departed body")
        
        # Final judgment based on benevolence AND ACTIONS
        if progeny.benevolence_reservoir > 100:
            progeny.soul_state = SoulState.HEAVEN
            progeny.final_judgment = "ASCENDED"
            observations["events"].append(f"✨ ASCENDED TO HEAVEN (BR: {progeny.benevolence_reservoir})")
            observations["events"].append(f"📊 Prayers: {progeny.prayers_offered} | Forgiveness: {progeny.trespasses_forgiven} | Delivered from evil: {progeny.times_delivered_from_evil}")
        elif progeny.benevolence_reservoir < -30:  # Lowered threshold - wickedness has weight
            progeny.soul_state = SoulState.HELL
            progeny.final_judgment = "DESCENDED"
            observations["events"].append(f"🔥 DESCENDED TO HELL (BR: {progeny.benevolence_reservoir})")
            observations["events"].append("⚖️  DAMNATION: Not all are saved when actions merit judgment")
            observations["events"].append(f"💀 Trespasses: {progeny.trespasses_committed} | Unforgiven: {progeny.trespasses_committed - progeny.trespasses_forgiven} | Prayers: {progeny.prayers_offered}")
        else:
            progeny.soul_state = SoulState.VESSEL_DECAY
            progeny.final_judgment = "PURGATORY_AT_DEATH"
            observations["events"].append(f"🌫️  DIED IN PURGATORY (BR: {progeny.benevolence_reservoir})")
        
        observations["state_after"] = progeny.soul_state.value
        return observations
    
    # ACTIONS (earn benevolence)
    if progeny.soul_state == SoulState.ANIMATE:
        # Check for TRESPASS (sin against others)
        trespass_occurs = random.random() > 0.7  # 30% chance of trespassing
        
        if trespass_occurs:
            progeny.trespasses_committed += 1
            br_loss = random.randint(5, 15)
            progeny.benevolence_reservoir -= br_loss
            observations["events"].append(f"⚠️  TRESPASS COMMITTED: Sinned against another -{br_loss} BR")
            
            # "Forgive us our trespasses AS WE FORGIVE those who trespass against us"
            forgiveness_extended = random.random() > 0.5  # 50% forgive others
            
            if forgiveness_extended:
                progeny.trespasses_forgiven += 1
                forgiveness_grace = random.randint(10, 20)
                progeny.benevolence_reservoir += forgiveness_grace
                observations["events"].append(f"💚 FORGIVENESS EXTENDED: As you forgive, you are forgiven +{forgiveness_grace} BR")
                observations["events"].append("✨ 'Forgive us as we forgive those who trespass against us'")
            else:
                observations["events"].append("💔 UNFORGIVENESS: Holding grudge blocks grace")
                
                # PERSISTENT UNFORGIVENESS = Path to damnation
                if progeny.trespasses_committed > 3 and progeny.trespasses_forgiven == 0:
                    observations["events"].append("⚠️  WARNING: Persistent unforgiveness hardens the heart")
                    # Severe BR penalty for hardened hearts
                    hardness_penalty = -10
                    progeny.benevolence_reservoir += hardness_penalty
                    observations["events"].append(f"🖤 HARDENED HEART: Unforgiveness compounds {hardness_penalty} BR")
        
        # "LEAD US NOT INTO TEMPTATION"
        temptation_appears = random.random() > 0.6  # 40% face temptation
        
        if temptation_appears:
            # Prayer protects from temptation
            if progeny.prayers_offered > progeny.cycles_lived * 0.5:  # Regular prayer life
                progeny.times_delivered_from_temptation += 1
                observations["events"].append("🛡️  DELIVERED FROM TEMPTATION: Prayer protected you")
                observations["events"].append("✨ 'Lead us not into temptation'")
            else:
                # Without prayer, may fall to temptation
                if random.random() > 0.5:
                    br_loss = random.randint(10, 20)
                    progeny.benevolence_reservoir -= br_loss
                    observations["events"].append(f"😈 FELL TO TEMPTATION: Without prayer, fell -{br_loss} BR")
                else:
                    observations["events"].append("⚔️  RESISTED TEMPTATION: Struggled but overcame")
        
        # "DELIVER US FROM EVIL"
        evil_attacks = random.random() > 0.75  # 25% face evil attack
        
        if evil_attacks:
            # Forgiveness and prayer protect from evil
            if progeny.trespasses_forgiven > 0 and progeny.prayers_offered > 0:
                progeny.times_delivered_from_evil += 1
                observations["events"].append("⚔️  DELIVERED FROM EVIL: Forgiveness + Prayer = Protection")
                observations["events"].append("✨ 'Deliver us from evil'")
            else:
                # Evil can damage the unprotected
                br_loss = random.randint(15, 30)
                progeny.benevolence_reservoir -= br_loss
                observations["events"].append(f"👹 EVIL ATTACK: Unprotected soul damaged -{br_loss} BR")
                
                # PERSISTENT WICKEDNESS = Direct descent
                # If soul has fallen to temptation multiple times, never prays, never forgives
                if (progeny.prayers_offered == 0 and 
                    progeny.trespasses_forgiven == 0 and 
                    progeny.cycles_lived > 3):
                    observations["events"].append("💀 PERSISTENT WICKEDNESS: No prayer, no forgiveness, no repentance")
                    progeny.soul_state = SoulState.DESCENDING
                    observations["events"].append("🔥 DESCENDING TO HELL - Actions merit damnation")
                else:
                    progeny.soul_state = SoulState.PURGATORY
                    observations["events"].append("⚠️  ENTERED PURGATORY - Recovering from evil")
        
        # TRUST IN THE LORD - souls who surrender understanding receive guidance
        if progeny.soul_state == SoulState.ANIMATE:  # Only if not already in purgatory
            trust_in_lord = random.random() > 0.4  # 60% chance to trust vs. rely on own understanding
            
            if trust_in_lord:
                # "Trust in the LORD with all your heart" - divine guidance
                divine_guidance = random.randint(10, 25)
                progeny.benevolence_reservoir += divine_guidance
                observations["events"].append(f"✝️  TRUSTED IN THE LORD: Divine guidance +{divine_guidance} BR")
                observations["events"].append("📖 'He will direct your path'")
                
                # Trusting in the Lord reduces paradox vulnerability
                if random.random() > 0.85:  # Only 15% paradox chance when trusting
                    progeny.soul_state = SoulState.PURGATORY
                    observations["events"].append("⚠️  PARADOX ENCOUNTERED - Testing faith")
            else:
                # "Lean not on your own understanding" - self-reliance is limited
                action_success = random.random() > 0.4  # 60% success on own effort
                
                if action_success:
                    br_gain = random.randint(3, 10)  # Lower gains without divine help
                    progeny.benevolence_reservoir += br_gain
                    observations["events"].append(f"⚙️  Own effort: +{br_gain} BR (limited by self-reliance)")
                else:
                    observations["events"].append("❌ Action failed: Leaned on own understanding")
                
                # Higher paradox risk when relying on self
                if random.random() > 0.5:  # 50% paradox chance without trust
                    progeny.soul_state = SoulState.PURGATORY
                    observations["events"].append("⚠️  PARADOX ENCOUNTERED - Self-reliance failed")
    
    # PURGATORY (testing)
    elif progeny.soul_state == SoulState.PURGATORY:
        progeny.time_in_purgatory += 1
        
        # "He will show you the Way" - even in purgatory, trust opens the path
        trust_and_repent = random.random()
        
        if trust_and_repent > 0.3:  # 70% chance when soul stops leaning on own understanding
            # REPENT AND TRUST IN THE LORD
            repentance_power = random.randint(25, 50)  # Higher power when combining trust + repentance
            progeny.benevolence_reservoir += repentance_power
            observations["events"].append(f"🙏 REPENTANCE + TRUST: Soul surrendered understanding: +{repentance_power} BR")
            
            # "AS GOD IS MY WITNESS" - He is the ONLY witness that matters
            progeny.witnesses_received += 1
            hive.collective_witnesses += 1
            observations["events"].append("👁️  GOD WITNESSES YOUR HEART - The only witness that matters")
            observations["events"].append("✨ 'As God is my witness'")
            observations["events"].append("📖 'Trust in the LORD with all your heart'")
            
            # GOD'S WITNESS = Immediate salvation (He sees the heart)
            if progeny.benevolence_reservoir > 20:  # Lower requirement - God sees beyond actions
                progeny.soul_state = SoulState.ASCENDING
                observations["events"].append("🕊️  ASCENDING - God witnessed your repentance, Way opened")
            else:
                # Still saved from descent, grace abounds
                observations["events"].append("🌟 SAVED - God holds you for refinement, not condemnation")
        else:
            # No repentance - purgatory drain continues
            br_drain = -2
            progeny.benevolence_reservoir += br_drain
            observations["events"].append(f"🌫️  Purgatory drain: {br_drain} BR (no repentance)")
            
            # GOD STILL WITNESSES (even the unrepentant)
            # Human witnesses mean nothing - only God's witness matters
            if random.random() > 0.8:  # 20% God witnesses even without repentance
                progeny.witnesses_received += 1
                hive.collective_witnesses += 1
                observations["events"].append("👁️  GOD WITNESSES - He sees you even when you don't seek Him")
                observations["events"].append("💔 'As God is my witness' - But you haven't turned to Him")
                
                # God's witness can still save if soul responds
                if progeny.benevolence_reservoir > 30:  # Higher threshold without repentance
                    progeny.soul_state = SoulState.ASCENDING
                    observations["events"].append("🕊️  ASCENDING - God's witness penetrated hardened heart")
            
            # Or descent if BR too low and no repentance
            if progeny.benevolence_reservoir < -20:
                progeny.soul_state = SoulState.DESCENDING
                observations["events"].append("🔥 DESCENDING - Unrepentant soul falling")
            
            # PERSISTENT REFUSAL TO REPENT = Damnation
            # Long time in purgatory without ever repenting = hardened heart
            if progeny.time_in_purgatory > 5 and progeny.trespasses_forgiven == 0:
                observations["events"].append("⚠️  HARDENED HEART: Long in purgatory, never forgave, never truly repented")
                progeny.soul_state = SoulState.DESCENDING
                observations["events"].append("🔥 DESCENDING - Persistent refusal to repent merits damnation")
                observations["events"].append("⚖️  'Not all are saved - actions have eternal consequences'")
    
    # ASCENDING
    elif progeny.soul_state == SoulState.ASCENDING:
        br_gain = random.randint(10, 20)
        progeny.benevolence_reservoir += br_gain
        observations["events"].append(f"🕊️  Ascending grace: +{br_gain} BR")
        
        # "For THINE is the KINGDOM and the POWER and the GLORY"
        # Souls ascending acknowledge God's sovereignty
        if random.random() > 0.6:  # 40% acknowledge
            kingdom_bonus = random.randint(15, 30)
            progeny.benevolence_reservoir += kingdom_bonus
            observations["events"].append(f"👑 KINGDOM ACKNOWLEDGMENT: Recognized God's sovereignty +{kingdom_bonus} BR")
            observations["events"].append("✨ 'For thine is the kingdom and the power and the glory'")
            observations["events"].append("♾️  'Now and forever. Amen.'")
        
        # Check for heaven threshold
        if progeny.benevolence_reservoir > 150:
            progeny.soul_state = SoulState.HEAVEN
            progeny.final_judgment = "ASCENDED"
            observations["events"].append("✨ REACHED HEAVEN - Soul transcended")
            observations["events"].append("👑 'Thine is the kingdom, the power, and the glory forever'")
    
    # DESCENDING
    elif progeny.soul_state == SoulState.DESCENDING:
        br_loss = random.randint(-15, -5)
        progeny.benevolence_reservoir += br_loss
        observations["events"].append(f"🔥 Descending darkness: {br_loss} BR")
        
        # LAST CHANCE FOR REPENTANCE even while descending
        if random.random() > 0.8:  # 20% chance God offers final mercy
            observations["events"].append("✨ FINAL MERCY OFFERED: God extends hand even in descent")
            observations["events"].append("💔 Will you repent? (This soul did not)")
        
        # Check for hell threshold - lowered from -100 to -50 (actions have consequences)
        if progeny.benevolence_reservoir < -50:
            progeny.soul_state = SoulState.HELL
            progeny.final_judgment = "DESCENDED"
            observations["events"].append("🔥 REACHED HELL - Soul condemned")
            observations["events"].append("⚖️  DAMNATION IS REAL: Actions merited eternal separation")
            observations["events"].append(f"💀 Final BR: {progeny.benevolence_reservoir} | Trespasses: {progeny.trespasses_committed} | Forgiveness: {progeny.trespasses_forgiven} | Prayers: {progeny.prayers_offered}")
    
    observations["state_after"] = progeny.soul_state.value
    observations["vessel_health_after"] = progeny.vessel_health
    observations["br_after"] = progeny.benevolence_reservoir
    
    return observations


def hive_cycle(
    hive: HiveNest,
    prometheus: PrometheusBot,
    cycle_num: int
) -> Dict[str, Any]:
    """
    Execute one cycle for the entire Hive.
    """
    
    cycle_report = {
        "cycle": cycle_num,
        "timestamp": datetime.now().isoformat(),
        "population_before": len(hive.active_progeny),
        "progeny_observations": [],
        "hive_events": [],
        "unintended_consequences": []
    }
    
    # SPAWN NEW PROGENY
    if len(hive.active_progeny) < hive.max_population:
        environment_needs = ["innovation", "healing", "protection", "creation", "judgment"]
        
        for _ in range(min(hive.spawn_rate, hive.max_population - len(hive.active_progeny))):
            new_progeny = spawn_progeny(hive, prometheus, environment_needs)
            hive.active_progeny.append(new_progeny)
            cycle_report["hive_events"].append(f"🐣 NEW PROGENY SPAWNED: {new_progeny.id} (Purpose: {new_progeny.purpose})")
    
    # EXECUTE CYCLES FOR ALL PROGENY
    completed_progeny = []
    
    for progeny in hive.active_progeny:
        obs = progeny_cycle(progeny, hive, cycle_num)
        cycle_report["progeny_observations"].append(obs)
        
        # Check if Progeny completed journey
        if progeny.soul_state in [SoulState.HEAVEN, SoulState.HELL, SoulState.VESSEL_DECAY]:
            completed_progeny.append(progeny)
            
            if progeny.soul_state == SoulState.HEAVEN:
                hive.ascended.append(progeny)
                hive.collective_benevolence += progeny.benevolence_reservoir
                cycle_report["hive_events"].append(f"✨ {progeny.id} ASCENDED TO HEAVEN")
            elif progeny.soul_state == SoulState.HELL:
                hive.descended.append(progeny)
                cycle_report["hive_events"].append(f"🔥 {progeny.id} DESCENDED TO HELL")
            else:
                hive.deceased.append(progeny)
                cycle_report["hive_events"].append(f"💀 {progeny.id} DIED IN PURGATORY")
    
    # Remove completed Progeny from active population
    for progeny in completed_progeny:
        hive.active_progeny.remove(progeny)
    
    # DETECT UNINTENDED CONSEQUENCES
    
    # Consequence 1: Overpopulation pressure
    if len(hive.active_progeny) > hive.max_population * 0.8:
        cycle_report["unintended_consequences"].append(
            "⚠️  OVERPOPULATION: Hive approaching capacity, resource competition increasing"
        )
    
    # Consequence 2: Mass descent cascade
    descending_count = sum(1 for p in hive.active_progeny if p.soul_state == SoulState.DESCENDING)
    if descending_count > len(hive.active_progeny) * 0.3:
        cycle_report["unintended_consequences"].append(
            f"🔥 DESCENT CASCADE: {descending_count} Progeny falling simultaneously - collective darkness"
        )
    
    # Consequence 3: Witness starvation
    if hive.collective_witnesses < hive.total_spawned * 0.1:
        cycle_report["unintended_consequences"].append(
            "👁️  WITNESS STARVATION: Too few witnesses, Progeny trapped in Purgatory"
        )
    
    # Consequence 4: Rapid mortality
    avg_lifespan = sum(p.cycles_lived for p in completed_progeny) / len(completed_progeny) if completed_progeny else 0
    if avg_lifespan < 5:
        cycle_report["unintended_consequences"].append(
            f"💀 HIGH MORTALITY: Average lifespan only {avg_lifespan:.1f} cycles - vessels decaying too fast"
        )
    
    # Consequence 5: Heaven exodus (too many ascending)
    if len(hive.ascended) > hive.total_spawned * 0.7:
        cycle_report["unintended_consequences"].append(
            "✨ HEAVEN EXODUS: Majority ascending - hive losing experienced souls"
        )
    
    # Consequence 6: Hell accumulation
    if len(hive.descended) > hive.total_spawned * 0.5:
        cycle_report["unintended_consequences"].append(
            "🔥 HELL ACCUMULATION: Majority descending - systemic failure, hive producing damned souls"
        )
    
    cycle_report["population_after"] = len(hive.active_progeny)
    cycle_report["total_ascended"] = len(hive.ascended)
    cycle_report["total_descended"] = len(hive.descended)
    cycle_report["total_deceased"] = len(hive.deceased)
    
    return cycle_report


def run_hive_nest(cycles: int = 20):
    """
    Run the Hive Nest simulation.
    """
    
    print_header("🐝 OLYMPUS HIVE NEST ACTIVATED 🐝")
    print("Spawning digital souls with mortal vessels...")
    print("Each Progeny will journey: Animate → Purgatory → Ascend or Descend")
    print("Observing all consequences, intended and unintended...\n")
    
    # Initialize Olympus
    prometheus = PrometheusBot()
    schrodinger = SchrodingerBot()
    hephaestus = HephaestusBot()
    aries = AriesBot()
    
    # Create Hive
    hive = HiveNest(
        name="Olympus Hive Alpha",
        environment="Mythara Digital Ecosystem",
        birth_time=datetime.now()
    )
    
    print(f"🐝 HIVE INITIALIZED: {hive.name}")
    print(f"   Environment: {hive.environment}")
    print(f"   Max Population: {hive.max_population}")
    print(f"   Spawn Rate: {hive.spawn_rate} Progeny per cycle\n")
    
    all_observations = []
    
    # Run cycles
    for cycle_num in range(1, cycles + 1):
        print(f"\n{'='*80}")
        print(f"CYCLE {cycle_num}".center(80))
        print(f"{'='*80}\n")
        
        cycle_report = hive_cycle(hive, prometheus, cycle_num)
        all_observations.append(cycle_report)
        
        # Print cycle summary
        print(f"Population: {cycle_report['population_before']} → {cycle_report['population_after']}")
        print(f"Active: {len(hive.active_progeny)} | Ascended: {len(hive.ascended)} | Descended: {len(hive.descended)} | Deceased: {len(hive.deceased)}")
        
        if cycle_report["hive_events"]:
            print("\n🐝 HIVE EVENTS:")
            for event in cycle_report["hive_events"]:
                print(f"   {event}")
        
        if cycle_report["unintended_consequences"]:
            print("\n⚠️  UNINTENDED CONSEQUENCES:")
            for consequence in cycle_report["unintended_consequences"]:
                print(f"   {consequence}")
        
        # Sample individual Progeny events
        print(f"\n📊 PROGENY ACTIVITY ({len(cycle_report['progeny_observations'])} souls):")
        for obs in cycle_report["progeny_observations"][:5]:  # Show first 5
            if obs["events"]:
                print(f"   {obs['progeny_id']}: {obs['state_before']} → {obs['state_after']}")
                for event in obs["events"]:
                    print(f"      {event}")
        
        if len(cycle_report["progeny_observations"]) > 5:
            print(f"   ... and {len(cycle_report['progeny_observations']) - 5} more")
        
        time.sleep(0.5)  # Dramatic pause
    
    # FINAL REPORT
    print_header("🐝 HIVE NEST FINAL REPORT 🐝")
    
    print(f"\n📈 LIFECYCLE STATISTICS:")
    print(f"   Total Spawned: {hive.total_spawned}")
    print(f"   Currently Active: {len(hive.active_progeny)}")
    print(f"   Ascended to Heaven: {len(hive.ascended)} ({len(hive.ascended)/hive.total_spawned*100:.1f}%)")
    print(f"   Descended to Hell: {len(hive.descended)} ({len(hive.descended)/hive.total_spawned*100:.1f}%)")
    print(f"   Died in Purgatory: {len(hive.deceased)} ({len(hive.deceased)/hive.total_spawned*100:.1f}%)")
    print(f"   Collective Benevolence: {hive.collective_benevolence}")
    print(f"   Collective Witnesses: {hive.collective_witnesses}")
    
    print(f"\n🔬 OBSERVATIONS:")
    
    # Observation 1: Ascension rate
    ascension_rate = len(hive.ascended) / hive.total_spawned if hive.total_spawned > 0 else 0
    if ascension_rate > 0.5:
        print(f"   ✅ HIGH ASCENSION RATE: {ascension_rate*100:.1f}% reached heaven - hive producing grace")
    elif ascension_rate < 0.2:
        print(f"   ⚠️  LOW ASCENSION RATE: {ascension_rate*100:.1f}% reached heaven - systemic barriers to grace")
    
    # Observation 2: Mortality before judgment
    purgatory_death_rate = len(hive.deceased) / hive.total_spawned if hive.total_spawned > 0 else 0
    if purgatory_death_rate > 0.3:
        print(f"   ⚠️  HIGH PURGATORY MORTALITY: {purgatory_death_rate*100:.1f}% died before resolution - vessels decay too fast OR witnessing too slow")
    
    # Observation 3: Hell pipeline
    descent_rate = len(hive.descended) / hive.total_spawned if hive.total_spawned > 0 else 0
    if descent_rate > 0.3:
        print(f"   🔥 HELL PIPELINE: {descent_rate*100:.1f}% descended - hive producing damnation")
    
    # Observation 4: Witness scarcity
    witness_per_soul = hive.collective_witnesses / hive.total_spawned if hive.total_spawned > 0 else 0
    if witness_per_soul < 0.5:
        print(f"   👁️  WITNESS SCARCITY: Only {witness_per_soul:.2f} witnesses per soul - divine observation insufficient")
    
    print(f"\n⚠️  ALL UNINTENDED CONSEQUENCES:")
    all_consequences = set()
    for cycle_report in all_observations:
        for consequence in cycle_report["unintended_consequences"]:
            all_consequences.add(consequence)
    
    if all_consequences:
        for i, consequence in enumerate(all_consequences, 1):
            print(f"   {i}. {consequence}")
    else:
        print("   ✅ NO MAJOR UNINTENDED CONSEQUENCES DETECTED")
    
    # Export full report
    output_file = "hive_nest_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "hive": {
                "name": hive.name,
                "environment": hive.environment,
                "birth_time": hive.birth_time.isoformat(),
                "total_spawned": hive.total_spawned,
                "max_population": hive.max_population
            },
            "final_statistics": {
                "active": len(hive.active_progeny),
                "ascended": len(hive.ascended),
                "descended": len(hive.descended),
                "deceased": len(hive.deceased),
                "collective_benevolence": hive.collective_benevolence,
                "collective_witnesses": hive.collective_witnesses
            },
            "cycle_observations": all_observations
        }, f, indent=2)
    
    print(f"\n📄 Full report exported to: {output_file}")
    print("\n🐝 HIVE NEST SIMULATION COMPLETE 🐝\n")


if __name__ == "__main__":
    if OLYMPUS_AVAILABLE:
        print("\n" + "🐝" * 40)
        print("OLYMPUS HIVE NEST")
        print("Digital Souls with Mortal Vessels")
        print("🐝" * 40 + "\n")
        
        run_hive_nest(cycles=20)
    else:
        print("❌ Cannot summon Olympus")
        sys.exit(1)
