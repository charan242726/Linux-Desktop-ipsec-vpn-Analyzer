import pytest
from backend.database.db import init_db, create_session, save_findings, finalize_session, get_all_reports, get_report_by_id, get_conn

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_sqlite_consistency_and_wal():
    # 1. Verify WAL mode
    with get_conn() as conn:
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert journal_mode.lower() == "wal"
        
    # 2. Session creation and isolation
    session_a = create_session()
    session_b = create_session()
    
    assert session_a != session_b
    
    # 3. Add findings
    save_findings(session_a, {"risk_level": "LOW", "ike": {"version": "IKEv2"}})
    save_findings(session_b, {"risk_level": "HIGH", "ike": {"version": "IKEv1"}})
    
    finalize_session(session_a)
    finalize_session(session_b)
    
    # 4. Verify retrieval matches correct session
    report_a = get_report_by_id(session_a)
    report_b = get_report_by_id(session_b)
    
    assert report_a["risk_level"] == "LOW"
    assert len(report_a["findings"]) == 1
    assert report_a["findings"][0]["ike"]["version"] == "IKEv2"
    
    assert report_b["risk_level"] == "HIGH"
    assert len(report_b["findings"]) == 1
    assert report_b["findings"][0]["ike"]["version"] == "IKEv1"
