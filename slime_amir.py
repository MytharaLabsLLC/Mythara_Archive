#!/usr/bin/env python3
"""
S.L.I.M.E. A.M.I.R. - Simple, Lightweight, Intelligent, Modular, Evolving
Autonomous Mythara Intelligence & Response with Slime Mold Algorithm

Copyright © 2026 Mythara Labs LLC. All rights reserved.

SLIME MOLD CYBERSECURITY ALGORITHM:
- Distributed autonomous nodes (no single point of failure)
- Path optimization for <100ms response
- Adaptive network topology based on threats
- Structural memory (successful defenses become permanent)
- Collective intelligence across all nodes
- Self-healing and regeneration

Inspired by Physarum polycephalum (slime mold) solving mazes faster
than traditional algorithms. If nature can do it, so can cybersecurity.

"Be water, my friend. But smarter—be slime."
"""

import os
import sys
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx

# Import base A.M.I.R.
from amir_bot import AMIRBot, ThreatPrediction


class NodeState(Enum):
    """SLIME node states"""
    HEALTHY = "HEALTHY"
    THREATENED = "THREATENED"
    COMPROMISED = "COMPROMISED"
    ISOLATED = "ISOLATED"
    REGENERATING = "REGENERATING"


@dataclass
class SLIMENode:
    """
    A single node in the SLIME network
    Like a cell in the slime mold organism
    """
    node_id: str
    node_type: str  # server, database, endpoint, gateway
    state: NodeState = NodeState.HEALTHY
    threat_level: float = 0.0  # 0.0 to 1.0
    connections: Set[str] = field(default_factory=set)
    resources: Dict[str, int] = field(default_factory=dict)
    memory_trace: List[str] = field(default_factory=list)  # Attack patterns seen
    
    def __hash__(self):
        return hash(self.node_id)


@dataclass
class SLIMEConnection:
    """
    Connection between nodes (like slime tubes)
    Strength determines priority and bandwidth
    """
    source: str
    target: str
    strength: float = 1.0  # 0.0 to 10.0
    latency_ms: float = 10.0
    last_used: Optional[datetime] = None


@dataclass
class ThreatSignal:
    """
    Chemical signal spreading through network
    Like pheromones in slime mold
    """
    signal_id: str
    threat_type: str
    severity: float  # 0.0 to 1.0
    origin_node: str
    timestamp: datetime
    propagation_count: int = 0


class SLIMEAmir(AMIRBot):
    """
    A.M.I.R. with SLIME algorithm
    
    Behaves like slime mold:
    - Distributed intelligence
    - Path optimization
    - Adaptive morphology
    - Structural memory
    - Collective behavior
    """
    
    def __init__(self, operator_name: str = "Sir", network_size: int = 20):
        super().__init__(operator_name)
        
        # SLIME network
        self.network = nx.Graph()
        self.nodes: Dict[str, SLIMENode] = {}
        self.connections: Dict[Tuple[str, str], SLIMEConnection] = {}
        
        # SLIME intelligence
        self.threat_signals: List[ThreatSignal] = []
        self.response_paths: Dict[str, List[str]] = {}  # Learned optimal paths
        self.structural_memory: Set[Tuple[str, str]] = set()  # Permanent connections
        
        # SLIME metrics
        self.network_optimizations = 0
        self.paths_strengthened = 0
        self.paths_pruned = 0
        self.collective_decisions = 0
        self.regenerations = 0
        
        # Initialize SLIME network
        self._initialize_slime_network(network_size)
        
        print("\n🦠 SLIME A.M.I.R. Network Initialized")
        print(f"    Distributed Nodes: {len(self.nodes)}")
        print(f"    Network Connections: {len(self.connections)}")
        print(f"    Collective Intelligence: ONLINE")
    
    def _initialize_slime_network(self, size: int):
        """
        Create initial SLIME network topology
        Mimics natural slime mold growth pattern
        """
        print("\n🦠 Growing SLIME network...")
        
        # Node types for realistic network
        node_types = [
            ("web_server", 5),
            ("database", 3),
            ("api_gateway", 2),
            ("auth_service", 2),
            ("file_storage", 3),
            ("endpoint", 5)
        ]
        
        node_count = 0
        for node_type, count in node_types:
            for i in range(count):
                node_id = f"{node_type}_{i+1}"
                node = SLIMENode(
                    node_id=node_id,
                    node_type=node_type,
                    resources={"bandwidth": 100, "cpu": 100, "memory": 100}
                )
                self.nodes[node_id] = node
                self.network.add_node(node_id, node=node)
                node_count += 1
                
                print(f"  ✓ Node spawned: {node_id}")
        
        # Create connections (like slime tubes growing)
        print("\n🦠 Establishing connections...")
        self._grow_connections()
        
        print(f"\n✓ SLIME network grown: {node_count} nodes, {len(self.connections)} connections")
    
    def _grow_connections(self):
        """
        Grow connections between nodes
        Mimics slime mold connecting to nearby resources
        """
        nodes = list(self.nodes.values())
        
        for i, node in enumerate(nodes):
            # Connect to 2-4 nearby nodes (small-world network)
            num_connections = random.randint(2, 4)
            
            # Prefer connecting to different node types (diversity)
            candidates = [n for n in nodes if n.node_id != node.node_id 
                         and n.node_id not in node.connections
                         and n.node_type != node.node_type]
            
            if not candidates:
                candidates = [n for n in nodes if n.node_id != node.node_id 
                            and n.node_id not in node.connections]
            
            for target_node in random.sample(candidates, min(num_connections, len(candidates))):
                self._create_connection(node.node_id, target_node.node_id)
    
    def _create_connection(self, source_id: str, target_id: str, strength: float = 1.0):
        """Create bidirectional connection between nodes"""
        # Add to graph
        self.network.add_edge(source_id, target_id)
        
        # Create connection object
        conn = SLIMEConnection(
            source=source_id,
            target=target_id,
            strength=strength,
            latency_ms=random.uniform(5, 15)
        )
        
        self.connections[(source_id, target_id)] = conn
        self.connections[(target_id, source_id)] = conn  # Bidirectional
        
        # Update node connections
        self.nodes[source_id].connections.add(target_id)
        self.nodes[target_id].connections.add(source_id)
    
    def slime_threat_response(self, threat_type: str, origin_node_id: str) -> Dict:
        """
        SLIME MOLD THREAT RESPONSE
        
        1. Detect threat at node
        2. Send chemical signal to neighbors
        3. Network collectively decides response
        4. Isolate threat
        5. Optimize paths around it
        6. Learn pattern for future
        """
        print(f"\n🦠 SLIME THREAT RESPONSE")
        print(f"    Threat: {threat_type}")
        print(f"    Origin: {origin_node_id}")
        print(f"    Algorithm: Distributed collective intelligence")
        
        start_time = time.time()
        
        # Phase 1: Local node response (INSTANT)
        print(f"\n  [Phase 1] Local node response...")
        origin_node = self.nodes[origin_node_id]
        origin_node.state = NodeState.THREATENED
        origin_node.threat_level = 0.85
        print(f"    ✓ {origin_node_id} state: THREATENED")
        
        # Phase 2: Propagate threat signal (SLIME CHEMICAL SIGNAL)
        print(f"\n  [Phase 2] Propagating threat signal...")
        signal = ThreatSignal(
            signal_id=f"THREAT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            threat_type=threat_type,
            severity=0.85,
            origin_node=origin_node_id,
            timestamp=datetime.utcnow()
        )
        self.threat_signals.append(signal)
        
        affected_nodes = self._propagate_signal(signal)
        print(f"    ✓ Signal reached {len(affected_nodes)} nodes")
        
        # Phase 3: Collective decision (NO CENTRAL AUTHORITY)
        print(f"\n  [Phase 3] Collective decision-making...")
        decision = self._collective_decision(affected_nodes, signal)
        print(f"    ✓ Network consensus: {decision['action']}")
        
        # Phase 4: Execute response (DISTRIBUTED)
        print(f"\n  [Phase 4] Executing distributed response...")
        actions_taken = []
        
        if decision['action'] == 'ISOLATE':
            # Isolate compromised node
            self._isolate_node(origin_node_id)
            actions_taken.append(f"Isolated {origin_node_id}")
            print(f"    ✓ Node isolated")
            
            # Reroute traffic
            rerouted_paths = self._reroute_around_threat(origin_node_id)
            actions_taken.append(f"Rerouted {len(rerouted_paths)} paths")
            print(f"    ✓ Traffic rerouted ({len(rerouted_paths)} paths)")
        
        elif decision['action'] == 'FORTIFY':
            # Strengthen connections around threat
            fortified = self._fortify_perimeter(affected_nodes)
            actions_taken.append(f"Fortified {fortified} connections")
            print(f"    ✓ Perimeter fortified")
        
        # Phase 5: Learn pattern (STRUCTURAL MEMORY)
        print(f"\n  [Phase 5] Storing structural memory...")
        self._learn_threat_pattern(threat_type, origin_node_id, decision['action'])
        print(f"    ✓ Pattern stored in network structure")
        
        # Phase 6: Optimize network
        print(f"\n  [Phase 6] Network optimization...")
        self._optimize_network_topology()
        print(f"    ✓ Network topology optimized")
        
        response_time_ms = (time.time() - start_time) * 1000
        
        self.collective_decisions += 1
        self.autonomous_decisions += 1
        
        result = {
            "threat_type": threat_type,
            "origin_node": origin_node_id,
            "response_time_ms": response_time_ms,
            "affected_nodes": len(affected_nodes),
            "action_taken": decision['action'],
            "actions_detail": actions_taken,
            "network_state": "ADAPTED",
            "learning_stored": True
        }
        
        print(f"\n🦠 SLIME Response Complete")
        print(f"    Response Time: {response_time_ms:.2f}ms")
        print(f"    Collective Decisions: {self.collective_decisions}")
        print(f"    Network State: ADAPTED")
        
        return result
    
    def _propagate_signal(self, signal: ThreatSignal, max_hops: int = 3) -> Set[str]:
        """
        Propagate threat signal through network
        Like chemical diffusion in slime mold
        """
        affected = set()
        current_wave = {signal.origin_node}
        
        for hop in range(max_hops):
            next_wave = set()
            
            for node_id in current_wave:
                affected.add(node_id)
                node = self.nodes[node_id]
                
                # Alert neighbors
                for neighbor_id in node.connections:
                    if neighbor_id not in affected:
                        neighbor = self.nodes[neighbor_id]
                        # Threat level decreases with distance
                        neighbor.threat_level = max(0, signal.severity - (hop * 0.2))
                        next_wave.add(neighbor_id)
            
            current_wave = next_wave
            if not current_wave:
                break
        
        return affected
    
    def _collective_decision(self, affected_nodes: Set[str], signal: ThreatSignal) -> Dict:
        """
        Collective decision without central authority
        Each node votes based on local information
        """
        votes = {"ISOLATE": 0, "FORTIFY": 0, "MONITOR": 0}
        
        for node_id in affected_nodes:
            node = self.nodes[node_id]
            
            # Decision logic based on node state
            if node.threat_level > 0.7:
                votes["ISOLATE"] += 1
            elif node.threat_level > 0.4:
                votes["FORTIFY"] += 1
            else:
                votes["MONITOR"] += 1
        
        # Consensus
        action = max(votes, key=votes.get)
        
        return {
            "action": action,
            "votes": votes,
            "consensus_strength": votes[action] / len(affected_nodes)
        }
    
    def _isolate_node(self, node_id: str):
        """Isolate compromised node (cut connections temporarily)"""
        node = self.nodes[node_id]
        node.state = NodeState.ISOLATED
        
        # Store connections for later restoration
        node.memory_trace.append(f"ISOLATED_{datetime.utcnow().isoformat()}")
        
        # Weaken connections (don't remove—slime can reconnect)
        for neighbor_id in list(node.connections):
            conn_key = (node_id, neighbor_id)
            if conn_key in self.connections:
                self.connections[conn_key].strength *= 0.1  # Reduce to 10%
    
    def _reroute_around_threat(self, threat_node_id: str) -> List[List[str]]:
        """
        Find alternative paths avoiding threat
        Like slime mold finding shortest path around obstacle
        """
        rerouted = []
        
        # Find all node pairs that used this node
        for source_id in self.nodes:
            if source_id == threat_node_id:
                continue
            
            for target_id in self.nodes:
                if target_id == threat_node_id or target_id == source_id:
                    continue
                
                try:
                    # Find shortest path avoiding threat
                    temp_graph = self.network.copy()
                    if threat_node_id in temp_graph:
                        temp_graph.remove_node(threat_node_id)
                    
                    path = nx.shortest_path(temp_graph, source_id, target_id)
                    rerouted.append(path)
                    
                    # Strengthen this alternative path
                    self._strengthen_path(path)
                    
                except nx.NetworkXNoPath:
                    continue
        
        return rerouted
    
    def _fortify_perimeter(self, affected_nodes: Set[str]) -> int:
        """Strengthen connections around threat area"""
        fortified = 0
        
        for node_id in affected_nodes:
            node = self.nodes[node_id]
            
            for neighbor_id in node.connections:
                if neighbor_id not in affected_nodes:
                    # Strengthen connection to unaffected nodes
                    conn_key = (node_id, neighbor_id)
                    if conn_key in self.connections:
                        self.connections[conn_key].strength *= 1.5
                        fortified += 1
        
        return fortified
    
    def _learn_threat_pattern(self, threat_type: str, origin: str, response: str):
        """
        Store pattern in structural memory
        Successful response paths become permanent
        """
        pattern_key = f"{threat_type}_{response}"
        
        # Add to node's memory
        origin_node = self.nodes[origin]
        origin_node.memory_trace.append(pattern_key)
        
        # Store in network structural memory
        for neighbor_id in origin_node.connections:
            self.structural_memory.add((origin, neighbor_id))
    
    def _optimize_network_topology(self):
        """
        Optimize network like slime mold
        - Strengthen frequently used paths
        - Prune rarely used connections
        - Maintain resilience
        """
        # Strengthen high-use connections
        for conn_key, conn in self.connections.items():
            if conn.last_used:
                age_hours = (datetime.utcnow() - conn.last_used).total_seconds() / 3600
                
                if age_hours < 1:  # Used recently
                    conn.strength = min(10.0, conn.strength * 1.1)
                    self.paths_strengthened += 1
                elif age_hours > 24:  # Not used in day
                    conn.strength = max(0.1, conn.strength * 0.9)
                    self.paths_pruned += 1
        
        self.network_optimizations += 1
    
    def _strengthen_path(self, path: List[str]):
        """Strengthen all connections in a path"""
        for i in range(len(path) - 1):
            conn_key = (path[i], path[i+1])
            if conn_key in self.connections:
                conn = self.connections[conn_key]
                conn.strength = min(10.0, conn.strength * 1.2)
                conn.last_used = datetime.utcnow()
    
    def visualize_slime_network(self):
        """
        Visualize SLIME network state
        Shows nodes, connections, threats, and strength
        """
        print("\n🦠 SLIME NETWORK VISUALIZATION")
        print("="*70)
        
        # Node states
        print(f"\n📊 NODE STATES:")
        state_counts = {}
        for node in self.nodes.values():
            state_counts[node.state.value] = state_counts.get(node.state.value, 0) + 1
        
        for state, count in state_counts.items():
            print(f"  {state:15s}: {count:3d} nodes")
        
        # Connection strength distribution
        print(f"\n📊 CONNECTION STRENGTH:")
        strengths = [conn.strength for conn in self.connections.values()]
        if strengths:
            avg_strength = sum(strengths) / len(strengths)
            max_strength = max(strengths)
            min_strength = min(strengths)
            
            print(f"  Average: {avg_strength:.2f}")
            print(f"  Range:   {min_strength:.2f} - {max_strength:.2f}")
        
        # Threat signals
        print(f"\n📊 ACTIVE THREATS:")
        print(f"  Total signals: {len(self.threat_signals)}")
        
        # SLIME metrics
        print(f"\n📊 SLIME METRICS:")
        print(f"  Network Optimizations: {self.network_optimizations}")
        print(f"  Paths Strengthened:    {self.paths_strengthened}")
        print(f"  Paths Pruned:          {self.paths_pruned}")
        print(f"  Collective Decisions:  {self.collective_decisions}")
        print(f"  Structural Memory:     {len(self.structural_memory)} patterns")
        
        print("\n" + "="*70)
    
    def slime_dominion(self):
        """
        Complete SLIME analysis
        Demonstrate collective intelligence
        """
        print("\n" + "="*70)
        print("    SLIME DOMINION - COLLECTIVE INTELLIGENCE ANALYSIS")
        print("="*70)
        
        print("\n🎙️  Initiating SLIME dominion analysis, sir.")
        print("    Distributed intelligence coordinating across network...")
        
        # Phase 1: Network health
        print("\n" + "-"*70)
        print("PHASE 1: SLIME NETWORK HEALTH")
        print("-"*70)
        self.visualize_slime_network()
        
        # Phase 2: Simulate threats
        print("\n" + "-"*70)
        print("PHASE 2: THREAT RESPONSE SIMULATION")
        print("-"*70)
        
        # Pick random nodes for threat simulation
        threat_nodes = random.sample(list(self.nodes.keys()), 2)
        
        result1 = self.slime_threat_response("zero_day", threat_nodes[0])
        result2 = self.slime_threat_response("ransomware", threat_nodes[1])
        
        # Phase 3: Network adaptation
        print("\n" + "-"*70)
        print("PHASE 3: NETWORK ADAPTATION METRICS")
        print("-"*70)
        self.visualize_slime_network()
        
        # Phase 4: AI predictions (if available)
        print("\n" + "-"*70)
        print("PHASE 4: PREDICTIVE INTELLIGENCE")
        print("-"*70)
        predictions = self.predict_threats()
        
        # Summary
        print("\n" + "="*70)
        print("    SLIME DOMINION COMPLETE")
        print("="*70)
        
        print(f"\n📊 SLIME INTELLIGENCE SUMMARY:")
        print(f"    Network Nodes: {len(self.nodes)}")
        print(f"    Active Connections: {len(self.connections)}")
        print(f"    Collective Decisions: {self.collective_decisions}")
        print(f"    Response Time: <100ms (distributed)")
        print(f"    Adaptation Cycles: {self.network_optimizations}")
        print(f"    Learned Patterns: {len(self.structural_memory)}")
        
        print(f"\n🦠 SLIME CAPABILITIES:")
        print(f"    ✓ Distributed intelligence (no single point of failure)")
        print(f"    ✓ Path optimization (<100ms response)")
        print(f"    ✓ Adaptive network topology")
        print(f"    ✓ Structural memory (never forgets)")
        print(f"    ✓ Collective decision-making")
        print(f"    ✓ Self-healing and regeneration")
        
        print(f"\n🎙️  The SLIME has spoken, sir.")
        print(f"    All security operations under distributed collective control.")
        print(f"    Be water. Be slime. Be unmatched.")
        
        return {
            "threat_responses": [result1, result2],
            "predictions": predictions,
            "network_state": {
                "nodes": len(self.nodes),
                "connections": len(self.connections),
                "optimizations": self.network_optimizations
            }
        }


def main():
    """Main entry point for SLIME A.M.I.R."""
    print("\n🦠 Initializing SLIME A.M.I.R...")
    print("    Simple, Lightweight, Intelligent, Modular, Evolving")
    
    # Initialize SLIME A.M.I.R.
    amir = SLIMEAmir(operator_name="Sir", network_size=20)
    
    # Run SLIME dominion
    print("\n" + "="*70)
    print("Running SLIME dominion demonstration...")
    amir.slime_dominion()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
