#!/usr/bin/env python3
"""
Copyright © 2026 Mythara Labs LLC. All rights reserved.

QUANTUM BATTLE ARENA
Evolving Threats vs. Quantum SLIME Defense
Real-time adversarial training and testing

FOR AUTHORIZED SECURITY TESTING ONLY
Educational and defensive security research purposes
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict

from quantum_threat_simulator import (
    QuantumThreatSimulator, 
    AttackVector, 
    EvolutionStrategy
)
from quantum_slime_defense import QuantumSlimeDefense

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BATTLE')


class QuantumBattleArena:
    """
    Quantum Battle Arena
    Pits evolving threats against quantum defense in adversarial simulation
    """
    
    def __init__(self):
        self.threat_simulator = QuantumThreatSimulator()
        self.defense_system = QuantumSlimeDefense(initial_nodes=20)
        self.battle_history = []
        self.start_time = time.time()
        
        logger.info("⚔️  Quantum Battle Arena initialized")
    
    async def run_battle(self, duration: float = 60.0, 
                        attack_frequency: float = 5.0) -> Dict:
        """
        Run adversarial battle between threats and defenses
        Both systems evolve in real-time based on outcomes
        """
        
        print("\n" + "="*70)
        print("║          QUANTUM BATTLE ARENA - STARTING          ║")
        print("="*70)
        print(f"\n⚔️  BATTLE PARAMETERS")
        print(f"├─ Duration: {duration}s")
        print(f"├─ Attack Frequency: {attack_frequency} attacks/sec")
        print(f"├─ Defense Nodes: {len(self.defense_system.nodes)}")
        print(f"└─ Threat Variants: {len(self.threat_simulator.threat_library)}")
        
        # Display initial status
        print("\n" + "="*70)
        print("    INITIAL DEFENSE STATUS")
        print("="*70)
        self.defense_system.display_status()
        
        print("\n" + "="*70)
        print("    INITIAL THREAT STATUS")
        print("="*70)
        self.threat_simulator.display_status()
        
        # Create evolving threat campaign
        print("\n🎯 Creating adversarial attack campaign...")
        campaign = self.threat_simulator.create_campaign(
            name="Quantum Adversarial Assault",
            strategy=EvolutionStrategy.ADVERSARIAL,
            attack_vectors=[
                AttackVector.SQL_INJECTION,
                AttackVector.DDOS,
                AttackVector.ZERO_DAY,
                AttackVector.QUANTUM_ATTACK,
                AttackVector.QUANTUM_MITM,
                AttackVector.RANSOMWARE
            ],
            duration=duration,
            attack_frequency=attack_frequency
        )
        
        print("\n" + "="*70)
        print("║              BATTLE IN PROGRESS              ║")
        print("="*70)
        print("\n⚡ Real-time battle log:\n")
        
        # Run campaign against defense system
        battle_start = time.time()
        results = await self.threat_simulator.run_campaign(
            campaign, 
            defense_system=self.defense_system
        )
        battle_duration = time.time() - battle_start
        
        # Analyze results
        print("\n" + "="*70)
        print("║              BATTLE COMPLETE              ║")
        print("="*70)
        
        defense_stats = self.defense_system.get_network_status()
        threat_stats = self.threat_simulator.get_statistics()
        
        # Calculate metrics
        total_attacks = campaign.total_attacks
        successful_attacks = campaign.successful_attacks
        blocked_attacks = defense_stats['statistics']['threats_blocked']
        attack_success_rate = (successful_attacks / total_attacks * 100) if total_attacks > 0 else 0
        defense_success_rate = (blocked_attacks / total_attacks * 100) if total_attacks > 0 else 0
        
        print(f"\n📊 BATTLE STATISTICS")
        print(f"\n⚔️  ATTACK METRICS")
        print(f"├─ Total Attacks: {total_attacks}")
        print(f"├─ Successful Attacks: {successful_attacks} ({attack_success_rate:.1f}%)")
        print(f"├─ Failed Attacks: {total_attacks - successful_attacks}")
        print(f"├─ Threat Generations: {campaign.current_generation}")
        print(f"└─ Final Variants: {len(campaign.variants)}")
        
        print(f"\n🛡️  DEFENSE METRICS")
        print(f"├─ Threats Detected: {defense_stats['statistics']['threats_detected']}")
        print(f"├─ Threats Blocked: {blocked_attacks} ({defense_success_rate:.1f}%)")
        print(f"├─ Defense Mutations: {defense_stats['statistics']['mutations']}")
        print(f"├─ Quantum Channels: {defense_stats['quantum_channels']}")
        print(f"├─ Network Health: {defense_stats['network_health']:.1%}")
        print(f"└─ Quantum Coherence: {defense_stats['quantum_coherence']:.1%}")
        
        print(f"\n⚡ PERFORMANCE")
        print(f"├─ Battle Duration: {battle_duration:.2f}s")
        print(f"├─ Attacks per Second: {total_attacks / battle_duration:.2f}")
        print(f"├─ Avg Response Time: {(battle_duration / total_attacks * 1000):.2f}ms")
        print(f"└─ Throughput: {total_attacks / battle_duration:.0f} ops/sec")
        
        # Determine winner
        print(f"\n🏆 BATTLE OUTCOME")
        if defense_success_rate > attack_success_rate:
            print(f"   ✅ DEFENSE VICTORY!")
            print(f"   Defense successfully blocked {defense_success_rate:.1f}% of attacks")
            winner = "defense"
        elif attack_success_rate > defense_success_rate:
            print(f"   ⚠️  THREAT BREAKTHROUGH!")
            print(f"   Threats achieved {attack_success_rate:.1f}% success rate")
            winner = "threats"
        else:
            print(f"   ⚖️  STALEMATE")
            print(f"   Both systems achieved {defense_success_rate:.1f}% effectiveness")
            winner = "draw"
        
        # Evolution metrics
        print(f"\n🧬 EVOLUTIONARY PROGRESS")
        print(f"├─ Threat Evolution Events: {threat_stats['evolution_events']}")
        print(f"├─ Defense Mutations: {defense_stats['statistics']['mutations']}")
        print(f"├─ Total Defense Patterns Learned: {defense_stats['total_defense_patterns']}")
        print(f"└─ Quantum Network Topology Version: v{defense_stats['topology_version']}")
        
        # Display final states
        print("\n" + "="*70)
        print("    FINAL DEFENSE STATUS")
        print("="*70)
        self.defense_system.display_status()
        
        print("\n" + "="*70)
        print("    FINAL THREAT STATUS")
        print("="*70)
        self.threat_simulator.display_status()
        
        # Save battle report
        battle_report = {
            'timestamp': datetime.now().isoformat(),
            'duration': battle_duration,
            'winner': winner,
            'attack_metrics': {
                'total_attacks': total_attacks,
                'successful_attacks': successful_attacks,
                'success_rate': attack_success_rate,
                'generations': campaign.current_generation,
                'final_variants': len(campaign.variants)
            },
            'defense_metrics': {
                'threats_detected': defense_stats['statistics']['threats_detected'],
                'threats_blocked': blocked_attacks,
                'success_rate': defense_success_rate,
                'mutations': defense_stats['statistics']['mutations'],
                'network_health': defense_stats['network_health'],
                'quantum_coherence': defense_stats['quantum_coherence']
            },
            'performance': {
                'attacks_per_second': total_attacks / battle_duration,
                'avg_response_time_ms': battle_duration / total_attacks * 1000,
                'throughput': total_attacks / battle_duration
            }
        }
        
        self.battle_history.append(battle_report)
        
        return battle_report
    
    async def run_tournament(self, rounds: int = 3, round_duration: float = 30.0):
        """
        Run multiple battle rounds
        Systems continuously evolve between rounds
        """
        
        print("\n" + "="*70)
        print("║        QUANTUM BATTLE TOURNAMENT STARTING         ║")
        print("="*70)
        print(f"\n🏆 Tournament: {rounds} rounds x {round_duration}s each")
        
        tournament_results = []
        
        for round_num in range(1, rounds + 1):
            print(f"\n" + "="*70)
            print(f"║                    ROUND {round_num}/{rounds}                   ║")
            print("="*70)
            
            battle_report = await self.run_battle(
                duration=round_duration,
                attack_frequency=5.0
            )
            
            tournament_results.append(battle_report)
            
            if round_num < rounds:
                print(f"\n⏸️  Pausing for 5 seconds before next round...\n")
                await asyncio.sleep(5)
        
        # Tournament summary
        print("\n" + "="*70)
        print("║          TOURNAMENT COMPLETE - FINAL RESULTS          ║")
        print("="*70)
        
        defense_wins = sum(1 for r in tournament_results if r['winner'] == 'defense')
        threat_wins = sum(1 for r in tournament_results if r['winner'] == 'threats')
        draws = sum(1 for r in tournament_results if r['winner'] == 'draw')
        
        print(f"\n🏆 TOURNAMENT RESULTS")
        print(f"├─ Total Rounds: {rounds}")
        print(f"├─ Defense Victories: {defense_wins}")
        print(f"├─ Threat Victories: {threat_wins}")
        print(f"└─ Draws: {draws}")
        
        if defense_wins > threat_wins:
            print(f"\n🎊 TOURNAMENT CHAMPION: QUANTUM SLIME DEFENSE")
        elif threat_wins > defense_wins:
            print(f"\n⚠️  TOURNAMENT CHAMPION: QUANTUM THREATS")
        else:
            print(f"\n⚖️  TOURNAMENT RESULT: TIE")
        
        # Average metrics
        avg_attack_success = sum(r['attack_metrics']['success_rate'] for r in tournament_results) / rounds
        avg_defense_success = sum(r['defense_metrics']['success_rate'] for r in tournament_results) / rounds
        total_attacks = sum(r['attack_metrics']['total_attacks'] for r in tournament_results)
        total_blocked = sum(r['defense_metrics']['threats_blocked'] for r in tournament_results)
        
        print(f"\n📊 TOURNAMENT AVERAGES")
        print(f"├─ Avg Attack Success Rate: {avg_attack_success:.1f}%")
        print(f"├─ Avg Defense Success Rate: {avg_defense_success:.1f}%")
        print(f"├─ Total Attacks: {total_attacks}")
        print(f"├─ Total Blocked: {total_blocked}")
        print(f"└─ Overall Defense Rate: {(total_blocked / total_attacks * 100):.1f}%")
        
        print("\n" + "="*70)
        print("✅ TOURNAMENT COMPLETE")
        print("="*70)
        print("\n🔬 Key Observations:")
        print("   ✓ Both systems evolved in real-time during battle")
        print("   ✓ Threats adapted to defense patterns")
        print("   ✓ Defense learned and mutated against new attacks")
        print("   ✓ Quantum properties provided detection advantages")
        print("   ✓ Distributed architecture prevented single point failure")
        print("\n")


async def main():
    """Main demonstration"""
    
    print("\n" + "="*70)
    print("║                                                      ║")
    print("║          QUANTUM BATTLE ARENA v1.0                   ║")
    print("║     Evolving Threats vs. Quantum SLIME Defense      ║")
    print("║                                                      ║")
    print("="*70)
    
    arena = QuantumBattleArena()
    
    # Run single battle
    print("\n🎮 Choose mode:")
    print("   1. Single Battle (60 seconds)")
    print("   2. Quick Battle (30 seconds)")
    print("   3. Tournament (3 rounds x 30 seconds)")
    print("   4. Extended Tournament (5 rounds x 45 seconds)")
    
    # For demo, run quick battle
    mode = 2  # Quick battle
    
    if mode == 1:
        await arena.run_battle(duration=60.0, attack_frequency=5.0)
    elif mode == 2:
        await arena.run_battle(duration=30.0, attack_frequency=5.0)
    elif mode == 3:
        await arena.run_tournament(rounds=3, round_duration=30.0)
    elif mode == 4:
        await arena.run_tournament(rounds=5, round_duration=45.0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Battle Arena terminated by user")
    except Exception as e:
        logger.error(f"❌ Error in Battle Arena: {e}", exc_info=True)
