# Eightfold AI - Multi-Source Candidate Data Transformer

A deterministic, rule-based ETL pipeline built in Python 3 that ingests candidate data from varied structured and unstructured sources, normalizes it, resolves conflicts, and projects it into a canonical schema based on a dynamic runtime configuration.

## Architecture
The pipeline is modularized for enterprise scalability:
- `main.py`: CLI entry point and execution orchestrator.
- `pipeline.py`: Ingestion (`Detect`/`Extract`) and the core `Merge` logic.
- `normalize.py`: Data standardization (E.164 phone formatting, Skill aliasing).
- `config_engine.py`: The projection layer that reshapes the canonical schema dynamically.
- `models.py`: Strict type definitions using Python dataclasses.

## Setup & Installation
Ensure you have Python 3.8+ installed.

1. **Clone the repository and create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install requests
   ```

## Execution

Run the pipeline via the command line, passing in your input sources and your desired runtime configuration view:

```bash
python main.py --ats ats_input.json --github github_input.json --config runtime_config.json --output final_profile.json
```

> **Note**: After execution, the resulting projected canonical profile will be saved to `final_profile.json` as the sample output.

## Testing

A standard Python test suite is included to verify graceful degradation, phone normalization, and interval-based date mathematics. To run the tests:

```bash
python -m unittest test_pipeline.py
```

## Features & Edge Cases Handled

- **Graceful Degradation:** The Detect stage intercepts malformed JSON or missing files without crashing the pipeline, allowing the merge engine to build profiles from surviving sources.
- **Dynamic Data Reshaping:** The runtime config allows users to dynamically select fields, remap keys, trigger on-the-fly normalization, and toggle tracking metadata without altering the underlying canonical record.
- **Deterministic Conflict Resolution:** Adheres to a strict authoritative source hierarchy (ATS for history/contact, GitHub for technical skills) to ensure idempotent execution.