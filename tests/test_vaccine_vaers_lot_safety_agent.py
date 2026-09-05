"""
Automated Pytest Test Suite for Vaccine Vaers Lot Safety Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
import os
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    """Test that PHI guard properly redacts sensitive information."""
    text_with_phi = "Patient John Doe, MRN-123456, SSN 123-45-6789"
    redacted = PHIGuard.redact_phi(text_with_phi)
    assert "John Doe" not in redacted
    assert "123-45-6789" not in redacted
    assert "REDACTED_IDENTIFIER" in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_tamper_detection():
    """Test that audit trail detects tampering with HMAC verification."""
    trail = AuditTrail(secret_key="test-key-for-tamper-detection")
    trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "original"})

    # Verify intact trail passes
    assert trail.verify_integrity() is True

    # Tamper with the entry
    trail.logs[0]["payload_hash"] = "tampered_hash"

    # Verify tampered trail fails
    assert trail.verify_integrity() is False


def test_batch_processing_file_not_found():
    """Test that batch processing handles missing input file gracefully."""
    result = main(["batch", "-i", "nonexistent_file.csv"])
    assert result == 1


def test_batch_processing_with_valid_csv():
    """Test batch processing with a valid CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        f.write("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n")
        f.write("TASK-BATCH-01,TARGET-B01,28.4,14.2,True,DISCORDANT\n")
        f.write("TASK-BATCH-02,TARGET-B02,12.0,4.1,False,NOMINAL\n")
        temp_path = f.name

    try:
        result = main(["batch", "-i", temp_path, "-o", "test_batch_output.csv"])
        assert result == 0
        assert os.path.exists("test_batch_output.csv")

        # Verify output content
        import csv
        with open("test_batch_output.csv", 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            # Row 1: critical_flag=True triggers CRITICAL_STAT_PANIC
            assert rows[0]["overall_urgency"] == "CRITICAL_STAT_PANIC"
            # Row 2: nominal values trigger ROUTINE
            assert rows[1]["overall_urgency"] == "ROUTINE"
    finally:
        os.unlink(temp_path)
        if os.path.exists("test_batch_output.csv"):
            os.unlink("test_batch_output.csv")


def test_batch_processing_empty_csv():
    """Test that batch processing handles empty CSV gracefully."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        f.write("")  # Empty file
        temp_path = f.name

    try:
        result = main(["batch", "-i", temp_path])
        assert result == 1
    finally:
        os.unlink(temp_path)
