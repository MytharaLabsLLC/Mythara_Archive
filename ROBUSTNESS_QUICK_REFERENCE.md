# ROBUSTNESS FRAMEWORK - QUICK REFERENCE

**For Mythara Bot Developers**

---

## 1-MINUTE INTEGRATION GUIDE

### Add to any bot in 3 steps:

**Step 1: Import**
```python
from robustness_framework import (
    ConnectionPool, InputValidator, RateLimiter,
    retry_on_failure, compute_integrity_hash
)
```

**Step 2: Initialize in `__init__`**
```python
self.rate_limiter = RateLimiter(max_requests=100, time_window=60)
self.validator = InputValidator()
```

**Step 3: Use in your code**
```python
# Validate inputs
email = self.validator.validate_email(user_input)

# Check rate limit
if not self.rate_limiter.is_allowed(user_id):
    return {"error": "Rate limit exceeded"}

# Database with proper cleanup
conn = None
try:
    conn = sqlite3.connect(db_path)
    cursor.execute("SELECT * FROM users")
    conn.commit()
except sqlite3.Error as e:
    logger.error(f"DB error: {e}")
    if conn:
        conn.rollback()
finally:
    if conn:
        conn.close()
```

---

## COMMON PATTERNS

### ✓ Input Validation
```python
# Email
email = validator.validate_email("user@example.com")

# Phone
phone = validator.validate_phone("(555) 123-4567")  # Returns: "5551234567"

# Integer with range
score = validator.validate_integer("75", min_value=0, max_value=100)

# String sanitization
safe_text = validator.sanitize_string(user_input, max_length=500)
```

### ✓ Rate Limiting
```python
if not limiter.is_allowed(user_id):
    remaining = limiter.get_remaining(user_id)
    return {"error": "Rate limit exceeded", "retry_after": remaining}
```

### ✓ Retry Logic
```python
@retry_on_failure(max_retries=3, backoff_factor=2.0)
def unreliable_operation():
    # Your code here
    pass
```

### ✓ Integrity Hashing
```python
data = {"user_id": "123", "action": "login"}
hash = compute_integrity_hash(data)
# Store hash with record for tamper detection
```

### ✓ Connection Pooling
```python
pool = ConnectionPool("database.db", pool_size=5)

with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    # Auto-commit on success, rollback on error
```

---

## BEFORE/AFTER EXAMPLES

### Example 1: Database Connection
```python
# ❌ BEFORE (BAD - connection leak)
conn = sqlite3.connect("db.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
conn.commit()
conn.close()  # Only closes if no exception!

# ✅ AFTER (GOOD - guaranteed cleanup)
conn = None
try:
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    conn.commit()
except sqlite3.Error as e:
    logger.error(f"Error: {e}")
    if conn:
        conn.rollback()
finally:
    if conn:
        conn.close()
```

### Example 2: Error Handling
```python
# ❌ BEFORE (BAD - silent failure)
try:
    result = risky_operation()
except:
    pass  # Error silently ignored!

# ✅ AFTER (GOOD - logged with context)
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    error_recovery.record_error(e, "risky_operation")
    raise
```

### Example 3: Input Validation
```python
# ❌ BEFORE (BAD - SQL injection vulnerable)
user_id = request.get("user_id")
cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

# ✅ AFTER (GOOD - parameterized + validated)
user_id = validator.validate_integer(request.get("user_id"))
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

---

## QUICK TESTS

### Test if framework is working:
```bash
# 1. Test framework
python core/source_proprietary/robustness_framework.py

# 2. Run full test suite
python tests/test_robustness_improvements.py

# 3. Check your bot
python Commercial/<your_bot>.py
```

---

## CHEAT SHEET

| Feature | Class/Function | Usage |
|---------|---------------|-------|
| Connection Pool | `ConnectionPool` | `with pool.get_connection() as conn:` |
| Email Validation | `InputValidator.validate_email()` | `email = validator.validate_email(input)` |
| Phone Validation | `InputValidator.validate_phone()` | `phone = validator.validate_phone(input)` |
| Integer Validation | `InputValidator.validate_integer()` | `score = validator.validate_integer(input, 0, 100)` |
| Rate Limiting | `RateLimiter.is_allowed()` | `if limiter.is_allowed(user_id):` |
| Retry Logic | `@retry_on_failure` | `@retry_on_failure(max_retries=3)` |
| Integrity Hash | `compute_integrity_hash()` | `hash = compute_integrity_hash(data)` |
| Error Recording | `ErrorRecovery.record_error()` | `recovery.record_error(e, "function_name")` |

---

## GOTCHAS & TIPS

### ⚠️ Don't do this:
```python
# ❌ Bare except
try:
    operation()
except:  # Catches ALL exceptions including KeyboardInterrupt!
    pass

# ✅ Specific exceptions
try:
    operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except sqlite3.Error as e:
    logger.error(f"Database error: {e}")
```

### ⚠️ Don't do this:
```python
# ❌ String formatting in SQL
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### ⚠️ Don't do this:
```python
# ❌ Connection not closed on error
conn = sqlite3.connect("db.db")
cursor.execute("SELECT * FROM users")
conn.close()

# ✅ Always use try-finally
conn = None
try:
    conn = sqlite3.connect("db.db")
    cursor.execute("SELECT * FROM users")
finally:
    if conn:
        conn.close()
```

---

## SUPPORT

**Documentation:** `ROBUSTNESS_IMPROVEMENTS_REPORT.md`  
**Test Suite:** `tests/test_robustness_improvements.py`  
**Framework Code:** `core/source_proprietary/robustness_framework.py`

**Questions?** Read the full report for detailed explanations and examples.

---

✅ **Remember:** Robustness is not optional for production systems!
