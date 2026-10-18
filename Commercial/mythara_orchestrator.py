# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Mythara Orchestrator - Central Token-Based API
All bots authenticate here. VP Bot manages everything.

SSIP Integration:
- Token-based Sanctification (only authorized actions proceed)
- Integrity hashes on all decisions
- Blessings Reservoir for bot performance tracking
- Shadow_Resolver fallback if token invalid
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

# Master VP token (sanctified - never changes)
VP_MASTER_TOKEN = hashlib.sha256("MYTHARA_VP_2025".encode()).hexdigest()

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'mythara_orchestrator.db')

def init_db():
    """Initialize SQLite database for shared state."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Bot registry
    c.execute('''CREATE TABLE IF NOT EXISTS bots
                 (bot_id TEXT PRIMARY KEY,
                  bot_name TEXT,
                  status TEXT,
                  last_run TEXT,
                  performance_score INTEGER,
                  token TEXT)''')
    
    # Decisions log (SSIP audit trail)
    c.execute('''CREATE TABLE IF NOT EXISTS decisions
                 (decision_id TEXT PRIMARY KEY,
                  timestamp TEXT,
                  bot_id TEXT,
                  action TEXT,
                  approved BOOLEAN,
                  reason TEXT,
                  integrity_hash TEXT)''')
    
    # Tasks queue
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (task_id TEXT PRIMARY KEY,
                  assigned_to TEXT,
                  task_type TEXT,
                  payload TEXT,
                  status TEXT,
                  created_at TEXT,
                  completed_at TEXT)''')
    
    # Shared state (prospect tracking, etc.)
    c.execute('''CREATE TABLE IF NOT EXISTS shared_state
                 (key TEXT PRIMARY KEY,
                  value TEXT,
                  updated_at TEXT)''')
    
    conn.commit()
    conn.close()

init_db()


# ============================================================================
# TOKEN VALIDATION (Sanctification Pattern)
# ============================================================================

def validate_token(token: str, bot_id: str) -> bool:
    """Validate bot token using SSIP sanctification pattern."""
    
    # VP Master token always valid
    if token == VP_MASTER_TOKEN:
        return True
    
    # Check if bot has valid token in registry
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT token FROM bots WHERE bot_id = ?", (bot_id,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0] == token:
        return True
    
    # Shadow_Resolver: deny if token invalid
    return False


def generate_integrity_hash(data: Dict) -> str:
    """Generate SSIP integrity hash for decision."""
    canonical = json.dumps(data, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'operational',
        'service': 'Mythara Orchestrator',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/register_bot', methods=['POST'])
def register_bot():
    """Register new bot with orchestrator."""
    data = request.json
    
    # Only VP can register bots
    if not validate_token(data.get('vp_token'), 'vp_bot'):
        return jsonify({'error': 'Unauthorized - Invalid VP token'}), 401
    
    bot_id = data['bot_id']
    bot_name = data['bot_name']
    
    # Generate unique token for this bot
    bot_token = hashlib.sha256(f"{bot_id}{datetime.now().isoformat()}".encode()).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO bots 
                 (bot_id, bot_name, status, last_run, performance_score, token)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (bot_id, bot_name, 'registered', datetime.now().isoformat(), 100, bot_token))
    conn.commit()
    conn.close()
    
    return jsonify({
        'bot_id': bot_id,
        'bot_token': bot_token,
        'status': 'registered',
        'message': 'Bot registered successfully'
    })


@app.route('/request_approval', methods=['POST'])
def request_approval():
    """
    Worker bot requests approval for action.
    VP Bot validates and approves/denies.
    """
    data = request.json
    bot_id = data.get('bot_id')
    token = data.get('token')
    action = data.get('action')
    reason = data.get('reason')
    
    # Validate token
    if not validate_token(token, bot_id):
        return jsonify({'approved': False, 'reason': 'Invalid token'}), 401
    
    # VP Bot decision logic
    approved = True  # Default approve (VP trusts registered bots)
    
    # Special rules (Sanctified)
    if action == 'send_email' and data.get('count', 0) > 100:
        approved = False  # Block spam
        reason = 'Email limit exceeded (max 100/day)'
    
    if action == 'deploy_bot' and data.get('cost', 0) > 500:
        approved = False  # Block expensive deployments
        reason = 'Budget exceeded (max $500/month)'
    
    # Log decision with integrity hash
    decision_id = hashlib.sha256(f"{bot_id}{action}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    integrity_hash = generate_integrity_hash({
        'bot_id': bot_id,
        'action': action,
        'approved': approved
    })
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO decisions 
                 (decision_id, timestamp, bot_id, action, approved, reason, integrity_hash)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (decision_id, datetime.now().isoformat(), bot_id, action, approved, reason, integrity_hash))
    conn.commit()
    conn.close()
    
    return jsonify({
        'approved': approved,
        'decision_id': decision_id,
        'reason': reason,
        'integrity_hash': integrity_hash
    })


@app.route('/get_task', methods=['POST'])
def get_task():
    """Worker bot requests next task from queue."""
    data = request.json
    bot_id = data.get('bot_id')
    token = data.get('token')
    
    if not validate_token(token, bot_id):
        return jsonify({'error': 'Invalid token'}), 401
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get next pending task for this bot type
    c.execute("""SELECT task_id, task_type, payload 
                 FROM tasks 
                 WHERE assigned_to = ? AND status = 'pending'
                 ORDER BY created_at ASC
                 LIMIT 1""", (bot_id,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        task_id, task_type, payload = result
        return jsonify({
            'task_id': task_id,
            'task_type': task_type,
            'payload': json.loads(payload) if payload else {}
        })
    
    return jsonify({'task': None})


@app.route('/complete_task', methods=['POST'])
def complete_task():
    """Worker bot reports task completion."""
    data = request.json
    task_id = data.get('task_id')
    bot_id = data.get('bot_id')
    token = data.get('token')
    result = data.get('result')
    
    if not validate_token(token, bot_id):
        return jsonify({'error': 'Invalid token'}), 401
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE tasks 
                 SET status = 'completed', completed_at = ?
                 WHERE task_id = ?""",
              (datetime.now().isoformat(), task_id))
    
    # Update bot performance score
    c.execute("""UPDATE bots 
                 SET last_run = ?, performance_score = performance_score + 1
                 WHERE bot_id = ?""",
              (datetime.now().isoformat(), bot_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'completed'})


@app.route('/create_task', methods=['POST'])
def create_task():
    """VP Bot creates task for worker bot."""
    data = request.json
    
    # Only VP can create tasks
    if not validate_token(data.get('vp_token'), 'vp_bot'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    task_id = hashlib.sha256(f"{data['assigned_to']}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO tasks 
                 (task_id, assigned_to, task_type, payload, status, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (task_id,
               data['assigned_to'],
               data['task_type'],
               json.dumps(data.get('payload', {})),
               'pending',
               datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({'task_id': task_id, 'status': 'created'})


@app.route('/get_state', methods=['POST'])
def get_state():
    """Get shared state value."""
    data = request.json
    key = data.get('key')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM shared_state WHERE key = ?", (key,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return jsonify({'key': key, 'value': json.loads(result[0])})
    
    return jsonify({'key': key, 'value': None})


@app.route('/set_state', methods=['POST'])
def set_state():
    """Set shared state value."""
    data = request.json
    key = data.get('key')
    value = data.get('value')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO shared_state (key, value, updated_at)
                 VALUES (?, ?, ?)""",
              (key, json.dumps(value), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'updated'})


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Get orchestrator dashboard data."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get all bots
    c.execute("SELECT * FROM bots")
    bots = [dict(zip(['bot_id', 'bot_name', 'status', 'last_run', 'performance_score', 'token'], row)) for row in c.fetchall()]
    
    # Get recent decisions
    c.execute("SELECT * FROM decisions ORDER BY timestamp DESC LIMIT 10")
    decisions = [dict(zip(['decision_id', 'timestamp', 'bot_id', 'action', 'approved', 'reason', 'integrity_hash'], row)) for row in c.fetchall()]
    
    # Get pending tasks
    c.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
    pending_tasks = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'bots': bots,
        'recent_decisions': decisions,
        'pending_tasks': pending_tasks,
        'orchestrator_status': 'operational',
        'master_token': VP_MASTER_TOKEN[:8] + '...',  # Show first 8 chars only
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("🎯 Mythara Orchestrator Starting...")
    print(f"   VP Master Token: {VP_MASTER_TOKEN}")
    print(f"   Database: {DB_PATH}")
    print(f"   API: http://localhost:5000")
    print("\nEndpoints:")
    print("   GET  /health - Health check")
    print("   GET  /dashboard - Orchestrator dashboard")
    print("   POST /register_bot - Register new bot")
    print("   POST /request_approval - Request action approval")
    print("   POST /get_task - Get next task")
    print("   POST /complete_task - Mark task complete")
    print("   POST /create_task - Create new task (VP only)")
    print("   POST /get_state - Get shared state")
    print("   POST /set_state - Set shared state")
    print("\n🔐 Token-based authentication active")
    print("📊 SSIP integrity hashing enabled")
    print("\nStarting server...\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
