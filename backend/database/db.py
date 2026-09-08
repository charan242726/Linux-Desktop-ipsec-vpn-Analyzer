import sqlite3
import json
import logging
import threading
import hashlib
import os
from backend.config import DB_PATH

logger = logging.getLogger(__name__)

# One connection per thread — SQLite's safest pattern
_local = threading.local()

def get_conn() -> sqlite3.Connection:
    """Returns a thread-local SQLite connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(str(DB_PATH), check_same_thread=True)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")  # allows concurrent reads
    return _local.conn

def close_conn():
    """Call on thread shutdown."""
    if hasattr(_local, "conn") and _local.conn:
        _local.conn.close()
        _local.conn = None

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                risk_level TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER REFERENCES sessions(id),
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                findings_json TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.commit()
    logger.info("Database initialized")

def create_session() -> int:
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO sessions DEFAULT VALUES")
        conn.commit()
        return cur.lastrowid

def save_findings(session_id: int, findings: dict):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO findings (session_id, findings_json) VALUES (?, ?)",
            (session_id, json.dumps(findings))
        )
        risk = findings.get("risk_level", "UNKNOWN")
        conn.execute(
            "UPDATE sessions SET risk_level = ? WHERE id = ?",
            (risk, session_id)
        )
        conn.commit()

def finalize_session(session_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,)
        )
        conn.commit()
    logger.info(f"Session {session_id} finalized")

# ─────────────────────────────────────────────────────────────
# Preferences
# ─────────────────────────────────────────────────────────────

DEFAULT_PREFERENCES = {
    "notifications_enabled": "true",
    "pin_enabled": "false",
    "network_interface": "Automatic",
    "vpn_detection": "true",
    "ai_analysis": "true",
    "security_assessment": "true",
}

def get_preferences() -> dict:
    """Return all preferences as a dict, filling in defaults for missing keys."""
    with get_conn() as conn:
        rows = conn.execute("SELECT key, value FROM preferences").fetchall()
        stored = {r["key"]: r["value"] for r in rows}
    # Merge defaults so callers always get every key
    result = dict(DEFAULT_PREFERENCES)
    result.update(stored)
    return result

def set_preference(key: str, value: str):
    """Upsert a single preference value."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO preferences (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value)
        )
        conn.commit()

# ── PIN helpers ─────────────────────────────────────────────

def _hash_pin(pin: str, salt: bytes) -> str:
    """PBKDF2-HMAC-SHA256, 260 000 iterations — fast enough, secure enough."""
    dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 260_000)
    return salt.hex() + ":" + dk.hex()

def set_pin(pin: str):
    """Hash + store the PIN. Also marks pin_enabled = true."""
    salt = os.urandom(16)
    hashed = _hash_pin(pin, salt)
    set_preference("pin_hash", hashed)
    set_preference("pin_enabled", "true")
    logger.info("PIN updated")

def clear_pin():
    """Remove PIN and disable lock."""
    with get_conn() as conn:
        conn.execute("DELETE FROM preferences WHERE key='pin_hash'")
        conn.commit()
    set_preference("pin_enabled", "false")
    logger.info("PIN cleared")

def verify_pin(pin: str) -> bool:
    """Return True if the provided PIN matches the stored hash."""
    prefs = get_preferences()
    pin_hash = prefs.get("pin_hash", "")
    if not pin_hash:
        return False
    try:
        salt_hex, dk_hex = pin_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        return _hash_pin(pin, salt) == pin_hash
    except Exception:
        return False

def get_all_reports() -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY started_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

def get_report_by_id(report_id: int) -> dict | None:
    with get_conn() as conn:
        session = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (report_id,)
        ).fetchone()
        if not session:
            return None
        findings = conn.execute(
            "SELECT findings_json FROM findings WHERE session_id = ? ORDER BY recorded_at",
            (report_id,)
        ).fetchall()
        return {
            **dict(session),
            "findings": [json.loads(f["findings_json"]) for f in findings]
        }
