"""CLI integration and input rejection."""
from cli import main
from agents.models import SystemTaskPayload
from pydantic import ValidationError
import csv
import pytest


def test_lot_cli_roundtrip(tmp_path):
    source = tmp_path / "vax.csv"
    target = tmp_path / "result.csv"
    source.write_text("VAERS_ID,VAX_LOT,VAX_TYPE\n1,AAA,COVID19\n1,AAA,COVID19\n2,AAA,COVID19\n")
    assert main(["lots", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="") as f:
        records = list(csv.DictReader(f))
    assert records[0]["report_count"] == "2"
    assert records[0]["lot"] == "AAA"


def test_missing_lot_columns(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("VAERS_ID,OTHER\n1,AAA\n")
    assert main(["lots", "-i", str(source), "-o", str(tmp_path / "out.csv")]) == 1
    assert not (tmp_path / "out.csv").exists()


@pytest.mark.parametrize("metric", [float("nan"), float("inf"), float("-inf")])
def test_invalid_nonfinite_payload_rejected(metric):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T1", target_identifier="X", primary_metric=metric)
