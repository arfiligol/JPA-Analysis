# SQUID JPA Analysis Pipeline

## Project Overview
This project provides an automated analysis pipeline for SQUID JPA (Josephson Parametric Amplifier) simulation data, primarily exported from ANSYS HFSS. The pipeline handles data ingestion, resonance frequency extraction, physical model fitting, and visualization.

## Development Principles
To ensure maintainability, readability, and scalability, all contributions to this project must adhere to the following principles:

1.  **Single Responsibility Principle (SRP)**
    *   Each function or class must have a single, well-defined purpose.
    *   Avoid "god functions" that handle extraction, calculation, and plotting simultaneously.
    *   *Example*: A function that calculates Q-factor should not also be responsible for loading the CSV file.

2.  **Strict Typing**
    *   All functions must use Python type hints for arguments and return values.
    *   Use modern Python 3.12+ syntax (e.g., `list`, `dict`, `tuple`, `|` for unions) instead of `typing` module aliases.
    *   The codebase is checked with `basedpyright` for type safety.

3.  **Standalone Models**
    *   Physical models (e.g., LC resonance formulas) must be implemented as standalone functions or classes.
    *   They should be decoupled from data processing logic to allow independent verification and testing.


## Analysis Workflow
The current analysis flow consists of the following stages:

1.  **Data Ingestion**: Load raw simulation data (e.g., CSV files containing Imaginary Admittance or S11 Phase).
2.  **Extraction**: Identify resonance frequencies from the raw data.
3.  **Fitting**: Fit the extracted resonance frequencies to a physical model (e.g., SQUID LC model) to retrieve circuit parameters ($L_s$, $C_{eff}$).
4.  **Visualization**: Generate plots to visualize the fitting quality and physical parameters.

## Project Structure
(Proposed Structure - Subject to Refactoring)

```
project_root/
├── main.py                 # Entry point for the analysis pipeline
├── README.md               # Project documentation
├── data/                   # Raw/processed HFSS exports (see below)
├── requirements.txt        # Python dependencies
└── src/                    # Source code directory
    ├── extraction/         # Modules for extracting features from raw data
    │   ├── admittance.py   # Extract from Im(Y)
    │   └── phase.py        # Extract from S11 Phase
    ├── models/             # Physical model definitions
    │   └── squid_model.py  # SQUID LC equations
    ├── fitting/            # Fitting algorithms
    │   └── optimizer.py    # Curve fitting logic
    ├── visualization/      # Plotting tools
    │   └── plot_utils.py   # Plotting functions
    └── scripts/            # Ad-hoc/CLI utilities (plot comparison, Q-factor, etc.)
```

## Data Layout

Raw inputs live under `data/raw/`, grouped by source type (measurement, circuit simulation, layout simulation). Measurement datasets are further divided by modality:

- `data/raw/measurement/admittance/`: Imaginary admittance sweeps (`*Admittance_Imaginary*.csv`, etc.).
- `data/raw/measurement/phase/`: S-parameter phase exports (`*S11*.csv`, etc.).
- `data/raw/measurement/flux_dependence/`: Flux-bias VNA sweeps (TXT exports).
- `data/raw/circuit_simulation/` and `data/raw/layout_simulation/`: Reserved for future HFSS/Sonnet pipeline outputs.
- `data/processed/reports/`: Generated analysis artifacts, e.g., `analysis_result.json`.

Use the helper constants in `src/utils/paths.py` (`RAW_LAYOUT_ADMITTANCE_DIR`, `RAW_LAYOUT_PHASE_DIR`, `RAW_MEASUREMENT_FLUX_DEPENDENCE_DIR`, `PROCESSED_REPORTS_DIR`) to reference these folders in code so future refactors do not require hard-coded paths.

## Utility Scripts

Exploratory or comparison helpers live under `src/scripts/`. Run them as modules so they can import the shared pipeline code:

```bash
uv run python -m src.scripts.plot_comparison
uv run python -m src.scripts.q_factor_tool
uv run python -m src.scripts.admittance_zero_crossings
uv run python -m src.scripts.resonance_fit
uv run flux-dependence-plot  # flux dependence heatmaps (Plotly default)
```

`resonance_fit` standardizes the admittance exports, extracts mode crossings, performs the LC/SRF parameter fit, prints the cleaned DataFrame per dataset, and saves comparison plots under `data/processed/reports/resonance_fits/` (`.html` by default, `.png` when `--matplotlib` is used).

`flux-dependence-plot` loads the `data/preprocessed/<component>.json` records (produced via `convert-flux-dependence`) and renders amplitude/phase heatmaps in Plotly (Matplotlib if `--matplotlib` is set). Supply the component ID or JSON path (defaults to `LJPAL6572_B44D1`), choose view(s) with `--view`, adjust phase display via `--phase-unit`/`--wrap-phase`, and add 2D slices with `--slice-frequency` or `--slice-bias` to inspect cross-sections.

### Preprocessing Raw Data
Raw HFSS/measurement exports live under `data/raw/…` but the analysis pipeline consumes **preprocessed** records stored under `data/preprocessed/`. Each record is a JSON serialization of a `ComponentRecord` (see `src/preprocess/schema.py`), which describes a component, the parameter datasets it contains (S/Y/Z parameters, amplitude/phase/real/imaginary), sweep axes (frequency, flux bias, L_jun, …) and the numeric matrices.

1. **Convert HFSS admittance data**
   ```bash
   uv run python -m src.preprocess.convert_hfss_admittance \
       data/raw/admittance/LJPAL658_v1_Im_Y11.csv \
       --component-id LJPAL658_v1
   ```
   This reads the raw CSV, pivots it into frequency × L_jun matrices, wraps them in a `ComponentRecord`, and writes `data/preprocessed/LJPAL658_v1.json`. The output can be inspected with `cat data/preprocessed/LJPAL658_v1.json` or loaded via `ComponentRecord.model_validate_json()`.

   Arguments:
   - `csv`: path to the raw HFSS export.
   - `--component-id`: optional override for the component name (defaults to the filename prefix).
   - `--output`: optional custom destination path; by default the record is saved to `data/preprocessed/<component_id>.json`.

2. **Schema reference**
   Run `python -m src.preprocess.schema` to see a minimal example of the `ComponentRecord` structure (axes definitions, dataset values, metadata), or import the models from `src.preprocess.schema` if you want to programmatically inspect/validate preprocessed files.

3. **Convert flux dependence sweeps**
   ```bash
   uv run python -m src.preprocess.convert_flux_dependence \
       data/raw/measurement/flux_dependence/LJPAL6572_B44D1_FluxDep_-2to2mA_0.1mA_3.8to8.0GHz_-55dBm_201_30_73.392.txt
   ```
   This parses the TXT sweep (bias × frequency amplitude/phase), stores the amplitude and phase matrices as S-parameter datasets (with probe power metadata), and writes `data/preprocessed/LJPAL6572_B44D1.json`. Subsequent `flux-dependence-plot` runs read this JSON instead of re-parsing the TXT.

Once the preprocessed JSON exists, downstream scripts should read from `data/preprocessed/…` rather than the raw CSVs to ensure a consistent schema regardless of data source (circuit simulation, layout simulation, or measurement).

## Feature List

### 1. Resonance Extraction
*   **From Admittance**: Extracts resonance frequency where $Im(Y) = 0$.
*   **From Phase**: Extracts resonance frequency from the peak of Group Delay derived from S11 Phase.

### 2. Model Fitting
*   **SQUID LC Model**: Fits frequency vs. Junction Inductance ($L_{jun}$) data.
    *   Formula: $f = \frac{1}{2\pi\sqrt{(L_{jun}/2 + L_s)C}}$
    *   Parameters: Series Inductance ($L_s$), Effective Capacitance ($C$).

### 3. Visualization
*   **Fitting Results**: Overlays raw simulation data points with the fitted model curve.
*   **Parameter Display**: Shows extracted $L_s$ and $C$ values on the plot.
*   **Interactive Backend**: Every CLI script renders Plotly figures with zoom, export, and drawing tools by default. Pass `--matplotlib` to any script if you need a static Matplotlib snapshot instead. Shared styling utilities live in `src/utils/plotting.py`.

## Usage

### Prerequisites
*   Install [uv](https://github.com/astral-sh/uv):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

### Running the Analysis
1.  **Install Dependencies**:
    ```bash
    uv sync
    ```
2.  **Run the Pipeline**:
    ```bash
    uv run main.py
    ```
    Or, if you want to activate the virtual environment manually:
    ```bash
    source .venv/bin/activate
    python main.py
    ```

### Adding New Dependencies
To add a new package (e.g., `requests`):
```bash
uv add requests
```
