# Agent Rules

This file defines the rules and standards that the Agent must follow when working on this project.

## 1. Type Checking Compliance
All code must satisfy **BasedPyright** Standard Type Check requirements.

- **Strict Compliance**: Ensure 0 errors in `basedpyright` output for all Python files.
- **Exception**: **Matplotlib** related calls are exempt from strict type checking. Use `# type: ignore` to suppress errors specifically related to `matplotlib` or `plt` calls if they cannot be resolved otherwise.
- **Argparse**: Strictly type `argparse` arguments using `NamedTuple` or similar structures to ensure `parser.parse_args()` returns typed objects, avoiding `Any`.

## 2. Single Responsibility Principle (SRP)
The project structure and file contents must adhere to the Single Responsibility Principle.

- **File Level**: Each file should have a single, well-defined purpose (e.g., data loading, plotting, optimization, script entry point). Avoid "god files" that do everything.
- **Function/Class Level**: Functions and classes should do one thing and do it well. Decouple logic (e.g., physical models) from side effects (e.g., I/O, plotting).
- **Project Structure**: Maintain a clear separation of concerns (e.g., `src/models`, `src/visualization`, `src/scripts`, `src/optimizer`).

## 3. Tooling & Verification
Run the shared tooling locally before submitting changes.

- **Static Analysis**: `uv run basedpyright` and `uv run ruff check .` must finish with zero findings. Fix violations rather than disabling rules unless absolutely necessary.
- **Reproducibility**: Document any new tooling or CLI entry points you add in `README.md` so other contributors know how to verify the change set.

## 4. Data & Output Handling
Protect raw data and respect the canonical directory structure.

- **Read-Only Raw Inputs**: Treat everything under `data/raw/` as immutable. Preprocessed artifacts belong in `data/preprocessed/`, analysis outputs in `data/processed/reports/`.
- **Shared Path Helpers**: Use the constants in `src/utils/paths.py` (`RAW_ADMITTANCE_DIR`, `PROCESSED_REPORTS_DIR`, etc.) instead of hard-coded paths to keep scripts portable.

## 5. Script Authoring Workflow
Utility CLIs must behave consistently.

- **Location & Entry Point**: Place ad-hoc tools in `src/scripts/` and ensure they run via `uv run python -m src.scripts.<module>`.
- **User Guidance**: Implement `--help` descriptions and mention new scripts (usage, options, expected outputs) in `README.md`.

## 6. Schema & Types
Keep schema definitions synchronized with implementation changes.

- **TypedDict Updates**: When adjusting analysis payloads or serialized report formats, update the relevant `TypedDict`/`pydantic` models (e.g., `src/types.py`, `src/preprocess/schema.py`) and describe the new fields in the docs.
- **Breaking Changes**: Call out any output schema changes in PR descriptions so downstream consumers can adjust promptly.
