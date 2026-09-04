import json
import socket
import subprocess
from datetime import datetime, timezone


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return ""

        return result.stdout.strip()

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def get_interfaces():
    output = run_command(["ip", "-br", "link"])

    interfaces = []

    for line in output.splitlines():
        parts = line.split()

        if len(parts) < 2:
            continue

        interface = parts[0]
        state = parts[1]

        if interface == "lo":
            continue

        interfaces.append(
            {
                "name": interface,
                "state": state,
            }
        )

    return interfaces


def get_routes():
    output = run_command(["ip", "route"])

    routes = []

    for line in output.splitlines():
        routes.append(line)

    return routes


def detect_vpn_interfaces(interfaces):
    vpn_keywords = [
        "tun",
        "tap",
        "ipsec",
        "wg",
        "vpn",
    ]

    candidates = []

    for interface in interfaces:
        name = interface["name"].lower()

        for keyword in vpn_keywords:
            if keyword in name:
                candidates.append(interface)
                break

    return candidates


def get_hostname():
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def detect_network():
    interfaces = get_interfaces()
    routes = get_routes()
    vpn_interfaces = detect_vpn_interfaces(interfaces)

    active_interfaces = [
        interface
        for interface in interfaces
        if interface["state"].upper() == "UP"
    ]

    vpn_interface_detected = len(vpn_interfaces) > 0

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": get_hostname(),

        "interfaces": interfaces,

        "active_interfaces": active_interfaces,

        "vpn": {
            "interface_detected": vpn_interface_detected,
            "candidate_interfaces": vpn_interfaces,
        },

        "routes": routes,

        "status": "VPN_INTERFACE_DETECTED"
        if vpn_interface_detected
        else "NO_VPN_INTERFACE_DETECTED",
    }

    return result


def main():
    result = detect_network()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
