# Vaccine VAERS Lot Safety Agent

Local, descriptive exploration of **VAERS vaccine-lot report associations**. Upload an official VAERSVAX CSV in the browser or use the Python CLI to summarize the number of distinct reported `VAERS_ID` values per vaccine type, manufacturer, and normalized lot identifier.

> **Interpretation:** These are counts of reported events following vaccination, **not** adverse-event incidence rates, adjusted risks, causal estimates, or validated safety signals. VAERS is a passive surveillance system with reporting bias and incomplete information. The tool has no administered-dose denominators, statistical scan procedure, or controlled comparisons. Never infer that a vaccine lot is unsafe from these counts alone. See the [official VAERS Data Guide](https://vaers.hhs.gov/data/dataguide.html).

## Browser explorer

Open `web/index.html` in a modern browser, or use the repository's configured GitHub Pages deployment once active.

1. Download VAERS public files from [vaers.hhs.gov/data.html](https://vaers.hhs.gov/data.html).
2. Select the **VAERSVAX** vaccine table CSV (e.g. `2025VAERSVAX.csv`), not VAERSDATA or VAERSSYMPTOMS.
3. Review unique report-lot counts, filter results, and export the summary CSV. Use **Load synthetic example** to test without real data.

Required columns: `VAERS_ID` and `VAX_LOT`. Optional grouping columns: `VAX_TYPE` and `VAX_MANU` (missing values are grouped as `UNKNOWN`). Lot strings are trimmed and uppercased; unreported or unknown lot values and missing report IDs are excluded. Exact duplicate report IDs in the *same* group are counted once; an ID may appear in multiple groups. This deduplication does not resolve secondary reports with different IDs or validate lot identifiers. No background rate, hypothesis test, or safety ranking is generated.

**Privacy:** The browser reads the selected file locally; CSV records are not sent to a server, third party, or browser storage. It displays and exports aggregate counts only. Public VAERS data may still contain sensitive free text—avoid uploading private patient files. CSV exports escape spreadsheet formulas. Browser uploads are limited to 20 MB; use the Python CLI for larger inputs.

## Python CLI

Requires Python 3.10 or later.

```bash
python -m pip install -e ".[api,dev]"
python cli.py lots -i sample_vaersvax.csv -o lot_report_counts.csv
python cli.py lots -i /path/to/2025VAERSVAX.csv -o lot_report_counts.csv
```

The output includes `vaccine_type`, `manufacturer`, `lot`, and `report_count`. The CSV source is read locally. There is no outbound API access.

The pre-existing **illustrative**, rule-based task evaluator remains available:

```bash
python cli.py audit --task-id DEMO-01 --target LOT-01 --primary 28.5 --secondary 14.2 --critical
python cli.py batch -i sample.csv -o results.csv
python cli.py chat "What is the system status?"
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The `audit`, `batch`, and `/api/audit` paths evaluate generic supplied metrics against fixed illustrative thresholds; they do **not** import VAERS data or implement validated CDC/FDA methods, spatial-temporal Poisson scans, or clinical decision support. Mock chat is deterministic placeholder output, not scientific verification.

## REST API and Docker

Install the `api` extra and start the REST API as above. Local API: `http://127.0.0.1:8000/docs`. Available endpoints include `/health`, `/metrics` (JSON counters), `/api/audit`, `/api/chat`, and `/api/audit/logs`. The in-memory HMAC audit chain provides tamper detection within a process but is not persistent unless externally archived; `AUDIT_SECRET_KEY` selects a stable signing key. The regex-based identifier filter does **not** guarantee comprehensive PHI removal or HIPAA compliance. Do not submit patient-identifiable data to this demonstration API.

```bash
docker compose up --build
```

Docker Compose binds to `127.0.0.1:8000` by default, not a public interface. To bind another address, set `BIND_ADDRESS` explicitly. Do not expose the unauthenticated API publicly without adding authentication, access controls, TLS, and storage/retention safeguards.

## Development and tests

```bash
python -m pip install -e ".[api,dev]"
python -m pytest -q
node --test tests/test_web_lots.cjs
node --check web/app.js
node --check web/lot_analysis.js
```

CI tests Python 3.10–3.13 and the browser CSV module; a separate GitHub Pages workflow publishes the static `web/` directory on `master`. The browser implementation uses plain JavaScript rather than Pyodide: no Python runtime or server is required for the CSV workflow. Tested browser engine syntax with Node; full cross-browser compatibility should be confirmed for target environments.

## License

MIT — see [LICENSE](LICENSE).
