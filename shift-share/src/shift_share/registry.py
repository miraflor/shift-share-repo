"""Formula registry for shift_share.

A registry keeps the package expandable. New formulas can live in separate
modules and be registered under short method names without rewriting the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from .data import ShiftShareData, ShiftShareResult
from .formulas.arcelus import arcelus_dynamic

FormulaFunction = Callable[..., ShiftShareResult]


@dataclass(frozen=True)
class FormulaSpec:
    """Description of an implemented shift-share formula."""

    name: str
    function: FormulaFunction
    description: str


FORMULAS: Dict[str, FormulaSpec] = {
    "arcelus-dynamic": FormulaSpec(
        name="arcelus-dynamic",
        function=arcelus_dynamic,
        description=(
            "Rolling Arcelus-style extension with expected and differential "
            "national, industry, regional-growth, and regional-industry effects."
        ),
    ),
}


def get_formula(name: str) -> FormulaSpec:
    """Return a registered formula by name."""

    try:
        return FORMULAS[name]
    except KeyError as exc:
        available = ", ".join(sorted(FORMULAS))
        raise ValueError(f"Unknown method '{name}'. Available methods: {available}") from exc


def list_methods() -> Dict[str, str]:
    """Return method descriptions for display in the CLI or documentation."""

    return {name: spec.description for name, spec in FORMULAS.items()}
