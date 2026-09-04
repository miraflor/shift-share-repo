"""A small, expandable Python package for shift-share analysis."""

from .data import ShiftShareData, ShiftShareResult
from .formulas.arcelus import arcelus_dynamic
from .io import component_table, diagnostics_table, read_wide_csv
from .registry import get_formula, list_methods

__all__ = [
    "ShiftShareData",
    "ShiftShareResult",
    "arcelus_dynamic",
    "component_table",
    "diagnostics_table",
    "get_formula",
    "list_methods",
    "read_wide_csv",
]

__version__ = "0.1.0"
