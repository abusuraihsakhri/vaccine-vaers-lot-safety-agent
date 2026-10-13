"""Regression tests for descriptive VAERSVAX lot counting."""
import csv
from pathlib import Path
import pytest
from vaers_lots import count_lot_reports, read_vaers_vax, write_lot_csv


def test_unique_associations_and_lot_separation():
    rows = [
        {"VAERS_ID": "0001", "VAX_TYPE": "COVID19", "VAX_MANU": "Maker A", "VAX_LOT": " ab1 "},
        {"VAERS_ID": "0001", "VAX_TYPE": "COVID19", "VAX_MANU": "Maker A", "VAX_LOT": "AB1"},
        {"VAERS_ID": "0002", "VAX_TYPE": "COVID19", "VAX_MANU": "Maker A", "VAX_LOT": "ab1"},
        {"VAERS_ID": "0001", "VAX_TYPE": "FLU", "VAX_MANU": "Maker B", "VAX_LOT": "AB1"},
        {"VAERS_ID": "0003", "VAX_TYPE": "FLU", "VAX_MANU": "Maker B", "VAX_LOT": "UNKNOWN"},
        {"VAERS_ID": "", "VAX_TYPE": "FLU", "VAX_MANU": "Maker B", "VAX_LOT": "AB1"},
    ]
    out, stats = count_lot_reports(rows)
    assert [r["report_count"] for r in out] == [2, 1]
    assert stats == {"input_rows": 6, "excluded_rows": 2,
                     "lot_groups": 2, "distinct_lot_report_associations": 3}


def test_bom_quoted_fields_and_export_formula_guard(tmp_path):
    infile = tmp_path / "data.csv"
    infile.write_text("\ufeffVAERS_ID,VAX_LOT,VAX_TYPE,VAX_MANU\n1,\"A,1\",CVX,\"Company, Inc\"\n"
                      "2,\"=2+2\",CVX,Company\n", encoding="utf-8")
    rows, stats = read_vaers_vax(infile)
    assert stats["lot_groups"] == 2
    assert any(r["lot"] == "A,1" for r in rows)
    output = tmp_path / "out.csv"
    write_lot_csv(output, rows)
    with output.open(newline="") as f:
        exported = list(csv.DictReader(f))
    assert any(r["lot"] == "'=2+2" for r in exported)


@pytest.mark.parametrize("value", ["", "VAERS_ID,OTHER\n1,z\n",
                                    "VAERS_ID,VAERS_ID,VAX_LOT\na,b,c\n",
                                    "VAERS_ID,VAX_LOT\n1,a,extra\n"])
def test_bad_csv_rejected(tmp_path, value):
    path = tmp_path / "bad.csv"
    path.write_text(value)
    with pytest.raises(ValueError):
        read_vaers_vax(path)
