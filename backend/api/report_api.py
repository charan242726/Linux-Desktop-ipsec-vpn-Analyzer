import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = (
    PROJECT_ROOT
    / "backend"
    / "results"
)

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"],
)


def validate_analysis_id(
    analysis_id: str,
):
    """
    Prevent path traversal and ensure that
    the analysis ID refers to a single directory name.
    """

    if (
        not analysis_id
        or Path(analysis_id).name != analysis_id
        or analysis_id in {".", ".."}
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid analysis ID",
        )


def get_analysis_dir(
    analysis_id: str,
):
    validate_analysis_id(
        analysis_id
    )

    return (
        RESULTS_DIR
        / analysis_id
    )


def load_final_result(
    analysis_dir: Path,
):
    final_file = (
        analysis_dir
        / "final_result.json"
    )

    if not final_file.exists():
        return None

    try:
        with final_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None


def build_report_summary(
    analysis_id: str,
    result: dict,
):
    report = result.get(
        "report",
        {},
    )

    integrity = result.get(
        "integrity",
        {},
    )

    blockchain = result.get(
        "blockchain",
        {},
    )

    artifacts = result.get(
        "artifacts",
        {},
    )

    report_file = (
        artifacts.get("security_report")
        or str(
            RESULTS_DIR
            / analysis_id
            / "report"
            / "security_report.json"
        )
    )

    pdf_file = (
        artifacts.get(
            "security_report_pdf"
        )
        or str(
            RESULTS_DIR
            / analysis_id
            / "report"
            / "security_report.pdf"
        )
    )

    report_path = Path(
        report_file
    )

    pdf_path = Path(
        pdf_file
    )

    return {
        "analysis_id": analysis_id,
        "report_id": report.get(
            "report_id"
        ),
        "capture_id": report.get(
            "capture_id"
        ),
        "generated_at": report.get(
            "generated_at"
        ),
        "status": result.get(
            "status",
            report.get(
                "status",
                "UNKNOWN",
            ),
        ),
        "security_score": (
            result.get(
                "security",
                {}
            ).get(
                "security_score"
            )
        ),
        "risk_level": (
            result.get(
                "security",
                {}
            ).get(
                "risk_level"
            )
        ),
        "sha256": integrity.get(
            "report_hash"
        ),
        "blockchain_status": blockchain.get(
            "status"
        ),
        "blockchain_verified": (
            blockchain.get(
                "verified",
                False,
            )
        ),
        "report_exists": (
            report_path.exists()
        ),
        "report_path": str(
            report_path
        ),
        "pdf_exists": (
            pdf_path.exists()
        ),
        "pdf_path": str(
            pdf_path
        ),
    }


@router.get("")
def list_reports():
    """
    Return all completed analysis reports
    stored under backend/results.
    """

    if not RESULTS_DIR.exists():
        return {
            "reports": [],
            "count": 0,
        }

    reports = []

    for analysis_dir in RESULTS_DIR.iterdir():

        if not analysis_dir.is_dir():
            continue

        result = load_final_result(
            analysis_dir
        )

        if not result:
            continue

        if result.get(
            "status"
        ) != "COMPLETED":
            continue

        analysis_id = result.get(
            "analysis_id",
            analysis_dir.name,
        )

        summary = build_report_summary(
            analysis_id,
            result,
        )

        reports.append(
            summary
        )

    reports.sort(
        key=lambda item:
            item.get(
                "generated_at"
            ) or "",
        reverse=True,
    )

    return {
        "reports": reports,
        "count": len(reports),
    }


@router.get("/{analysis_id}")
def get_report(
    analysis_id: str,
):
    """
    Return the complete saved analysis
    result for a report.
    """

    analysis_dir = (
        get_analysis_dir(
            analysis_id
        )
    )

    if not analysis_dir.exists():
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    result = load_final_result(
        analysis_dir
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Saved analysis result not found",
        )

    return result


@router.get("/{analysis_id}/json")
def get_report_json(
    analysis_id: str,
):
    """
    Return the generated security report JSON.
    """

    analysis_dir = (
        get_analysis_dir(
            analysis_id
        )
    )

    report_file = (
        analysis_dir
        / "report"
        / "security_report.json"
    )

    if not report_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Security report JSON not found",
        )

    try:
        with report_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        raise HTTPException(
            status_code=500,
            detail="Unable to read security report",
        )


@router.get("/{analysis_id}/download")
def download_report(
    analysis_id: str,
):
    """
    Download the generated security report JSON.
    """

    analysis_dir = (
        get_analysis_dir(
            analysis_id
        )
    )

    report_file = (
        analysis_dir
        / "report"
        / "security_report.json"
    )

    if not report_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Security report JSON not found",
        )

    return FileResponse(
        path=str(report_file),
        media_type="application/json",
        filename=(
            f"{analysis_id}_security_report.json"
        ),
    )


@router.get("/{analysis_id}/download/pdf")
def download_report_pdf(
    analysis_id: str,
):
    """
    Download the generated PDF security report.
    """

    analysis_dir = (
        get_analysis_dir(
            analysis_id
        )
    )

    pdf_file = (
        analysis_dir
        / "report"
        / "security_report.pdf"
    )

    if not pdf_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Security report PDF not found",
        )

    return FileResponse(
        path=str(pdf_file),
        media_type="application/pdf",
        filename=(
            f"{analysis_id}_security_report.pdf"
        ),
    )
