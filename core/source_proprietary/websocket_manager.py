#!/usr/bin/env python3
"""
Mythara Engine - WebSocket Support
Real-time communication for Soul Engine dashboard and paradox alerts.

Copyright © 2026 Mythara Labs LLC. All rights reserved.
"""

from fastapi import WebSocket
from typing import List, Dict, Any, Optional, Set
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.

    Features:
    - Per-organization channels
    - Broadcast to all connections
    - User-specific alerts
    - Automatic cleanup on disconnect
    """

    def __init__(self):
        # Store active connections by organization
        self.active_connections: Dict[str, List[WebSocket]] = {}

        # Store user metadata for each connection
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

        # Track which users are watching which entities
        self.subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(
        self, websocket: WebSocket, user_id: str, org_id: str, role: str = "viewer"
    ) -> None:
        """
        Accept new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            user_id: Authenticated user ID
            org_id: Organization ID
            role: User role (admin, manager, viewer)
        """
        await websocket.accept()

        # Store connection by organization
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []

        self.active_connections[org_id].append(websocket)

        # Store metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "org_id": org_id,
            "role": role,
            "connected_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"✅ WebSocket connected: user={user_id}, org={org_id}, role={role}"
        )

        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection_established",
                "message": f"Connected to Soul Engine (org: {org_id})",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            websocket,
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove connection and cleanup.

        Args:
            websocket: WebSocket to disconnect
        """
        metadata = self.connection_metadata.get(websocket)

        if metadata:
            org_id = metadata["org_id"]
            user_id = metadata["user_id"]

            # Remove from active connections
            if org_id in self.active_connections:
                try:
                    self.active_connections[org_id].remove(websocket)

                    # Cleanup empty org lists
                    if not self.active_connections[org_id]:
                        del self.active_connections[org_id]

                except ValueError:
                    pass

            # Remove from subscriptions
            for sub_key in list(self.subscriptions.keys()):
                if websocket in self.subscriptions[sub_key]:
                    self.subscriptions[sub_key].remove(websocket)

                    # Cleanup empty subscription lists
                    if not self.subscriptions[sub_key]:
                        del self.subscriptions[sub_key]

            # Remove metadata
            del self.connection_metadata[websocket]

            logger.info(f"❌ WebSocket disconnected: user={user_id}, org={org_id}")

    async def send_personal_message(
        self, message: Dict[str, Any], websocket: WebSocket
    ) -> None:
        """
        Send message to specific connection.

        Args:
            message: Message dict to send (will be JSON-serialized)
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast_to_organization(
        self, org_id: str, message: Dict[str, Any]
    ) -> None:
        """
        Broadcast message to all connections in an organization.

        Args:
            org_id: Organization ID
            message: Message dict to broadcast
        """
        if org_id not in self.active_connections:
            return

        disconnected: List[WebSocket] = []

        for connection in self.active_connections[org_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Cleanup disconnected sockets
        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """
        Broadcast message to ALL connected clients (system-wide).

        Args:
            message: Message dict to broadcast
        """
        for org_id in list(self.active_connections.keys()):
            await self.broadcast_to_organization(org_id, message)

    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to specific user (all their connections).

        Args:
            user_id: Target user ID
            message: Message dict to send

        Returns:
            True if message was sent to at least one connection
        """
        sent = False

        for websocket, metadata in list(self.connection_metadata.items()):
            if metadata["user_id"] == user_id:
                try:
                    await websocket.send_json(message)
                    sent = True
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    self.disconnect(websocket)

        return sent

    def subscribe(self, entity_id: str, websocket: WebSocket) -> None:
        """
        Subscribe connection to specific entity updates (user, department, etc.).

        Args:
            entity_id: Entity to watch (user_id, dept_id, etc.)
            websocket: WebSocket connection
        """
        if entity_id not in self.subscriptions:
            self.subscriptions[entity_id] = set()

        self.subscriptions[entity_id].add(websocket)
        logger.info(f"📡 Subscription added: entity={entity_id}")

    async def notify_subscribers(self, entity_id: str, message: Dict[str, Any]) -> None:
        """
        Send message to all subscribers of an entity.

        Args:
            entity_id: Entity ID
            message: Message dict to send
        """
        if entity_id not in self.subscriptions:
            return

        disconnected: List[WebSocket] = []

        for websocket in self.subscriptions[entity_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
                disconnected.append(websocket)

        # Cleanup disconnected sockets
        for ws in disconnected:
            self.disconnect(ws)

    def get_connection_count(self, org_id: Optional[str] = None) -> int:
        """
        Get number of active connections.

        Args:
            org_id: Optional organization ID (if None, returns total)

        Returns:
            Connection count
        """
        if org_id:
            return len(self.active_connections.get(org_id, []))

        return sum(len(conns) for conns in self.active_connections.values())

    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics.

        Returns:
            Stats dict with connection counts, org breakdown, etc.
        """
        return {
            "total_connections": self.get_connection_count(),
            "organizations": len(self.active_connections),
            "subscriptions": len(self.subscriptions),
            "org_breakdown": {
                org_id: len(conns) for org_id, conns in self.active_connections.items()
            },
        }


# Global connection manager
manager = ConnectionManager()


# ===================== ALERT BROADCAST FUNCTIONS =====================


async def broadcast_paradox_alert(
    org_id: str, user_id: str, paradox: Dict[str, Any], risk_level: str
) -> None:
    """
    Broadcast new paradox alert to organization dashboard.

    Args:
        org_id: Organization ID
        user_id: User who created paradox
        paradox: Paradox data
        risk_level: Risk level (LOW, MODERATE, HIGH, CRITICAL)
    """
    message = {
        "type": "paradox_created",
        "org_id": org_id,
        "user_id": user_id,
        "risk_level": risk_level,
        "paradox": {
            "paradox_id": paradox.get("paradox_id"),
            "unresolved_score": paradox.get("unresolved_score"),
            "viability_score": paradox.get("viability_score"),
            "timestamp": paradox.get("timestamp"),
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    await manager.broadcast_to_organization(org_id, message)

    # Also notify subscribers of this specific user
    await manager.notify_subscribers(f"user:{user_id}", message)


async def broadcast_systemic_overload_alert(
    org_id: str,
    dept_id: str,
    affected_users: List[str],
    baseline_stress: float,
    acute_risk: float,
) -> None:
    """
    Broadcast systemic overload alert to organization.

    Args:
        org_id: Organization ID
        dept_id: Department ID
        affected_users: List of user IDs in overload
        baseline_stress: Average baseline stress
        acute_risk: Average acute risk
    """
    message = {
        "type": "systemic_overload",
        "severity": "CRITICAL",
        "org_id": org_id,
        "dept_id": dept_id,
        "affected_users_count": len(affected_users),
        "baseline_stress": baseline_stress,
        "acute_risk": acute_risk,
        "recommendation": "Environmental intervention required - fix systemic issues",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    await manager.broadcast_to_organization(org_id, message)


async def broadcast_indifference_alert(
    org_id: str,
    user_id: str,
    tension_trajectory: List[float],
    emotional_energy: float,
    days_until_critical: int,
) -> None:
    """
    Broadcast indifference trajectory alert (CRITICAL - violence prevention).

    Args:
        org_id: Organization ID
        user_id: User ID showing indifference
        tension_trajectory: Recent tension scores (decreasing pattern)
        emotional_energy: Current emotional energy (approaching 0)
        days_until_critical: Estimated days until terminal event
    """
    message = {
        "type": "indifference_trajectory",
        "severity": "TERMINAL",
        "org_id": org_id,
        "user_id": user_id,
        "tension_trajectory": tension_trajectory,
        "emotional_energy": emotional_energy,
        "days_until_critical": days_until_critical,
        "recommendation": "🚨 72-HOUR WATCH PROTOCOL: Immediate threat assessment required",
        "protocol": [
            "Crisis counselor within 2 hours",
            "Psychiatric evaluation within 6 hours",
            "72-hour supervision (no unsupervised time)",
            "Remove weapon access",
            "Consider psychiatric hold",
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    await manager.broadcast_to_organization(org_id, message)

    # Send urgent notification to subscribed administrators
    await manager.notify_subscribers(f"admin:{org_id}", message)


async def broadcast_risk_update(
    org_id: str, user_id: str, old_risk: float, new_risk: float, trajectory: str
) -> None:
    """
    Broadcast risk score update.

    Args:
        org_id: Organization ID
        user_id: User ID
        old_risk: Previous risk score
        new_risk: New risk score
        trajectory: IMPROVING or DECLINING
    """
    message = {
        "type": "risk_update",
        "org_id": org_id,
        "user_id": user_id,
        "old_risk": old_risk,
        "new_risk": new_risk,
        "trajectory": trajectory,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    await manager.broadcast_to_organization(org_id, message)


async def broadcast_system_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Broadcast system-wide event to all connections.

    Args:
        event_type: Event type (maintenance, update, alert)
        data: Event data
    """
    message = {
        "type": "system_event",
        "event_type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    await manager.broadcast_to_all(message)
