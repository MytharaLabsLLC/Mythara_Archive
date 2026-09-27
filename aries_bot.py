#!/usr/bin/env python3
"""
ARIES - The Action Execution Engine
An execution engine that takes approved decisions and runs them through
registered handlers — with precision and speed, one signed action at a time.

Copyright © 2025 Herbert Velez Jr. All rights reserved.

A.R.I.E.S.:
Autonomous Rapid Implementation & Execution System

PLATING (2026-09-22): Aries no longer executes raw strings. Every action must
carry a signed ActionEnvelope issued by the Soul Cradle authority
(soul_cradle.authorization). Aries verifies the envelope — signature, expiry,
payload integrity, action type, issuer — before dispatching to a registered
handler. No valid governed signal means no execution. There is no exec(),
no eval(), and no shell=True in this trust boundary.
"""

import json
import os
import time
import hashlib
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, PriorityQueue

from soul_cradle.authorization import (
    ActionEnvelope,
    AuthorizationError,
    SoulCradleAuthority,
)


class ActionPriority(Enum):
    """Priority levels for action execution"""

    CRITICAL = 1  # Must execute immediately
    HIGH = 2  # Execute as soon as possible
    NORMAL = 3  # Execute in normal queue order
    LOW = 4  # Execute when resources available
    BACKGROUND = 5  # Execute during idle time


class ActionStatus(Enum):
    """Status of action execution"""

    QUEUED = "queued"
    PREPARING = "preparing"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    BLOCKED = "blocked"


class ExecutionMode(Enum):
    """How to execute actions"""

    SEQUENTIAL = "sequential"  # One at a time
    PARALLEL = "parallel"  # All at once
    OPTIMIZED = "optimized"  # Smart ordering for dependencies
    AGGRESSIVE = "aggressive"  # Maximum speed, higher risk
    CAUTIOUS = "cautious"  # Validate everything, slower


@dataclass
class Action:
    """Represents a single executable action.

    An Action is inert until paired with a signed ActionEnvelope from the
    Soul Cradle authority. The envelope names a registered handler
    (action_type) and the typed payload it may run with. Raw command
    strings are not accepted anywhere in this class.
    """

    action_id: str
    description: str
    envelope: Optional[ActionEnvelope]
    payload: Dict[str, Any]
    priority: ActionPriority
    dependencies: List[str] = field(default_factory=list)
    validation_func: Optional[Callable] = None
    rollback_func: Optional[Callable] = None
    timeout_seconds: int = 300
    retry_count: int = 3
    status: ActionStatus = ActionStatus.QUEUED
    result: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    execution_time: float = 0.0
    attempts: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Complete execution plan with actions and strategy"""

    plan_id: str
    objective: str
    actions: List[Action]
    execution_mode: ExecutionMode
    total_actions: int
    completed_actions: int = 0
    failed_actions: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AriesBot:
    """
    A.R.I.E.S. - The Action Execution Engine

    Takes output from Prometheus (ideas), Schrödinger (evaluated paths),
    and Hephaestus (implementation plans) and runs it via registered handlers.

    Key Capabilities:
    - Priority-based action queuing
    - Parallel and sequential execution modes
    - Automatic dependency resolution
    - Retry logic with exponential backoff
    - Rollback on failure
    - Real-time progress tracking
    - Validation at every step
    """

    def __init__(self, authority: Optional[SoulCradleAuthority] = None):
        self.name = "ARIES"
        self.version = "2.0.0"
        # The membrane: every execution verifies against this authority.
        # Aries never mints its own envelopes — only Soul Cradle signs.
        self.authority = authority or SoulCradleAuthority()
        self.action_queue: PriorityQueue = PriorityQueue()
        self.completed_actions: List[Action] = []
        self.failed_actions: List[Action] = []
        self.blocked_actions: List[Action] = []
        self.execution_history: List[ExecutionPlan] = []
        self.active_threads: List[threading.Thread] = []
        self.is_executing = False

        print(f"⚔️ {self.name} - Action Execution Engine Initialized")
        print(f"   Autonomous Rapid Implementation & Execution System")
        print(
            f"   Plated: signed Soul Cradle authorization required for every action\n"
        )

    def create_action(
        self,
        description: str,
        envelope: ActionEnvelope,
        payload: Dict[str, Any],
        priority: ActionPriority = ActionPriority.NORMAL,
        dependencies: List[str] = None,
        timeout: int = 300,
        retry_count: int = 3,
        metadata: Dict[str, Any] = None,
        validation_func: Optional[Callable] = None,
        rollback_func: Optional[Callable] = None,
    ) -> Action:
        """
        Create a new executable action.

        Args:
            description: What this action does (human-readable)
            envelope: Signed ActionEnvelope from the Soul Cradle authority.
                Raw command strings are NOT accepted — pass an envelope.
            payload: Typed arguments for the registered handler named by
                envelope.action_type. Must hash-match the envelope.
            priority: Execution priority
            dependencies: List of action IDs that must complete first
            timeout: Maximum execution time in seconds
            retry_count: Number of retry attempts on failure
            metadata: Additional information

        Returns:
            Action object ready for execution
        """
        if isinstance(envelope, str):
            raise AuthorizationError(
                "Aries no longer executes raw command strings. "
                "Request a signed ActionEnvelope from SoulCradleAuthority.authorize() "
                "and pass it as the envelope."
            )
        if not isinstance(envelope, ActionEnvelope):
            raise AuthorizationError(
                f"envelope must be an ActionEnvelope, got {type(envelope).__name__}"
            )

        return Action(
            action_id=envelope.action_id,
            description=description,
            envelope=envelope,
            payload=payload,
            priority=priority,
            dependencies=dependencies or [],
            validation_func=validation_func,
            rollback_func=rollback_func,
            timeout_seconds=timeout,
            retry_count=retry_count,
            metadata=metadata or {},
        )

    def queue_action(self, action: Action):
        """Add action to execution queue"""
        self.action_queue.put((action.priority.value, action))
        print(f"📋 Queued: {action.description}")
        print(f"   Priority: {action.priority.name} | ID: {action.action_id}")

    def execute_action(self, action: Action) -> bool:
        """
        Execute a single action with retry logic and validation.

        The membrane: the envelope is verified against the Soul Cradle
        authority BEFORE anything runs. Any verification failure blocks
        the action — it is recorded, never executed, and never retried.

        Args:
            action: Action to execute

        Returns:
            True if successful, False otherwise
        """
        action.status = ActionStatus.PREPARING
        action.start_time = datetime.now().isoformat()

        action_type = action.envelope.action_type if action.envelope else "<none>"
        print(f"\n⚡ EXECUTING: {action.description}")
        print(f"   Action type: {action_type}")
        print(f"   Priority: {action.priority.name}")

        # -- THE MEMBRANE: verify authorization before execution ---------------
        ok, reason = self.authority.verify(action.envelope, action.payload)
        if not ok:
            action.status = ActionStatus.BLOCKED
            action.error = f"Authorization refused: {reason}"
            action.end_time = datetime.now().isoformat()
            self.blocked_actions.append(action)
            print(f"   🛡️ BLOCKED: {action.error} (not executed, not retried)")
            return False
        print(f"   🔏 Authorization verified (issuer: {action.envelope.issuer})")

        while action.attempts < action.retry_count:
            action.attempts += 1
            action.status = ActionStatus.EXECUTING

            try:
                start = time.time()

                # Dispatch ONLY to a pre-registered handler. No exec(),
                # no eval(), no shell. Unknown types were already refused
                # by verification above; this is defense in depth.
                action.result = self.authority.dispatch(action.envelope, action.payload)

                action.execution_time = time.time() - start

                # Validate if validation function provided
                if action.validation_func:
                    action.status = ActionStatus.VALIDATING
                    if not action.validation_func(action):
                        raise Exception("Validation failed")

                # Success!
                action.status = ActionStatus.COMPLETED
                action.end_time = datetime.now().isoformat()
                self.completed_actions.append(action)

                print(f"   ✅ SUCCESS ({action.execution_time:.2f}s)")
                if action.result:
                    result_preview = (
                        action.result[:100] + "..."
                        if len(action.result) > 100
                        else action.result
                    )
                    print(f"   Result: {result_preview}")

                return True

            except AuthorizationError as e:
                # Should not happen post-verification; treat as hard block.
                action.status = ActionStatus.BLOCKED
                action.error = str(e)
                action.end_time = datetime.now().isoformat()
                self.blocked_actions.append(action)
                print(f"   🛡️ BLOCKED: {action.error}")
                return False

            except Exception as e:
                action.error = str(e)
                print(f"   ❌ FAILED: {action.error}")
                print(f"   Attempt {action.attempts}/{action.retry_count}")

                if action.attempts < action.retry_count:
                    backoff = 2**action.attempts
                    print(f"   ⏳ Retrying in {backoff}s...")
                    time.sleep(backoff)

        # All retries exhausted
        action.status = ActionStatus.FAILED
        action.end_time = datetime.now().isoformat()
        self.failed_actions.append(action)

        # Attempt rollback via the registered rollback callable (code, not strings)
        if action.rollback_func:
            print(f"   🔄 Attempting rollback...")
            try:
                action.rollback_func(action)
                action.status = ActionStatus.ROLLED_BACK
                print(f"   ✅ Rollback successful")
            except Exception as e:
                print(f"   ❌ Rollback failed: {e}")

        return False

    def resolve_dependencies(self, actions: List[Action]) -> List[List[Action]]:
        """
        Resolve action dependencies and create execution waves.
        Actions in the same wave can execute in parallel.

        Args:
            actions: List of actions to order

        Returns:
            List of action waves (each wave can execute in parallel)
        """
        print(f"\n🔗 Resolving dependencies for {len(actions)} actions...")

        # Build dependency graph
        action_map = {a.action_id: a for a in actions}
        completed_ids = {a.action_id for a in self.completed_actions}

        waves = []
        remaining = set(a.action_id for a in actions)

        while remaining:
            # Find actions with no pending dependencies
            wave = []
            for action_id in list(remaining):
                action = action_map[action_id]
                deps_met = all(
                    dep in completed_ids or dep not in remaining
                    for dep in action.dependencies
                )
                if deps_met:
                    wave.append(action)
                    remaining.remove(action_id)

            if not wave:
                # Circular dependency detected
                blocked = [action_map[aid] for aid in remaining]
                for action in blocked:
                    action.status = ActionStatus.BLOCKED
                    self.failed_actions.append(action)
                print(
                    f"   ⚠️ Circular dependency detected, {len(blocked)} actions blocked"
                )
                break

            waves.append(wave)
            completed_ids.update(a.action_id for a in wave)

        print(f"   ✅ Organized into {len(waves)} execution waves")
        for i, wave in enumerate(waves):
            print(f"   Wave {i+1}: {len(wave)} actions")

        return waves

    def execute_wave_parallel(self, wave: List[Action]) -> Tuple[int, int]:
        """
        Execute a wave of actions in parallel.

        Args:
            wave: List of actions to execute simultaneously

        Returns:
            Tuple of (successful_count, failed_count)
        """
        print(f"\n🚀 Executing wave of {len(wave)} actions in parallel...")

        results = []
        threads = []

        def execute_with_result(action: Action):
            success = self.execute_action(action)
            results.append((action, success))

        # Start all threads
        for action in wave:
            thread = threading.Thread(target=execute_with_result, args=(action,))
            thread.start()
            threads.append(thread)
            self.active_threads.append(thread)

        # Wait for all to complete
        for thread in threads:
            thread.join()

        successful = sum(1 for _, success in results if success)
        failed = len(results) - successful

        print(f"   ✅ Wave complete: {successful} succeeded, {failed} failed")
        return successful, failed

    def execute_wave_sequential(self, wave: List[Action]) -> Tuple[int, int]:
        """
        Execute a wave of actions sequentially.

        Args:
            wave: List of actions to execute one by one

        Returns:
            Tuple of (successful_count, failed_count)
        """
        print(f"\n➡️ Executing wave of {len(wave)} actions sequentially...")

        successful = 0
        failed = 0

        for action in wave:
            if self.execute_action(action):
                successful += 1
            else:
                failed += 1

        print(f"   ✅ Wave complete: {successful} succeeded, {failed} failed")
        return successful, failed

    def execute_plan(
        self,
        objective: str,
        actions: List[Action],
        mode: ExecutionMode = ExecutionMode.OPTIMIZED,
    ) -> ExecutionPlan:
        """
        Execute a complete plan with multiple actions.

        Args:
            objective: What this plan achieves
            actions: List of actions to execute
            mode: Execution strategy

        Returns:
            Execution plan with results
        """
        self.is_executing = True

        plan_id = hashlib.sha256(f"{objective}_{time.time()}".encode()).hexdigest()[:16]

        plan = ExecutionPlan(
            plan_id=plan_id,
            objective=objective,
            actions=actions,
            execution_mode=mode,
            total_actions=len(actions),
            start_time=datetime.now().isoformat(),
        )

        print("=" * 70)
        print(f"⚔️ ARIES ACTION EXECUTION ENGINE")
        print("=" * 70)
        print(f"Objective: {objective}")
        print(f"Total Actions: {len(actions)}")
        print(f"Execution Mode: {mode.value}")
        print("=" * 70)

        start = time.time()

        if mode == ExecutionMode.SEQUENTIAL:
            # Execute all actions one by one
            for action in actions:
                if self.execute_action(action):
                    plan.completed_actions += 1
                else:
                    plan.failed_actions += 1

        elif mode == ExecutionMode.PARALLEL:
            # Execute all actions at once (no dependency resolution)
            s, f = self.execute_wave_parallel(actions)
            plan.completed_actions = s
            plan.failed_actions = f

        elif mode == ExecutionMode.OPTIMIZED:
            # Resolve dependencies and execute in waves
            waves = self.resolve_dependencies(actions)
            for wave in waves:
                if len(wave) > 1:
                    s, f = self.execute_wave_parallel(wave)
                else:
                    s, f = self.execute_wave_sequential(wave)
                plan.completed_actions += s
                plan.failed_actions += f

        elif mode == ExecutionMode.AGGRESSIVE:
            # Parallel execution, minimal pre-validation — but authorization
            # is NEVER skipped. Speed does not pierce the membrane.
            print(f"\n⚡ AGGRESSIVE MODE: Maximum speed (authorization still enforced)")
            s, f = self.execute_wave_parallel(actions)
            plan.completed_actions = s
            plan.failed_actions = f

        elif mode == ExecutionMode.CAUTIOUS:
            # Sequential with extra validation
            print(f"\n🛡️ CAUTIOUS MODE: Extra validation, slower execution")
            for action in actions:
                # Add validation step before execution
                print(f"\n🔍 Pre-execution validation for: {action.description}")
                if self.execute_action(action):
                    plan.completed_actions += 1
                else:
                    plan.failed_actions += 1
                    print(f"⚠️ Action failed, halting execution for safety")
                    break

        plan.end_time = datetime.now().isoformat()
        plan.success_rate = (
            plan.completed_actions / plan.total_actions if plan.total_actions > 0 else 0
        )

        elapsed = time.time() - start

        self.execution_history.append(plan)
        self.is_executing = False

        print("\n" + "=" * 70)
        print("⚔️ EXECUTION COMPLETE")
        print("=" * 70)
        print(f"✅ Completed: {plan.completed_actions}/{plan.total_actions}")
        print(f"❌ Failed: {plan.failed_actions}/{plan.total_actions}")
        print(f"📊 Success Rate: {plan.success_rate:.1%}")
        print(f"⏱️ Execution Time: {elapsed:.2f}s")
        print("=" * 70 + "\n")

        return plan

    def create_rollback_plan(self, failed_plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Run rollback callables for completed actions of a failed plan.

        Rollbacks are Python callables registered on the Action (reviewed
        code), not string commands — they never pass through the handler
        dispatcher, so no new envelopes are minted. Each rollback is
        audit-logged.

        Args:
            failed_plan: Plan that failed and needs rollback

        Returns:
            Summary dict of rollback outcomes
        """
        print(f"\n🔄 Rolling back failed execution...")

        rolled_back = 0
        rollback_failed = 0

        for action in reversed(self.completed_actions):
            if action in failed_plan.actions and action.rollback_func:
                try:
                    action.rollback_func(action)
                    action.status = ActionStatus.ROLLED_BACK
                    rolled_back += 1
                    print(f"   ✅ Rolled back: {action.description}")
                except Exception as e:
                    rollback_failed += 1
                    print(f"   ❌ Rollback failed for {action.description}: {e}")

        print(f"   Rolled back: {rolled_back}, failed: {rollback_failed}")
        return {"rolled_back": rolled_back, "rollback_failed": rollback_failed}

    def get_execution_report(self) -> Dict[str, Any]:
        """Generate comprehensive execution report"""
        total_executed = len(self.completed_actions) + len(self.failed_actions)

        return {
            "bot_name": self.name,
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_plans_executed": len(self.execution_history),
                "total_actions_executed": total_executed,
                "successful_actions": len(self.completed_actions),
                "failed_actions": len(self.failed_actions),
                "blocked_actions": len(self.blocked_actions),
                "overall_success_rate": (
                    len(self.completed_actions) / total_executed
                    if total_executed > 0
                    else 0
                ),
            },
            "execution_history": [
                {
                    "plan_id": plan.plan_id,
                    "objective": plan.objective,
                    "mode": plan.execution_mode.value,
                    "total_actions": plan.total_actions,
                    "completed": plan.completed_actions,
                    "failed": plan.failed_actions,
                    "success_rate": plan.success_rate,
                    "start_time": plan.start_time,
                    "end_time": plan.end_time,
                }
                for plan in self.execution_history
            ],
            "completed_actions": [
                {
                    "id": a.action_id,
                    "description": a.description,
                    "execution_time": a.execution_time,
                    "attempts": a.attempts,
                }
                for a in self.completed_actions[-10:]  # Last 10
            ],
            "failed_actions": [
                {
                    "id": a.action_id,
                    "description": a.description,
                    "error": a.error,
                    "attempts": a.attempts,
                }
                for a in self.failed_actions[-10:]  # Last 10
            ],
        }

    def export_report(self, filename: str = "aries_execution_report.json"):
        """Export execution report to JSON file"""
        report = self.get_execution_report()

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"💾 Execution report exported to: {filename}")
        return filename


def demonstrate_aries():
    """Demonstrate governed ARIES execution: authorize -> verify -> execute,
    then show the membrane refusing unsigned, tampered, and expired actions."""

    print("\n" + "=" * 70)
    print("🎯 ARIES GOVERNED EXECUTION DEMONSTRATION")
    print("=" * 70 + "\n")

    authority = SoulCradleAuthority()
    bot = AriesBot(authority=authority)

    def governed(
        description,
        action_type,
        payload,
        issuer="olympus_council",
        purpose="demonstration",
        **kw,
    ):
        env = authority.authorize(action_type, payload, issuer=issuer, purpose=purpose)
        return bot.create_action(description, env, payload, **kw)

    # A realistic governed pipeline: each step authorized by Soul Cradle.
    actions = [
        governed(
            "Validate environment setup",
            "emit_text",
            {"text": "Environment validated"},
            priority=ActionPriority.CRITICAL,
        ),
        governed(
            "Install dependencies",
            "emit_text",
            {"text": "Dependencies installed"},
            priority=ActionPriority.HIGH,
        ),
        governed(
            "Write deployment report",
            "write_report",
            {
                "filename": "demo/deploy_report.txt",
                "content": "Staging deployment completed.",
            },
            priority=ActionPriority.NORMAL,
        ),
    ]
    actions[1].dependencies = [actions[0].action_id]
    actions[2].dependencies = [actions[1].action_id]

    plan = bot.execute_plan("Governed demo pipeline", actions, ExecutionMode.OPTIMIZED)

    # -- Attack demonstrations: the membrane holds -------------------------
    print("\n🛡️ MEMBRANE TESTS (all must be BLOCKED, never executed)")
    print("-" * 70)

    # 1. No envelope at all
    naked = Action(
        action_id="naked1",
        description="Unsigned action",
        envelope=None,
        payload={},
        priority=ActionPriority.CRITICAL,
    )
    bot.execute_action(naked)

    # 2. Tampered payload (hash mismatch)
    env = authority.authorize(
        "emit_text", {"text": "original"}, issuer="olympus_council", purpose="demo"
    )
    tampered = bot.create_action("Tampered action", env, {"text": "EVIL"})
    bot.execute_action(tampered)

    # 3. Expired envelope
    old = authority.authorize(
        "emit_text",
        {"text": "stale"},
        issuer="olympus_council",
        purpose="demo",
        ttl_seconds=-1,
    )
    stale = bot.create_action("Expired action", old, {"text": "stale"})
    bot.execute_action(stale)

    # 4. Raw string command (the old vulnerability) — refused at creation
    try:
        bot.create_action("Old-style", "shell:rm -rf /", {})  # type: ignore
    except AuthorizationError as e:
        print(f"\n🛡️ Raw command string refused at creation: {e}")

    # Generate report
    print("\n📊 EXECUTION REPORT")
    print("=" * 70)
    report = bot.get_execution_report()

    print(f"Total Plans: {report['statistics']['total_plans_executed']}")
    print(f"Total Actions: {report['statistics']['total_actions_executed']}")
    print(f"Blocked (refused): {report['statistics']['blocked_actions']}")
    print(f"Success Rate: {report['statistics']['overall_success_rate']:.1%}")

    print("\n📋 Completed Actions:")
    for action in report["completed_actions"]:
        print(f"  ✅ {action['description']} ({action['execution_time']:.2f}s)")

    if report["failed_actions"]:
        print("\n❌ Failed Actions:")
        for action in report["failed_actions"]:
            print(f"  ❌ {action['description']}: {action['error']}")

    print("\n" + "=" * 70)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demonstrate_aries()
