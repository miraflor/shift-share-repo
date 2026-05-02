"""Core data containers for the shift_share package.

The package uses a simple convention throughout:

    values[i, r, t] = value for industry i, region r, period t

This 3-D array representation is not the only possible layout, but it is a
clean base for a package of shift-share formulas because most variants reuse
the same industry, region, and time aggregations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np


@dataclass(frozen=True)
class ShiftShareData:
    """Industry-region-time data used by all shift-share formulas.

    Attributes
    ----------
    industries:
        Ordered industry labels from the input data.
    regions:
        Ordered region labels from the input data.
    periods:
        Ordered period labels from the input data. These can be years, months,
        quarters, or any sortable / human-readable period labels.
    values:
        Numeric array with shape ``(n_industries, n_regions, n_periods)``.
    """

    industries: List[str]
    regions: List[str]
    periods: List[str]
    values: np.ndarray

    def __post_init__(self) -> None:
        """Fail early if labels and array dimensions disagree."""

        expected_shape = (len(self.industries), len(self.regions), len(self.periods))
        if self.values.shape != expected_shape:
            raise ValueError(
                f"values has shape {self.values.shape}, but labels imply {expected_shape}."
            )


@dataclass(frozen=True)
class ShiftShareResult:
    """Result returned by a shift-share formula.

    Attributes
    ----------
    method:
        Short method name, e.g. ``"arcelus-dynamic"``.
    components:
        Mapping from component code to component array. Each array should have
        the same shape as the input values.
    residual:
        Difference between observed change and reconstructed change from the
        components. A small residual is a useful accounting check.
    diagnostics:
        Extra arrays such as location quotients, expected values, or growth
        rates. Formula modules can add whatever diagnostics are useful.
    metadata:
        Lightweight method settings, such as the rolling window used.
    """

    method: str
    components: Dict[str, np.ndarray]
    residual: np.ndarray
    diagnostics: Dict[str, np.ndarray] = field(default_factory=dict)
    metadata: Dict[str, object] = field(default_factory=dict)
