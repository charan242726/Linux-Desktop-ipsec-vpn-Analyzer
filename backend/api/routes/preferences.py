from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.database.db import (
    get_preferences, set_preference,
    set_pin, clear_pin, verify_pin,
)

router = APIRouter(prefix="/preferences")

# ── Models ────────────────────────────────────────────────────

class PreferencesUpdate(BaseModel):
    notifications_enabled: Optional[bool] = None
    network_interface: Optional[str] = None
    vpn_detection: Optional[bool] = None
    ai_analysis: Optional[bool] = None
    security_assessment: Optional[bool] = None

class SetPinRequest(BaseModel):
    pin: str           # 4–8 digit PIN (validated client-side)

class VerifyPinRequest(BaseModel):
    pin: str

# ── Routes ────────────────────────────────────────────────────

@router.get("")
def read_preferences():
    """Return all user preferences. Never exposes pin_hash."""
    prefs = get_preferences()
    # Strip the internal hash — frontend only needs pin_enabled flag
    prefs.pop("pin_hash", None)
    # Cast boolean strings to actual booleans for JSON
    bool_keys = {
        "notifications_enabled", "pin_enabled",
        "vpn_detection", "ai_analysis", "security_assessment",
    }
    for k in bool_keys:
        if k in prefs:
            prefs[k] = prefs[k].lower() == "true"
    return prefs


@router.put("")
def update_preferences(body: PreferencesUpdate):
    """Update one or more preference values."""
    mapping = {
        "notifications_enabled": body.notifications_enabled,
        "network_interface": body.network_interface,
        "vpn_detection": body.vpn_detection,
        "ai_analysis": body.ai_analysis,
        "security_assessment": body.security_assessment,
    }
    for key, val in mapping.items():
        if val is not None:
            set_preference(key, str(val).lower() if isinstance(val, bool) else str(val))
    return {"ok": True}


@router.post("/pin")
def create_or_update_pin(body: SetPinRequest):
    """Set or change the app lock PIN."""
    if not body.pin.isdigit() or not (4 <= len(body.pin) <= 8):
        raise HTTPException(status_code=422, detail="PIN must be 4–8 digits")
    set_pin(body.pin)
    return {"ok": True, "pin_enabled": True}


@router.delete("/pin")
def remove_pin():
    """Disable the app lock PIN."""
    clear_pin()
    return {"ok": True, "pin_enabled": False}


@router.post("/pin/verify")
def check_pin(body: VerifyPinRequest):
    """Verify the PIN. Returns 200 + {ok: true} or 401."""
    if verify_pin(body.pin):
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Incorrect PIN")
