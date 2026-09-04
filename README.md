# shift-share

**An extensible Python package for shift-share analysis.**

`shift-share` provides a reusable framework for decomposing regional and sectoral change using shift-share methods.

The package is designed around a common data model, command-line interface, diagnostics, tests, and formula registry, allowing multiple shift-share decompositions to be implemented within the same framework.

The current release implements a **dynamic / rolling Arcelus-style shift-share decomposition** using homothetic values and expected/differential effects.

## Features

* Dynamic / rolling shift-share decomposition
* Arcelus-style homothetic benchmark
* Eight expected and differential effects
* Configurable rolling windows
* Command-line interface
* Python API
* CSV input and output
* Location quotient diagnostics
* Accounting-identity checks
* Extensible formula registry
* Automated tests
* Original legacy implementation retained for comparison

## Installation

Requires **Python 3.10+**.

Clone the repository:

```bash
git clone https://github.com/miraflor/shift-share.git
cd shift-share
```

Create a virtual environment if desired:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then install the package:

```bash
pip install -e .
```

For development and testing:

```bash
pip install -e ".[dev]"
```

## Quick start

An example dataset is included under:

```text
examples/input/example.csv
```

Run a five-period rolling decomposition:

```bash
shift-share \
    --input-dir examples/input \
    --output-dir examples/output \
    --method arcelus-dynamic \
    --window 5
```

The equivalent module command is:

```bash
python -m shift_share \
    --input-dir examples/input \
    --output-dir examples/output \
    --method arcelus-dynamic \
    --window 5
```

List available methods:

```bash
shift-share --list-methods
```

## Python API

The decomposition can also be run directly from Python:

```python
from shift_share.io import (
    read_wide_csv,
    component_table,
    diagnostics_table,
)
from shift_share.formulas.arcelus import arcelus_dynamic


data = read_wide_csv("examples/input/example.csv")

result = arcelus_dynamic(
    data,
    window=5,
)

components = component_table(data, result)
diagnostics = diagnostics_table(data, result)
```

## Input format

Input data use a wide **industry × region × time** structure.

For example:

```csv
Industry,Region,2019,2020,2021,2022
Agriculture,North,100,105,110,120
Manufacturing,North,200,190,210,230
Services,North,300,330,360,390
Agriculture,South,150,160,170,180
Manufacturing,South,250,260,255,275
Services,South,350,370,400,430
```

The expected format is:

1. first column: industry;
2. second column: region;
3. remaining columns: successive periods.

Blank or non-numeric values are treated as zero, while duplicate industry-region rows are aggregated.

---

## Implemented method

### `arcelus-dynamic`

The current implementation is a rolling shift-share decomposition based on a **homothetic benchmark**.

Let

$$
e_{irt}
$$

denote the observed value for industry \(i\), region \(r\), and period \(t\).

Define

$$
h_{irt}
=
\frac{E_{it}E_{rt}}{E_t},
$$

where:

* \(E_{it}\) is the total for industry \(i\);
* \(E_{rt}\) is the total for region \(r\);
* \(E_t\) is the overall reference-economy total.

The homothetic value \(h_{irt}\) is the value expected in an industry-region cell if the region had the same industrial composition as the reference economy.

The difference

$$
e_{irt}-h_{irt}
$$

therefore represents specialization above or below that benchmark.

### Components

The decomposition produces eight components:

| Code  | Component                                 |
| ----- | ----------------------------------------- |
| `ENG` | Expected National Growth Effect           |
| `DNG` | Differential National Growth Effect       |
| `ENI` | Expected National Industry Mix Effect     |
| `DNI` | Differential National Industry Mix Effect |
| `ERG` | Expected Regional Growth Effect           |
| `DRG` | Differential Regional Growth Effect       |
| `ERI` | Expected Regional Industry Mix Effect     |
| `DRI` | Differential Regional Industry Mix Effect |

The **expected** terms operate on the homothetic benchmark \(h\).

The **differential** terms operate on \(e-h\), capturing the interaction between growth effects and specialization relative to the benchmark.

For a one-period interval, the decomposition can be written schematically as:

$$
ENG = h g_n
$$

$$
DNG = (e-h)g_n
$$

$$
ENI = h(g_i-g_n)
$$

$$
DNI = (e-h)(g_i-g_n)
$$

$$
ERG = h(g_r-g_n)
$$

$$
DRG = (e-h)(g_r-g_n)
$$

$$
ERI
=
h(g_{ir}-g_r-g_i+g_n)
$$

$$
DRI
=
(e-h)(g_{ir}-g_r-g_i+g_n),
$$

where:

* \(g_n\) = reference-economy growth;
* \(g_i\) = industry growth;
* \(g_r\) = regional growth;
* \(g_{ir}\) = industry-region growth.

The eight terms together reconstruct observed change, subject to numerical precision and the treatment of zero-base observations.

## Rolling decomposition

Rather than comparing only two distant endpoints, `arcelus-dynamic` decomposes successive period-to-period changes and accumulates them over a trailing window.

For example:

```text
--window 1
```

produces a one-period decomposition.

```text
--window 5
```

accumulates up to five consecutive period-to-period decompositions.

This allows structural change to be examined dynamically rather than solely through an initial-to-final comparison.

---

## Diagnostics

The package calculates several diagnostic quantities alongside the decomposition.

### Homothetic value

$$
h_{irt}
=
\frac{E_{it}E_{rt}}{E_t}.
$$

This is the industry-region value implied by the reference economy's industrial structure.

### Location quotient

The package also computes

$$
LQ_{irt}
=
\frac{e_{irt}}{h_{irt}}.
$$

Broadly:

* \(LQ > 1\): above-benchmark specialization;
* \(LQ < 1\): below-benchmark specialization;
* \(LQ = 1\): industry share equal to the reference benchmark.

### Accounting residual

Observed change is compared with the sum of the shift-share components:

$$
\text{Residual}
=
\text{Observed Change}
-
\sum_k \text{Component}_k.
$$

A residual near zero indicates that the decomposition reconstructs observed change up to floating-point precision.

This accounting identity is also checked by the package tests.

---

## Output

For every input CSV, the command-line interface generates:

```text
<filename>_arcelus-dynamic_components.csv
<filename>_arcelus-dynamic_diagnostics.csv
```

### Components file

Contains the decomposition by:

* method;
* component;
* industry;
* region;
* period / rolling window.

### Diagnostics file

Contains:

* homothetic value;
* location quotient;
* observed rolling change;
* reconstructed change;
* residual.

---

## Repository structure

```text
shift-share/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
│
├── docs/
│   └── adding_formulas.md
│
├── examples/
│   ├── input/
│   │   └── example.csv
│   ├── output/
│   └── run_example.py
│
├── legacy/
│   └── shiftshare_original.py
│
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
│
└── tests/
    └── test_arcelus_identity.py
```

The GitHub repository and package distribution use the name `shift-share`, while the importable Python module is `shift_share`.

---

## Adding decomposition methods

The package is intended to support multiple shift-share formulations through a common interface.

To add a new method:

1. create a module under `src/shift_share/formulas/`;
2. implement the decomposition and return a `ShiftShareResult`;
3. register the method in `src/shift_share/registry.py`;
4. add an accounting-identity test.

See [`docs/adding_formulas.md`](docs/adding_formulas.md) for the extension pattern.

Potential additions include:

* classical shift-share;
* Esteban-Marquillas;
* static Arcelus decomposition;
* dynamic classical shift-share;
* spatial shift-share;
* other structural and regional growth decompositions.

---

## Origins

`shift-share` grew out of an older standalone implementation of shift-share analysis.

The original script is retained under `legacy/` for transparency. The current package reorganizes the analysis into reusable components with:

* explicit data structures;
* vectorized numerical operations;
* configurable rolling windows;
* reusable input/output routines;
* a command-line interface;
* a formula registry;
* diagnostic outputs;
* automated accounting checks.

The package also corrects a rolling-window indexing edge case in the original implementation.

## Methodological note

The current method is described deliberately as **Arcelus-style**.

Its use of homothetic values and the decomposition of national, industry, regional-growth, and regional-industry effects into expected and differential terms closely resembles the extension developed by Arcelus.

The rolling accumulation over successive intervals is also related to the broader literature on dynamic shift-share analysis.

However, the current implementation was reconstructed from the formula structure of legacy code rather than transcribed directly from a primary publication. Users citing the method in formal academic work should therefore verify the specification against the relevant primary literature.

## Limitations

Shift-share analysis is an **accounting decomposition, not a causal model**.

It describes how observed change can be partitioned under a chosen benchmark, but it does not establish why a region or industry grew.

Results may depend on:

* the reference economy;
* sectoral classification;
* geographic aggregation;
* choice of periods;
* rolling-window length;
* treatment of zero observations.

Growth from an initial value of zero is undefined. The current implementation sets undefined growth rates to zero to preserve numerical stability. Results involving zero-base sectors should therefore be interpreted carefully.

## License

Released under the **MIT License**.

Copyright © 2026 James Matthew Miraflor.
