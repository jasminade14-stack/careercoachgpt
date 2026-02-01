# CareerCoachGPT

CareerCoachGPT is a locally deployable, Generative AI–based career guidance system designed to support early-stage career orientation in academic environments. The system combines semantic retrieval, multi-agent reasoning, and a dedicated governance layer to provide personalized, transparent, and responsible career recommendations for students.

The project follows a modular, containerized architecture and is orchestrated via an n8n workflow to ensure reproducibility and traceability.

---

## System Overview

The system processes user queries in combination with structured student profile data and produces validated career recommendations. It consists of the following main components:

* **n8n**: Workflow orchestration and deterministic control logic
* **Haystack + Weaviate**: Semantic retrieval over job descriptions, skill learning paths, and ethics guidelines
* **CrewAI**: Multi-agent reasoning (analysis, coaching, ethics)
* **Guardrails**: Governance and validation layer for safety, fairness, and professional conduct
* **Docker Compose**: Local-first deployment and service coordination

---

## Repository Structure

```
careercoachgpt/
├── docker-compose.yml              # Service orchestration
├── careercoach-workflow.json       # n8n production workflow
├── haystack/                       # Semantic retrieval service
│   ├── app.py
│   ├── Dockerfile
│   └── data/                       # JSON-based knowledge base
├── student_support/                # CrewAI multi-agent service
│   ├── app.py
│   ├── agents/                     # Analyst, Coach, Ethics agents
│   └── Dockerfile
├── guardrails/                     # Governance and validation service
│   ├── app/
│   │   ├── app.py
│   │   ├── policy.py
│   │   └── schemas.py
│   ├── Dockerfile
│   └── requirements.txt
├── import_to_weaviate.py            # One-time data import script
├── ingest.py                       # Haystack-based ingestion pipeline
├── schema                          # Weaviate schema definition
└── student_profiles.csv            # Example student profile data
```

---

## Requirements

* Docker
* Docker Compose
* Minimum 8 GB RAM recommended
* Tested on local desktop environments (Windows / Linux / macOS)

No external cloud APIs are required. All services run locally.

---

## Installation

### 1. Clone or Download the Repository

You may either clone the repository using Git or download it as a ZIP archive and extract it locally.

```
git clone <repository-url>
cd careercoachgpt
```

---

### 2. Start the Services

From the project root directory, start all services using Docker Compose:

```
docker compose up -d
```

This will start the following containers:

* n8n
* Haystack API service
* Weaviate vector database
* CrewAI agent service
* Guardrails validation service

---

### 3. Import Initial Data (One-Time Setup)

Before running the system for the first time, the Weaviate database must be initialized.

Option A: Using the REST-based import script

```
python import_to_weaviate.py
```

Option B: Using the Haystack ingestion pipeline

```
python ingest.py
```

This step only needs to be executed once.

---

## n8n Workflow Setup

1. Open n8n in your browser:

[http://localhost:5678](http://localhost:5678)

 
2. Import the workflow file:

- `careercoach-workflow.json`

3. Activate the workflow.

The workflow orchestrates CSV-based profile enrichment, semantic retrieval, multi-agent reasoning, and governance validation.

---

## Example Usage

1. Upload or reference a CSV file containing student profile data.
2. Submit a natural language query via the n8n chat interface (e.g., "Which career paths fit my background?").
3. The system returns:
- Career-oriented coaching advice
- Ranked job role recommendations
- Suggested learning paths
- Governance-validated output

---

## Governance and Responsible AI

CareerCoachGPT integrates a dedicated governance layer to ensure responsible AI usage:

- **Discrimination Prevention**: Detection of biased or discriminatory language
- **Privacy Protection**: Screening for personally identifiable information (PII)
- **Professional Conduct**: Enforcement of appropriate and context-aware responses

All outputs are validated before being returned to the user.

---

## Limitations

- The system is a research and prototype implementation, not a production-ready advisory system
- Data quality and recommendation accuracy depend on the provided datasets
- No automated evaluation metrics are included

---

## License and Usage

This project is intended for academic and educational use only.

```
