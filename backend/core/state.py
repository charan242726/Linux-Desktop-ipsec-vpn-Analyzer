from enum import Enum

class VpnState(str, Enum):
    IDLE         = "IDLE"          # running, no VPN seen
    VPN_DETECTED = "VPN_DETECTED"  # IKE seen, waiting for user to start
    ANALYZING    = "ANALYZING"     # user started, active analysis
    PAUSED       = "PAUSED"        # user manually paused
    DISCONNECTED = "DISCONNECTED"  # VPN tunnel dropped, final report ready
