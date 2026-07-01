# Eightfold AI - Multi-Source Candidate Data Transformer

**Candidate:** Venumadhav S.  
**Role:** Engineering Intern (Jul-Dec 2026)  

## Overview
This repository contains a deterministic, rule-based ETL pipeline built in Python 3. It ingests candidate data from varied structured and unstructured sources, normalizes formats, resolves conflicts deterministically, and projects the data into a canonical schema based on a dynamic runtime configuration.

## Architecture
The pipeline was refactored from a monolithic script into a modular, production-ready architecture:
- `main.py`: CLI entry point and execution orchestrator. Includes the final validation stage.
- `pipeline.py`: Ingestion (`Detect`/`Extract`) and the core `Merge` logic, including interval date math and confidence weighting.
- `normalize.py`: Data standardization (E.164 phone formatting, Skill canonical aliasing).
- `config_engine.py`: The projection layer that reshapes the canonical schema dynamically.
- `models.py`: Strict type definitions and validation using Python dataclasses.
- `test_pipeline.py`: A Python `unittest` suite verifying edge cases and pipeline stability.

## Setup & Installation
Ensure you have Python 3.8+ installed.

1. **Clone the repository and create a virtual environment:**
   ```bash
   git clone https://github.com/CodingGeekVenu/Eightfold-Assignment.git
   cd eightfold-data-transformer
   python -m venv venv
   ```

2. **Activate the environment:**
- On Mac/Linux: `source venv/bin/activate`
- On Windows: `venv\Scripts\activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Execution (Exact Run Steps)

Run the pipeline via the command line, passing in your input sources and your desired runtime configuration view.

```bash
python main.py --ats ats_input.json --github github_input.json --config runtime_config.json
```

**Produced Output:** Upon successful execution, the pipeline will generate a `final_profile.json` file in the root directory containing the projected canonical profile.

## Testing

The pipeline includes a programmatic test suite covering edge cases (e.g., graceful degradation on malformed inputs, interval date math, and array index safety).

To run the tests:

```bash
python -m unittest test_pipeline.py
```

## Key Features & Design Decisions

* **Graceful Degradation (Detect Stage):** The pipeline intercepts empty files, `JSONDecodeError`s, and missing top-level keys before extraction, skipping the offending source gracefully without crashing the runtime.
* **Interval Date Math:** `years_experience` is calculated by converting all job histories into date intervals, sorting them chronologically, and merging overlaps to mathematically prevent duplicate experience counting. Invalid chronological dates (end < start) are clamped.
* **Dynamic Configuration (The Twist):** The projection layer allows downstream consumers to dynamically select fields, remap keys, trigger on-the-fly normalization, and toggle tracking metadata (Confidence/Provenance) without altering the underlying canonical record.
* **Missing Value Handling:** Honors the `on_missing` config flag by dynamically injecting `null`, gracefully omitting the key entirely, or throwing an explicit error.

## Assumptions & Descoped Items

* **Assumed Identity Matching:** Candidates are matched using an exact Email match, followed by Full Name.
* **Tradeoff - No Shared Keys:** If sources share no emails or matching names, the system conservatively treats them as separate candidates to prioritize high-confidence determinism over recall.
* **Descoped - NLP / Fuzzy Matching:** NLP entity extraction from raw prose (e.g., recruiter free-text notes) and fuzzy string matching (e.g., Levenshtein distance for companies) were deliberately omitted to preserve strictly deterministic explainability under the assessment's time constraints.
