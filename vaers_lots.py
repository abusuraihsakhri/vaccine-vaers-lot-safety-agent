"""Descriptive counts of distinct VAERS report identifiers by vaccine lot.

Input is a VAERSVAX-style CSV. This is not a vaccine adverse-event rate,
a causal analysis, or a statistical safety signal test.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

HEADERS = ("VAERS_ID", "VAX_LOT")
MISSING_LOTS = {"", "UNKNOWN", "UNK", "N/A", "NA", "NONE", "NOT REPORTED"}


def _clean(value: object) -> str:
    return str(value or "").strip()


def count_lot_reports(rows: Iterable[Dict[str, str]]) -> Tuple[List[Dict[str, object]], Dict[str, int]]:
    """Count unique VAERS_ID values per (vaccine type, manufacturer, lot).

    Repeated identical report/lot associations are counted once. One VAERS
    report can contribute to several different vaccine-lot groups.
    """
    groups: Dict[Tuple[str, str, str], set] = defaultdict(set)
    total = skipped = 0
    for row in rows:
        total += 1
        if None in row:
            raise ValueError(f"CSV row {total} contains more columns than its header")
        record = {str(k).strip().upper(): _clean(v) for k, v in row.items()}
        report_id = record.get("VAERS_ID", "")
        lot = record.get("VAX_LOT", "").upper()
        if not report_id or lot in MISSING_LOTS:
            skipped += 1
            continue
        vaccine_type = record.get("VAX_TYPE", "").upper() or "UNKNOWN"
        manufacturer = record.get("VAX_MANU", "").upper() or "UNKNOWN"
        groups[(vaccine_type, manufacturer, lot)].add(report_id)

    result = [
        {"vaccine_type": group[0], "manufacturer": group[1],
         "lot": group[2], "report_count": len(report_ids)}
        for group, report_ids in groups.items()
    ]
    result.sort(key=lambda row: (-row["report_count"], row["vaccine_type"],
                                 row["manufacturer"], row["lot"]))
    return result, {
        "input_rows": total,
        "excluded_rows": skipped,
        "lot_groups": len(result),
        "distinct_lot_report_associations": sum(r["report_count"] for r in result),
    }


def read_vaers_vax(path: str | Path) -> Tuple[List[Dict[str, object]], Dict[str, int]]:
    """Read CSV including quoted fields, embedded commas and UTF-8 BOM."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        names = reader.fieldnames
        if not names:
            raise ValueError("CSV is empty or has no header")
        headers = [name.strip().upper() for name in names]
        if len(set(headers)) != len(headers):
            raise ValueError("CSV contains duplicate column names")
        missing = set(HEADERS).difference(headers)
        if missing:
            raise ValueError("Required CSV columns: VAERS_ID and VAX_LOT")
        return count_lot_reports(reader)


def _safe_cell(value: object) -> str:
    """Prevent CSV formula execution when output is opened in a spreadsheet."""
    s = str(value)
    return "'" + s if s.lstrip().startswith(("=", "+", "-", "@")) or s.startswith(("\t", "\r", "\n")) else s


def write_lot_csv(path: str | Path, rows: Iterable[Dict[str, object]]) -> None:
    fields = ("vaccine_type", "manufacturer", "lot", "report_count")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _safe_cell(row[key]) for key in fields})
