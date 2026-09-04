# shift-share

`shift-share` is an expandable Python package for shift-share decompositions.

The first implemented method is a **dynamic / rolling Arcelus-style shift-share decomposition** adapted from an older script. The repository name is intentionally general so more formulas can be added later: classical shift-share, Esteban-Marquillas, Arcelus, dynamic variants, and spatial variants.

## Why this repository is structured as a package

Instead of one script, the code is organized as a small package:

```text
shift-share/
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── docs/
│   └── adding_formulas.md
├── examples/
│   ├── input/
│   │   └── example.csv
│   ├── output/
│   │   └── .gitkeep
│   └── run_example.py
├── legacy/
│   └── shiftshare_original.py
├── src/
│   └── shift_share/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── data.py
│       ├── io.py
│       ├── registry.py
│       └── formulas/
│           ├── __init__.py
│           └── arcelus.py
└── tests/
    └── test_arcelus_identity.py
```

The GitHub repository can be named `shift-share`; the importable Python module is named `shift_share`, because Python packages cannot use hyphens in import statements.

## Implemented method

### `arcelus-dynamic`

This method computes eight components:

| Code | Component |
|---|---|
| ENG | Expected National Growth Effect |
| DNG | Differential National Growth Effect |
| ENI | Expected National Industry Mix Effect |
| DNI | Differential National Industry Mix Effect |
| ERG | Expected Regional Growth Effect |
| DRG | Differential Regional Growth Effect |
| ERI | Expected Regional Industry Mix Effect |
| DRI | Differential Regional Industry Mix Effect |

The structure appears closest to **Arcelus (1984), “An Extension of Shift-Share Analysis”**, because it uses homothetic values and splits effects into expected and differential terms. The rolling-window accumulation is also close in spirit to **dynamic shift-share analysis** associated with Barff and Knight.

Cautious description:

> This package currently implements a rolling Arcelus-style shift-share decomposition using homothetic values. The formula source was inferred from the legacy code structure and should be checked against the primary paper before formal citation.

## Input format

Put CSV files in `examples/input/` or another folder of your choice.

Expected wide format:

```csv
Industry,Region,2019,2020,2021,2022
Agriculture,North,100,105,110,120
Manufacturing,North,200,190,210,230
Services,North,300,330,360,390
Agriculture,South,150,160,170,180
Manufacturing,South,250,260,255,275
Services,South,350,370,400,430
```

Rules:

1. First column = industry.
2. Second column = region.
3. Remaining columns = periods.
4. Blank or non-numeric cells are treated as zero.
5. Duplicate industry-region rows are summed.

## Install

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -e .
```

For development and tests:

```bash
pip install -e ".[dev]"
```

## Run from the command line

```bash
shift-share --input-dir examples/input --output-dir examples/output --method arcelus-dynamic --window 5
```

Equivalent:

```bash
python -m shift_share --input-dir examples/input --output-dir examples/output --method arcelus-dynamic --window 5
```

List available methods:

```bash
shift-share --list-methods
```

## Run from Python

```python
from shift_share.io import read_wide_csv, component_table, diagnostics_table
from shift_share.formulas.arcelus import arcelus_dynamic


data = read_wide_csv("examples/input/example.csv")
result = arcelus_dynamic(data, window=5)

components = component_table(data, result)
diagnostics = diagnostics_table(data, result)
```

## Output files

For each input CSV, the CLI writes:

```text
<filename>_arcelus-dynamic_components.csv
<filename>_arcelus-dynamic_diagnostics.csv
```

The components file is long-form and contains one row per method, component, industry, region, and rolling window.

The diagnostics file contains:

- residual;
- homothetic value;
- location quotient;
- observed rolling change;
- reconstructed change.

A near-zero residual means the components reconstruct observed change up to floating-point error. Large residuals often indicate zero-base growth or data issues.

## Adding more formulas

See [`docs/adding_formulas.md`](docs/adding_formulas.md).

The intended pattern is:

1. create a new module under `src/shift_share/formulas/`;
2. return a `ShiftShareResult`;
3. register the formula in `src/shift_share/registry.py`;
4. add a test that checks the accounting identity.

Good next additions:

- `classic`: national share, industry mix, regional shift;
- `esteban-marquillas`: homothetic-employment allocation effect;
- `arcelus-static`: non-rolling version of the current method;
- `dynamic-classic`: chained annual classic shift-share;
- `spatial`: regional effects based on neighboring regions.

## What was improved from the legacy script

- Converted one script into an expandable package layout.
- Added a formula registry so new methods can be plugged into the same CLI.
- Added dataclasses for input data and results.
- Added comprehensive comments explaining the decomposition.
- Fixed the rolling-window off-by-one issue in the original loop.
- Added command-line arguments.
- Added sample data, diagnostics output, and a basic test.
- Preserved the original script under `legacy/`.

## Limitations

Shift-share is an accounting decomposition, not a causal model. It is useful for organizing growth into interpretable components, but it does not prove why a region or industry grew.

Zero-base growth remains delicate. This implementation suppresses infinite growth rates by setting undefined growth to zero. That keeps the package usable but should be documented when analyzing sectors that appear from zero.
