# Vaccine VAERS Lot Safety Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Vaccine VAERS Lot Safety Agent is an enterprise-grade analytical engine for evaluating vaccine lot safety metrics. It processes task payloads through specialized worker agents that assess primary parameters, safety boundaries, and protocol conformance, producing cryptographically signed consensus dossiers with HMAC-SHA256 audit trails.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Multi-Worker Architecture**: Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) provide comprehensive evaluation.

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/vaccine-vaers-lot-safety-agent.git
cd vaccine-vaers-lot-safety-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. System Configuration Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier (default: TASK-2026-001)
- `--target`: Target entity identifier (default: KEY-TARGET-01)
- `--primary`: Primary measurement value (float, default: 28.5)
- `--secondary`: Secondary metric value (float, default: 14.2)
- `--critical`: Flag for emergency escalation (boolean)
- `--status`: Status descriptor (default: DISCORDANT)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task/case identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary metric value | Optional (default: 0.0) |
| `is_critical_flag` | Emergency escalation flag | Optional (default: false) |
| `status_descriptor` | Status code descriptor | Optional (default: NOMINAL) |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation with full integrity verification.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable for persistent audit integrity across restarts:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY="your-secure-random-key"

# Windows
set AUDIT_SECRET_KEY=your-secure-random-key

# Docker Compose
AUDIT_SECRET_KEY=your-secure-random-key docker-compose up
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
# Build and run with Docker
docker build -t vaccine-vaers-lot-safety-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-key vaccine-vaers-lot-safety-agent

# Or use Docker Compose
AUDIT_SECRET_KEY=your-key docker-compose up
```

---

## 📁 Project Structure

```
vaccine-vaers-lot-safety-agent/
├── agents/                      # Core agent modules
│   ├── __init__.py             # Package initialization
│   ├── api.py                  # FastAPI REST server
│   ├── base.py                 # Security, PHI guard, audit trail
│   ├── learning.py             # Bayesian calibration engine
│   ├── llm_factory.py          # LLM provider factory
│   ├── metrics.py              # Prometheus metrics exporter
│   ├── models.py               # Pydantic data models
│   ├── streamer.py             # WebSocket telemetry streamer
│   ├── supervisor.py           # Supervisor orchestrator
│   └── workers.py              # Specialized worker agents
├── tests/                      # Test suite
│   ├── test_vaccine_vaers_lot_safety_agent.py
│   ├── test_vaccine_lot_safety.py
│   └── test_enrichment.py
├── vaccine_lot_safety/          # Alternative implementation package
├── web/                        # Web operations console
├── cli.py                      # Main CLI entry point
├── simulator.py                # High-throughput simulation
├── enrichment.py               # Enrichment feature modules
├── sample.csv                  # Sample batch input
├── sample_payload.json         # Sample API payload
├── benchmark_dataset.json      # Benchmark test cases
├── pyproject.toml              # Project configuration
├── Dockerfile                  # Container build
├── docker-compose.yml          # Container orchestration
└── .github/workflows/ci.yml    # CI/CD pipeline
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
