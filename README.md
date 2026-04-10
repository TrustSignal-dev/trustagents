# TrustAgents



[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)



Defensive-security research repository for simulated fraud detection in compliance evidence pipelines. Supports proposal review with synthetic artifacts and explicit limits.



> **R&D boundary:** The `trustagents` oracle service is experimental, optional, non-blocking, and isolated from TrustSignal's production verification chain. Oracle output is advisory and ingestion-ready only.



---



## What This Is



TrustAgents explores anomaly detection and fraud-pattern recognition for compliance evidence using synthetic data and simulated pipelines. It does *not* replace or modify TrustSignal production controls (artifact hashing, signed receipts, receipt verification, scoped auth, webhook integrity, redaction).



### Key Constraints



- All fixtures and examples are **synthetic** unless explicitly documented otherwise

- Oracle fusion, chain anchoring, ZKP attestation, and autonomous research agents are documented as **future work** only

- Current content does not claim production dependency on any of these capabilities



---



## Repository Structure



```

proposal/               Grant-ready summaries, application text, budget, timeline

docs/

├── architecture/       Boundaries, integration architecture, implementation plan

├── integration/        TrustSignal optional handoff documentation

├── schemas/            Oracle API contract, decision schema, confidence model

├── methodology.md      Research methodology

├── problem-statement.md

└── threat-model.md     Threat assumptions

datasets/               Synthetic schema and sample anomalies (JSONL)

simulations/            Scenario catalog and pipeline model

agents/

├── anomaly-detection/  Anomaly detection agent role definition

├── evidence-analysis/  Evidence analysis agent role definition

└── verification/       Verification agent role definition

eval/                   Benchmark design and metrics

examples/               Sample oracle request/response payloads

src/trustagents/        Experimental oracle evaluation service

├── api/                FastAPI routes, error handling

├── adjudication/       Decision adjudication logic

├── auth/               Authentication helpers

├── comparators/        Evidence comparison engine

├── config/             Settings and configuration

├── connectors/         Data connectors (file, HTTP, mock registry)

├── models/             Data models

├── oracle/             Oracle evaluation service

├── pipeline/           Processing pipeline

├── scoring/            Scoring engine

└── storage/            Storage interface

tests/                  Unit, integration, and regression tests

output/pdf/             Generated grant application PDF

scripts/                PDF rendering and utilities

```



---



## Tech Stack



| Layer | Technology |

|---|---|

| Language | Python 3.12+ |

| Framework | FastAPI |

| HTTP Client | httpx |

| Validation | Pydantic v2 |

| Server | Uvicorn |

| Testing | pytest, pytest-cov |



---



## Quick Start



### Prerequisites



- Python 3.12+



### Setup



```bash

# Install dependencies

pip install -e .



# Install test dependencies

pip install -e ".[test]"



# Run tests

pytest



# Start the oracle service (development)

uvicorn src.trustagents.api.app:app --reload

```



---



## Oracle Service



The experimental oracle at `src/trustagents/` evaluates synthetic compliance evidence for anomalies:



1. **Ingest** — Receive evidence artifacts via API

2. **Score** — Apply comparators and scoring engine

3. **Adjudicate** — Produce advisory decision with confidence and risk levels

4. **Respond** — Return structured oracle response



See [docs/schemas/oracle-api-contract.md](docs/schemas/oracle-api-contract.md) for the API contract and [examples/](examples/) for sample payloads.



---



## Grant Proposal



The `proposal/` directory contains grant-ready materials:



- [Project Summary](proposal/project-summary.md)

- [Grant Application](proposal/grant-application.md)

- [Budget and Timeline](proposal/budget-and-timeline.md)

- [Generated PDF](output/pdf/trustagents-grant-application.pdf)



---



## Documentation



| Resource | Path |

|---|---|

| Problem Statement | [docs/problem-statement.md](docs/problem-statement.md) |

| Methodology | [docs/methodology.md](docs/methodology.md) |

| Threat Model | [docs/threat-model.md](docs/threat-model.md) |

| Oracle Architecture | [docs/architecture/oracle-service-architecture.md](docs/architecture/oracle-service-architecture.md) |

| TrustSignal Integration | [docs/integration/trustsignal-optional-handoff.md](docs/integration/trustsignal-optional-handoff.md) |

| R&D Boundary | [docs/architecture/trustagents-rd-boundary.md](docs/architecture/trustagents-rd-boundary.md) |



---



## Related Repositories



| Repository | Purpose |

|---|---|

| [TrustSignal](https://github.com/TrustSignal-dev/TrustSignal) | Core API and verification engine |

| [TrustSignal-Verify-Artifact](https://github.com/TrustSignal-dev/TrustSignal-Verify-Artifact) | GitHub Action for artifact verification |

| [TrustSignal-docs](https://github.com/TrustSignal-dev/TrustSignal-docs) | Public documentation |
