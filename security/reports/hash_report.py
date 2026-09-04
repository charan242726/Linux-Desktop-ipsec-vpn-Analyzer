import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python3 hash_report.py "
            "<report_file> <output_file>"
        )
        sys.exit(1)

    report_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    report_hash = calculate_sha256(report_file)

    result = {
        "report_id": "",
        "capture_id": "",
        "report_hash": report_hash,
        "hash_algorithm": "SHA-256",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "HASH_GENERATED"
    }

    # Read report metadata
    with open(report_file, "r") as f:
        report = json.load(f)

    result["report_id"] = report.get(
        "report_id",
        "UNKNOWN"
    )

    result["capture_id"] = report.get(
        "capture_id",
        "UNKNOWN"
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_file, "w") as f:
        json.dump(
            result,
            f,
            indent=2
        )

    print("Report hash generated.")
    print(f"Report : {report_file}")
    print(f"SHA256 : {report_hash}")
    print(f"Output : {output_file}")


if __name__ == "__main__":
    main()
