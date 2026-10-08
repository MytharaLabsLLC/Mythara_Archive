"""Tests for Commercial/drmythara_security.py — the DrMythara ePHI
security layer. Every test asserts a real control; none of these may
fail in a shippable build."""

import base64
import os
import sqlite3
import stat
import sys
from datetime import timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Commercial"))

from drmythara_security import (
    EncryptedSQLite,
    EncryptedFile,
    DataKey,
    MissingDataKeyError,
    SecurityError,
    AuthenticationError,
    AccountLockedError,
    SessionError,
    AccessDeniedError,
    BackupError,
    PasswordHasher,
    UserStore,
    SessionManager,
    BreakGlass,
    AuditReview,
    BackupManager,
    assert_subject_allowed,
)


# -- passwords ------------------------------------------------------------

def test_hash_and_verify_roundtrip():
    h = PasswordHasher.hash_password("correct-horse-12")
    assert PasswordHasher.verify_password("correct-horse-12", h)
    assert not PasswordHasher.verify_password("wrong-password", h)


def test_hash_format_is_versioned_pbkdf2():
    h = PasswordHasher.hash_password("another-long-pw")
    algo, iters, salt_b64, dk_b64 = h.split("$")
    assert algo == "pbkdf2-sha256"
    assert int(iters) >= 600_000
    assert len(base64.b64decode(salt_b64)) == 32


def test_salts_are_unique():
    assert (PasswordHasher.hash_password("same-password-1")
            != PasswordHasher.hash_password("same-password-1"))


def test_short_password_rejected():
    with pytest.raises(ValueError):
        PasswordHasher.hash_password("short")


def test_garbage_hash_never_verifies():
    assert not PasswordHasher.verify_password("anything", "not-a-hash")
    assert not PasswordHasher.verify_password("anything", "")


# -- data key --------------------------------------------------------------

def test_generate_key_is_valid_fernet():
    key = DataKey.generate_key()
    f = DataKey.resolve(key, strict=True)
    assert f.decrypt(f.encrypt(b"hello")) == b"hello"


def test_missing_key_strict_raises(monkeypatch):
    monkeypatch.delenv("DRMYTHARA_DATA_KEY", raising=False)
    with pytest.raises(MissingDataKeyError):
        DataKey.resolve(strict=True)


def test_missing_key_non_strict_returns_none(monkeypatch):
    monkeypatch.delenv("DRMYTHARA_DATA_KEY", raising=False)
    assert DataKey.resolve(strict=False) is None


def test_env_key_used(monkeypatch):
    key = DataKey.generate_key()
    monkeypatch.setenv("DRMYTHARA_DATA_KEY", key)
    f = DataKey.resolve(strict=True)
    assert f.decrypt(f.encrypt(b"x")) == b"x"


def test_bad_key_rejected():
    with pytest.raises(SecurityError):
        DataKey.resolve("not-a-real-key", strict=True)


def test_key_rotation(tmp_path):
    old_key = DataKey.generate_key()
    new_key = DataKey.generate_key()
    store = str(tmp_path / "store.db")
    EncryptedFile.write(store, b"sensitive bytes",
                        DataKey.resolve(old_key, strict=True))
    DataKey.rotate(old_key, new_key, [store])
    new_f = DataKey.resolve(new_key, strict=True)
    assert EncryptedFile.read(store, new_f) == b"sensitive bytes"
    old_f = DataKey.resolve(old_key, strict=True)
    with pytest.raises(SecurityError):
        EncryptedFile.read(store, old_f)


# -- encrypted file --------------------------------------------------------

def test_encrypted_file_roundtrip_and_perms(tmp_path):
    key = DataKey.generate_key()
    f = DataKey.resolve(key, strict=True)
    p = str(tmp_path / "secret.bin")
    EncryptedFile.write(p, b"phi data", f)
    assert EncryptedFile.read(p, f) == b"phi data"
    assert stat.S_IMODE(os.stat(p).st_mode) == 0o600
    # ciphertext on disk, not plaintext
    assert b"phi data" not in open(p, "rb").read()


def test_encrypted_file_wrong_key_fails(tmp_path):
    p = str(tmp_path / "secret.bin")
    EncryptedFile.write(p, b"phi data",
                        DataKey.resolve(DataKey.generate_key(), strict=True))
    with pytest.raises(SecurityError):
        EncryptedFile.read(p, DataKey.resolve(DataKey.generate_key(),
                                              strict=True))


def test_tampered_file_fails(tmp_path):
    key = DataKey.generate_key()
    f = DataKey.resolve(key, strict=True)
    p = str(tmp_path / "secret.bin")
    EncryptedFile.write(p, b"phi data", f)
    raw = bytearray(open(p, "rb").read())
    raw[20] ^= 0xFF
    open(p, "wb").write(bytes(raw))
    with pytest.raises(SecurityError):
        EncryptedFile.read(p, f)


# -- encrypted sqlite -------------------------------------------------------

def _make_db(path, fernet):
    with EncryptedSQLite(path, fernet) as conn:
        conn.execute("CREATE TABLE t (v TEXT)")
        conn.execute("INSERT INTO t VALUES ('hello')")


def test_encrypted_sqlite_roundtrip(tmp_path):
    f = DataKey.resolve(DataKey.generate_key(), strict=True)
    p = str(tmp_path / "enc.db")
    _make_db(p, f)
    with EncryptedSQLite(p, f) as conn:
        assert conn.execute("SELECT v FROM t").fetchone()[0] == "hello"
    assert b"hello" not in open(p, "rb").read()  # encrypted at rest


def test_encrypted_sqlite_wrong_key_fails(tmp_path):
    f = DataKey.resolve(DataKey.generate_key(), strict=True)
    p = str(tmp_path / "enc.db")
    _make_db(p, f)
    with pytest.raises(SecurityError):
        with EncryptedSQLite(
                p, DataKey.resolve(DataKey.generate_key(), strict=True)):
            pass


def test_encrypted_sqlite_no_temp_left_behind(tmp_path):
    f = DataKey.resolve(DataKey.generate_key(), strict=True)
    p = str(tmp_path / "enc.db")
    _make_db(p, f)
    before = set(os.listdir(tmp_path))
    with EncryptedSQLite(p, f) as conn:
        conn.execute("SELECT 1")
    assert set(os.listdir(tmp_path)) == before  # temp plaintext removed


# -- users -------------------------------------------------------------------

@pytest.fixture()
def memdb():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_user_create_and_authenticate(memdb):
    store = UserStore(memdb)
    store.create_user("dr.alvarez", "long-secure-password", role="admin")
    user = store.authenticate("dr.alvarez", "long-secure-password")
    assert user == {"user_id": "dr.alvarez", "role": "admin"}


def test_authenticate_wrong_password_generic_message(memdb):
    store = UserStore(memdb)
    store.create_user("nurse.joy", "long-secure-password")
    with pytest.raises(AuthenticationError,
                       match="Invalid user ID or password"):
        store.authenticate("nurse.joy", "wrong-password-xyz")


def test_authenticate_unknown_user_same_message(memdb):
    store = UserStore(memdb)
    with pytest.raises(AuthenticationError,
                       match="Invalid user ID or password"):
        store.authenticate("ghost", "whatever-password")


def test_lockout_after_five_failures(memdb):
    store = UserStore(memdb)
    store.create_user("tech.sam", "long-secure-password")
    for _ in range(4):
        with pytest.raises(AuthenticationError):
            store.authenticate("tech.sam", "bad-password-0000")
    with pytest.raises(AccountLockedError):
        store.authenticate("tech.sam", "bad-password-0000")
    # even the right password is refused while locked
    with pytest.raises(AccountLockedError):
        store.authenticate("tech.sam", "long-secure-password")


def test_unlock_restores_access(memdb):
    store = UserStore(memdb)
    store.create_user("tech.sam", "long-secure-password")
    for _ in range(5):
        try:
            store.authenticate("tech.sam", "bad-password-0000")
        except (AuthenticationError, AccountLockedError):
            pass
    store.unlock_user("tech.sam")
    assert store.authenticate("tech.sam", "long-secure-password")


def test_successful_login_resets_counter(memdb):
    store = UserStore(memdb)
    store.create_user("dr.b", "long-secure-password")
    for _ in range(4):
        with pytest.raises(AuthenticationError):
            store.authenticate("dr.b", "bad-password-0000")
    store.authenticate("dr.b", "long-secure-password")  # resets to 0
    for _ in range(4):
        with pytest.raises(AuthenticationError):
            store.authenticate("dr.b", "bad-password-0000")
    # 5th failure after reset → locked (proves the counter reset)
    with pytest.raises(AccountLockedError):
        store.authenticate("dr.b", "bad-password-0000")


def test_duplicate_user_rejected(memdb):
    store = UserStore(memdb)
    store.create_user("dup", "long-secure-password")
    with pytest.raises(ValueError):
        store.create_user("dup", "another-long-password")


# -- sessions ------------------------------------------------------------------

def test_session_create_validate_revoke():
    sm = SessionManager()
    tok = sm.create_session("u1", "clinician")
    assert sm.validate(tok)["user_id"] == "u1"
    sm.revoke(tok)
    with pytest.raises(SessionError):
        sm.validate(tok)


def test_session_idle_timeout():
    sm = SessionManager(idle_timeout=timedelta(milliseconds=1))
    tok = sm.create_session("u1", "clinician")
    import time
    time.sleep(0.01)
    with pytest.raises(SessionError, match="inactivity"):
        sm.validate(tok)


def test_session_absolute_timeout():
    sm = SessionManager(absolute_timeout=timedelta(milliseconds=1))
    tok = sm.create_session("u1", "clinician")
    import time
    time.sleep(0.01)
    with pytest.raises(SessionError, match="expired"):
        sm.validate(tok)


def test_unknown_token_rejected():
    with pytest.raises(SessionError):
        SessionManager().validate("bogus")


# -- break glass -----------------------------------------------------------------

def test_breakglass_needs_secret(monkeypatch):
    monkeypatch.delenv("DRMYTHARA_BREAKGLASS_SECRET", raising=False)
    with pytest.raises(SecurityError):
        BreakGlass()


def test_breakglass_issue_validate():
    bg = BreakGlass(secret="test-secret-value")
    issued = bg.issue_token("officer", "patient coding blue, records needed")
    rec = bg.validate_token(issued["token"])
    assert rec["operator_id"] == "officer"
    assert "coding blue" in rec["reason"]


def test_breakglass_needs_reason():
    bg = BreakGlass(secret="test-secret-value")
    with pytest.raises(ValueError):
        bg.issue_token("officer", "   ")


def test_breakglass_bad_token():
    bg = BreakGlass(secret="test-secret-value")
    with pytest.raises(AuthenticationError):
        bg.validate_token("bg_bogus")


def test_breakglass_expiry():
    bg = BreakGlass(secret="test-secret-value", ttl_minutes=0)
    issued = bg.issue_token("officer", "urgent")
    with pytest.raises(AuthenticationError):
        bg.validate_token(issued["token"])


# -- audit review ------------------------------------------------------------------

def test_audit_chain_verifies(memdb):
    audit = AuditReview(memdb)
    audit.log_event("u1", "login")
    audit.log_event("u1", "backup", detail="nightly")
    result = audit.verify_chain()
    assert result["ok"] and result["events"] == 2


def test_audit_tamper_detected(memdb):
    audit = AuditReview(memdb)
    audit.log_event("u1", "login")
    memdb.execute("UPDATE drmy_security_events SET action='forged'")
    memdb.commit()
    assert not audit.verify_chain()["ok"]


def test_review_signoff_workflow(memdb):
    audit = AuditReview(memdb)
    audit.log_event("u1", "login")
    audit.log_event("u2", "break_glass_login", emergency=True)
    status = audit.review_status()
    assert status["pending_count"] == 2
    assert status["pending_emergency"] == 1
    assert status["last_review"] is None
    result = audit.sign_off("reviewer.ana", note="weekly review")
    assert result["events_reviewed"] == 2
    assert result["reviewer"] == "reviewer.ana"
    status2 = audit.review_status()
    assert status2["pending_count"] == 0
    assert status2["last_review"] is not None


# -- subject scoping -----------------------------------------------------------------

def test_subject_scoping():
    assert_subject_allowed("patient-1", "patient-1")  # own records: ok
    assert_subject_allowed(None, "anyone")  # admin session: ok
    with pytest.raises(AccessDeniedError):
        assert_subject_allowed("patient-1", "patient-2")


# -- backups ----------------------------------------------------------------------------

def _enc_db(tmp_path):
    f = DataKey.resolve(DataKey.generate_key(), strict=True)
    p = str(tmp_path / "store.db")
    with EncryptedSQLite(p, f) as conn:
        conn.execute("CREATE TABLE t (v TEXT)")
        conn.execute("INSERT INTO t VALUES ('data')")
    return p, f


def test_backup_and_restore_roundtrip(tmp_path):
    p, f = _enc_db(tmp_path)
    mgr = BackupManager(str(tmp_path / "backups"))
    made = mgr.backup(p, f, "test")
    assert made["backup"].endswith(".bak")
    assert b"data" not in open(made["backup"], "rb").read()  # encrypted

    target = str(tmp_path / "restored.db")
    result = mgr.restore(made["backup"], target, f,
                         verify_opens=lambda path: _enc_db_check(path, f))
    assert result["sha256"] == made["sha256"]
    with EncryptedSQLite(target, f) as conn:
        assert conn.execute("SELECT v FROM t").fetchone()[0] == "data"


def _enc_db_check(path, f):
    with EncryptedSQLite(path, f) as conn:
        conn.execute("SELECT COUNT(*) FROM t").fetchone()


def test_restore_rejects_tampered_backup(tmp_path):
    p, f = _enc_db(tmp_path)
    mgr = BackupManager(str(tmp_path / "backups"))
    made = mgr.backup(p, f, "test")
    raw = bytearray(open(made["backup"], "rb").read())
    raw[30] ^= 0xFF
    open(made["backup"], "wb").write(bytes(raw))
    with pytest.raises(BackupError):
        mgr.restore(made["backup"], str(tmp_path / "r.db"), f)


def test_restore_rejects_wrong_key(tmp_path):
    p, f = _enc_db(tmp_path)
    mgr = BackupManager(str(tmp_path / "backups"))
    made = mgr.backup(p, f, "test")
    other = DataKey.resolve(DataKey.generate_key(), strict=True)
    with pytest.raises(BackupError):
        mgr.restore(made["backup"], str(tmp_path / "r.db"), other)


def test_test_restore_drill_logs_ok(tmp_path):
    p, f = _enc_db(tmp_path)
    mgr = BackupManager(str(tmp_path / "backups"))
    report = mgr.test_restore(p, f, "drill",
                              verify_opens=lambda path: _enc_db_check(path, f))
    assert report["ok"] is True
    assert report["match"] is True
