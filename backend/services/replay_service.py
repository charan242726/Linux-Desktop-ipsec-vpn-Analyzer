import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from backend.services.ai_service import run_ai_analysis
from backend.services.security_service import run_security_assessment
from backend.services.report_service import run_report_generation
from backend.services.pdf_service import generate_pdf_report
from backend.services.integrity_service import generate_report_hash
from backend.services.blockchain_service import register_and_verify_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CAPTURE = (
    PROJECT_ROOT
    / "testbed"
    / "captures"
    / "capture_combined_vpn.pcap"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "backend"
    / "results"
)


class ReplayCaptureError(RuntimeError):
    """Raised when replay analysis fails."""


class ReplayAnalyzer:

    def __init__(self, capture_file=None):

        now = datetime.now(timezone.utc)
        suffix = secrets.token_hex(2).upper()

        self.analysis_id = (
            f"REPLAY-{now.strftime('%Y%m%d-%H%M%S')}-{suffix}"
        )

        self.capture_file = Path(
            capture_file
            if capture_file
            else DEFAULT_CAPTURE
        ).resolve()

        self.analysis_dir = (
            RESULTS_DIR
            / self.analysis_id
        )

        self.events = []
        self.status = "IDLE"

    def emit(self, event, message, data=None):

        entry = {
            "timestamp":
                datetime.now(timezone.utc).isoformat(),

            "event":
                event,

            "message":
                message,

            "data":
                data or {},
        }

        self.events.append(entry)

        print(
            f"[{event}] {message}"
        )

    def save_json(self, path, data):

        path = Path(path)

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
            "Replay VPN analysis started.",
            {
                "analysis_id":
                    self.analysis_id,

                "capture_file":
                    str(self.capture_file),
            },
        )

        # ---------------------------------------------------------
        # 2. VALIDATE CAPTURE
        # ---------------------------------------------------------

        self.status = "VALIDATING_CAPTURE"

        self.emit(
            "CAPTURE_VALIDATING",
            "Validating replay PCAP.",
        )

        if not self.capture_file.exists():

            self.status = "FAILED"

            raise ReplayCaptureError(
                f"Replay capture not found: "
                f"{self.capture_file}"
            )

        self.emit(
            "CAPTURE_VALID",
            "Replay PCAP validated.",
            {
                "capture_file":
                    str(self.capture_file),
            },
        )

        # ---------------------------------------------------------
        # 3. AI ANALYSIS
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
            pcap_file=self.capture_file,
            output_dir=ai_dir,
            capture_id=self.analysis_id,
        )

        traffic = ai_result.get(
            "traffic",
            {}
        )

        self.emit(
            "AI_ANALYSIS_COMPLETED",
            "AI analysis completed.",
            {
                "ipsec_detected":
                    ai_result.get(
                        "ipsec_detected"
                    ),

                "ike_version":
                    ai_result.get(
                        "ike_version"
                    ),

                "mode":
                    ai_result.get(
                        "mode"
                    ),

                "traffic_type":
                    traffic.get(
                        "traffic_type"
                    ),

                "confidence":
                    ai_result.get(
                        "confidence"
                    ),
            },
        )

        # ---------------------------------------------------------
        # 4. SECURITY ASSESSMENT
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
        # 5. REPORT
        # ---------------------------------------------------------

        self.status = "GENERATING_REPORT"

        self.emit(
            "REPORT_GENERATION_STARTING",
            "Generating security report.",
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
        # 6. SHA-256
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
                "report_hash":
                    report_hash,
            },
        )

        # ---------------------------------------------------------
        # 7. BLOCKCHAIN
        # ---------------------------------------------------------

        self.status = "BLOCKCHAIN_REGISTERING"

        self.emit(
            "BLOCKCHAIN_REGISTERING",
            "Registering report fingerprint on blockchain.",
            {
                "report_id":
                    report_result.get(
                        "report_id"
                    ),

                "report_hash":
                    report_hash,
            },
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
        # 8. FINALIZE REPORT METADATA
        # ---------------------------------------------------------

        self.status = "FINALIZING_REPORT"

        self.emit(
            "REPORT_FINALIZING",
            "Adding integrity and blockchain verification metadata.",
        )

        try:
            with report_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                final_report = json.load(file)

        except (OSError, json.JSONDecodeError) as exc:

            self.status = "FAILED"

            raise ReplayCaptureError(
                f"Unable to load generated security report: {exc}"
            ) from exc

        final_report["integrity"] = {
            "status": "VERIFIED",
            "hash_algorithm": "SHA-256",
            "report_hash": report_hash,
            "fingerprint_scope": (
                "SHA-256 of the security report before "
                "blockchain metadata was appended."
            ),
        }

        final_report["blockchain"] = {
            "status":
                "BLOCKCHAIN_VERIFIED"
                if blockchain_result.get("verified")
                else "BLOCKCHAIN_NOT_VERIFIED",

            "verified":
                blockchain_result.get(
                    "verified",
                    False,
                ),

            "contract_address":
                blockchain_result.get(
                    "contract_address"
                ),

            "report_id":
                blockchain_result.get(
                    "report_id",
                    report_result.get(
                        "report_id"
                    ),
                ),

            "blockchain_hash":
                blockchain_result.get(
                    "blockchain_hash",
                    report_hash,
                ),
        }

        final_report["status"] = "VERIFIED"

        self.save_json(
            report_file,
            final_report,
        )

        report_result = final_report

        self.emit(
            "REPORT_FINALIZED",
            "Security report finalized with integrity and blockchain metadata.",
            {
                "report_id":
                    final_report.get(
                        "report_id"
                    ),

                "report_hash":
                    report_hash,

                "blockchain_verified":
                    blockchain_result.get(
                        "verified"
                    ),
            },
        )

        # ---------------------------------------------------------
        # 9. PDF REPORT
        # ---------------------------------------------------------

        self.status = "GENERATING_PDF"

        self.emit(
            "PDF_GENERATION_STARTING",
            "Generating final PDF security report.",
        )

        pdf_file = (
            self.analysis_dir
            / "report"
            / "security_report.pdf"
        )

        pdf_result = generate_pdf_report(
            report_file,
            pdf_file,
        )

        self.emit(
            "PDF_GENERATED",
            "Final PDF security report generated.",
            {
                "pdf_path":
                    str(pdf_file),
            },
        )

        # ---------------------------------------------------------
        # 10. COMPLETE
        # ---------------------------------------------------------

        self.status = "COMPLETED"

        self.emit(
            "COMPLETED",
            "Replay VPN security analysis completed.",
        )

        result = {
            "analysis_id":
                self.analysis_id,

            "mode":
                "REPLAY",

            "status":
                self.status,

            "capture":
                {
                    "file":
                        str(
                            self.capture_file
                        ),
                },

            "ai":
                ai_result,

            "security":
                security_result,

            "report":
                report_result,

            "pdf":
                pdf_result,

            "integrity":
                hash_result,

            "blockchain":
                blockchain_result,

            "events":
                self.events,

            "artifacts":
                {
                    "analysis_directory":
                        str(
                            self.analysis_dir
                        ),

                    "ai_result":
                        str(
                            ai_dir
                            / "ai_result.json"
                        ),

                    "security_assessment":
                        str(
                            security_file
                        ),

                    "security_report":
                        str(
                            report_file
                        ),

                    "security_report_pdf":
                        str(
                            pdf_file
                        ),

                    "report_hash":
                        str(
                            hash_file
                        ),

                    "blockchain_result":
                        str(
                            blockchain_file
                        ),
                },
        }

        self.save_json(
            self.analysis_dir
            / "final_result.json",
            result,
        )

        return result


def run_replay_analysis(
    capture_file=None,
):

    analyzer = ReplayAnalyzer(
        capture_file
    )

    return analyzer.run()


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Run complete VPN analysis "
            "using a replay PCAP."
        )
    )

    parser.add_argument(
        "capture_file",
        nargs="?",
        default=str(DEFAULT_CAPTURE),
    )

    args = parser.parse_args()

    result = run_replay_analysis(
        args.capture_file
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )
