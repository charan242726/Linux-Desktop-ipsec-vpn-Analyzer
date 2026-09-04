import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from capture.detector.network_detector import detect_network
from capture.detector.ipsec_detector import detect_ipsec_traffic
from capture.engine.capture_engine import capture_traffic

from backend.services.ai_service import run_ai_analysis
from backend.services.security_service import run_security_assessment
from backend.services.report_service import run_report_generation
from backend.services.integrity_service import generate_report_hash
from backend.services.blockchain_service import register_and_verify_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CAPTURE_DIR = PROJECT_ROOT / "capture" / "runtime"
RESULTS_DIR = PROJECT_ROOT / "backend" / "results"


class AnalysisOrchestrator:
    def __init__(self):
        self.status = "IDLE"
        self.events = []

        now = datetime.now(timezone.utc)
        suffix = secrets.token_hex(2).upper()

        self.analysis_id = (
            f"VPN-{now.strftime('%Y%m%d-%H%M%S')}-{suffix}"
        )

        self.analysis_dir = RESULTS_DIR / self.analysis_id

    def emit(self, event, message, data=None):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "message": message,
            "data": data or {},
        }

        self.events.append(entry)

        print(f"[{event}] {message}")

    def save_json(self, path, data):
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
            )

    def run(self):

        # ---------------------------------------------------------
        # 1. START
        # ---------------------------------------------------------

        self.status = "STARTING"

        self.emit(
            "STARTING",
            "Live VPN analysis started.",
            {
                "analysis_id": self.analysis_id,
            },
        )

        # ---------------------------------------------------------
        # 2. NETWORK DETECTION
        # ---------------------------------------------------------

        self.status = "DETECTING_NETWORK"

        self.emit(
            "DETECTING_NETWORK",
            "Detecting active network interfaces.",
        )

        network = detect_network()

        active_interfaces = network.get(
            "active_interfaces",
            [],
        )

        if not active_interfaces:

            self.status = "FAILED"

            self.emit(
                "FAILED",
                "No active network interface detected.",
            )

            return self.build_result(
                network=network,
            )

        # Prefer the interface associated with the default route.
        interface = self.get_default_route_interface(
            network
        )

        if not interface:
            interface = active_interfaces[0]["name"]

        self.emit(
            "NETWORK_DETECTED",
            f"Active interface detected: {interface}",
            {
                "interface": interface,
            },
        )

        # ---------------------------------------------------------
        # 3. IPSEC / VPN DETECTION
        # ---------------------------------------------------------

        self.status = "DETECTING_VPN"

        self.emit(
            "DETECTING_VPN",
            "Scanning for IKE, ESP and AH traffic.",
        )

        ipsec = detect_ipsec_traffic(
            interface
        )

        if not ipsec.get(
            "ipsec_detected",
            False,
        ):

            self.status = "WAITING_FOR_VPN"

            self.emit(
                "VPN_NOT_DETECTED",
                "No IPsec traffic detected.",
                ipsec,
            )

            result = self.build_result(
                network=network,
                ipsec=ipsec,
            )

            self.save_json(
                self.analysis_dir / "final_result.json",
                result,
            )

            return result

        self.emit(
            "VPN_DETECTED",
            "IPsec traffic detected.",
            ipsec,
        )

        # ---------------------------------------------------------
        # 4. LIVE CAPTURE
        # ---------------------------------------------------------

        self.status = "CAPTURING"

        self.emit(
            "CAPTURE_STARTING",
            "Starting live VPN traffic capture.",
        )

        CAPTURE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        capture_file = (
            CAPTURE_DIR
            / f"{self.analysis_id}.pcap"
        )

        capture = capture_traffic(
            interface=interface,
            output_file=capture_file,
            duration=30,
        )

        if capture.get("status") != "CAPTURE_COMPLETED":

            self.status = "FAILED"

            self.emit(
                "CAPTURE_FAILED",
                "Live packet capture failed.",
                capture,
            )

            return self.build_result(
                network=network,
                ipsec=ipsec,
                capture=capture,
            )

        self.emit(
            "CAPTURE_COMPLETED",
            "Live traffic capture completed.",
            capture,
        )

        # ---------------------------------------------------------
        # 5. AI ANALYSIS
        # ---------------------------------------------------------

        self.status = "ANALYZING"

        self.emit(
            "AI_ANALYSIS_STARTING",
            "Running AI protocol and traffic analysis.",
        )

        ai_dir = (
            self.analysis_dir
            / "ai"
        )

        ai_result = run_ai_analysis(
            pcap_file=capture_file,
            output_dir=ai_dir,
            capture_id=self.analysis_id,
        )

        self.emit(
            "AI_ANALYSIS_COMPLETED",
            "AI analysis completed.",
            {
                "ipsec_detected":
                    ai_result.get("ipsec_detected"),

                "ike_version":
                    ai_result.get("ike_version"),

                "mode":
                    ai_result.get("mode"),

                "traffic_type":
                    ai_result.get("traffic_type"),

                "confidence":
                    ai_result.get("confidence"),
            },
        )

        # ---------------------------------------------------------
        # 6. SECURITY ASSESSMENT
        # ---------------------------------------------------------

        self.status = "ASSESSING"

        self.emit(
            "SECURITY_ASSESSMENT_STARTING",
            "Evaluating VPN security posture.",
        )

        security_file = (
            self.analysis_dir
            / "security"
            / "security_assessment.json"
        )

        security_result = run_security_assessment(
            ai_dir / "ai_result.json",
            security_file,
        )

        self.emit(
            "SECURITY_ASSESSMENT_COMPLETED",
            "Security assessment completed.",
            {
                "security_score":
                    security_result.get(
                        "security_score"
                    ),

                "risk_level":
                    security_result.get(
                        "risk_level"
                    ),

                "findings":
                    len(
                        security_result.get(
                            "findings",
                            [],
                        )
                    ),
            },
        )

        # ---------------------------------------------------------
        # 7. REPORT
        # ---------------------------------------------------------

        self.status = "GENERATING_REPORT"

        self.emit(
            "REPORT_GENERATION_STARTING",
            "Generating professional security report.",
        )

        report_file = (
            self.analysis_dir
            / "report"
            / "security_report.json"
        )

        report_result = run_report_generation(
            ai_dir / "ai_result.json",
            security_file,
            report_file,
        )

        self.emit(
            "REPORT_GENERATED",
            "Security report generated.",
            {
                "report_id":
                    report_result.get(
                        "report_id"
                    ),
            },
        )

        # ---------------------------------------------------------
        # 8. SHA-256
        # ---------------------------------------------------------

        self.status = "HASHING"

        self.emit(
            "HASH_GENERATION_STARTING",
            "Calculating SHA-256 report fingerprint.",
        )

        hash_file = (
            self.analysis_dir
            / "integrity"
            / "report_hash.json"
        )

        hash_result = generate_report_hash(
            report_file,
            hash_file,
        )

        report_hash = hash_result.get(
            "report_hash"
        )

        self.emit(
            "HASH_GENERATED",
            "SHA-256 fingerprint generated.",
            {
                "report_hash": report_hash,
            },
        )

        # ---------------------------------------------------------
        # 9. BLOCKCHAIN
        # ---------------------------------------------------------

        self.status = "BLOCKCHAIN_REGISTERING"

        self.emit(
            "BLOCKCHAIN_REGISTERING",
            "Registering report fingerprint on blockchain.",
        )

        blockchain_result = (
            register_and_verify_report(
                report_id=report_result[
                    "report_id"
                ],
                report_hash=report_hash,
            )
        )

        blockchain_file = (
            self.analysis_dir
            / "blockchain"
            / "blockchain_result.json"
        )

        self.save_json(
            blockchain_file,
            blockchain_result,
        )

        self.emit(
            "BLOCKCHAIN_VERIFIED",
            "Report fingerprint verified on blockchain.",
            {
                "verified":
                    blockchain_result.get(
                        "verified"
                    ),

                "contract_address":
                    blockchain_result.get(
                        "contract_address"
                    ),
            },
        )

        # ---------------------------------------------------------
        # 10. FINAL RESULT
        # ---------------------------------------------------------

        self.status = "COMPLETED"

        self.emit(
            "COMPLETED",
            "Automated VPN security analysis completed.",
        )

        result = self.build_result(
            network=network,
            ipsec=ipsec,
            capture=capture,
            ai=ai_result,
            security=security_result,
            report=report_result,
            integrity=hash_result,
            blockchain=blockchain_result,
        )

        self.save_json(
            self.analysis_dir
            / "final_result.json",
            result,
        )

        return result

    @staticmethod
    def get_default_route_interface(
        network
    ):
        routes = network.get(
            "routes",
            [],
        )

        for route in routes:

            if route.startswith(
                "default "
            ):

                parts = route.split()

                if "dev" in parts:

                    index = parts.index(
                        "dev"
                    )

                    if index + 1 < len(parts):

                        return parts[
                            index + 1
                        ]

        return None

    def build_result(
        self,
        network=None,
        ipsec=None,
        capture=None,
        ai=None,
        security=None,
        report=None,
        integrity=None,
        blockchain=None,
    ):

        return {
            "analysis_id":
                self.analysis_id,

            "status":
                self.status,

            "network":
                network,

            "ipsec":
                ipsec,

            "capture":
                capture,

            "ai":
                ai,

            "security":
                security,

            "report":
                report,

            "integrity":
                integrity,

            "blockchain":
                blockchain,

            "events":
                self.events,

            "artifacts": {
                "analysis_directory":
                    str(
                        self.analysis_dir
                    ),
            },
        }


def run_live_analysis():

    orchestrator = AnalysisOrchestrator()

    return orchestrator.run()


if __name__ == "__main__":

    result = run_live_analysis()

    print(
        json.dumps(
            result,
            indent=2,
        )
    )
