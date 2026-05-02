"""Minimal Python API example.

Run from the repository root with:

    python examples/run_example.py
"""

from pathlib import Path

from shift_share.formulas.arcelus import arcelus_dynamic
from shift_share.io import component_table, diagnostics_table, read_wide_csv


data = read_wide_csv(Path("examples/input/example.csv"))
result = arcelus_dynamic(data, window=3)

components = component_table(data, result)
diagnostics = diagnostics_table(data, result)

print(components.head())
print(diagnostics.head())
