"""Input and output helpers for shift_share.

The default input format is intentionally humble: a wide CSV with industry in
the first column, region in the second column, and time periods in the remaining
columns. This mirrors the user's original script and is easy to prepare from
Excel, Stata, R, pandas, or a statistical agency table.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd

from .data import ShiftShareData, ShiftShareResult


def read_wide_csv(input_file: str | Path) -> ShiftShareData:
    """Read a wide industry-region-time CSV into :class:`ShiftShareData`.

    Expected format
    ---------------
    The first two columns are treated as labels. Their names do not matter.

    .. code-block:: text

        Industry,Region,2019,2020,2021
        Agriculture,North,100,105,111
        Manufacturing,North,200,190,205
        Agriculture,South,150,160,166

    Practical conventions
    ---------------------
    * Blank or non-numeric cells are treated as zero.
    * Duplicate industry-region rows are summed.
    * Input order of industries and regions is preserved, which keeps outputs
      easier to compare with the source file.
    """

    input_file = Path(input_file)
    df = pd.read_csv(input_file)

    if df.shape[1] < 3:
        raise ValueError(
            f"{input_file} must have at least three columns: "
            "industry, region, and at least one period column."
        )

    industry_col = df.columns[0]
    region_col = df.columns[1]
    period_cols = list(df.columns[2:])

    df[industry_col] = df[industry_col].astype(str)
    df[region_col] = df[region_col].astype(str)

    industries = list(pd.unique(df[industry_col]))
    regions = list(pd.unique(df[region_col]))

    for col in period_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    grouped = df.groupby([industry_col, region_col], as_index=False)[period_cols].sum()

    industry_index = {name: idx for idx, name in enumerate(industries)}
    region_index = {name: idx for idx, name in enumerate(regions)}

    import numpy as np

    values = np.zeros((len(industries), len(regions), len(period_cols)), dtype=float)
    for _, row in grouped.iterrows():
        i = industry_index[row[industry_col]]
        r = region_index[row[region_col]]
        values[i, r, :] = row[period_cols].to_numpy(dtype=float)

    return ShiftShareData(
        industries=industries,
        regions=regions,
        periods=[str(col) for col in period_cols],
        values=values,
    )


def component_table(data: ShiftShareData, result: ShiftShareResult) -> pd.DataFrame:
    """Convert component arrays to a tidy long table.

    The table is deliberately long-form because it is easier to plot, group,
    filter, and join in pandas, R, Stata, DuckDB, or a BI tool.
    """

    component_labels: Dict[str, str] = result.metadata.get("component_labels", {})  # type: ignore[assignment]
    window = int(result.metadata.get("window", 1))

    rows: List[dict] = []
    for code, array in result.components.items():
        label = component_labels.get(code, code)
        for i, industry in enumerate(data.industries):
            for r, region in enumerate(data.regions):
                for t, end_period in enumerate(data.periods):
                    first_interval = max(1, t - window + 1) if t > 0 else 0
                    start_period = data.periods[first_interval - 1] if t > 0 else end_period
                    rows.append(
                        {
                            "method": result.method,
                            "component_code": code,
                            "component": label,
                            "industry": industry,
                            "region": region,
                            "window_start": start_period,
                            "window_end": end_period,
                            "value": array[i, r, t],
                        }
                    )

    return pd.DataFrame(rows)


def diagnostics_table(data: ShiftShareData, result: ShiftShareResult) -> pd.DataFrame:
    """Convert residuals and diagnostic arrays to a tidy long table."""

    window = int(result.metadata.get("window", 1))
    rows: List[dict] = []

    for i, industry in enumerate(data.industries):
        for r, region in enumerate(data.regions):
            for t, end_period in enumerate(data.periods):
                first_interval = max(1, t - window + 1) if t > 0 else 0
                start_period = data.periods[first_interval - 1] if t > 0 else end_period
                row = {
                    "method": result.method,
                    "industry": industry,
                    "region": region,
                    "window_start": start_period,
                    "window_end": end_period,
                    "residual": result.residual[i, r, t],
                }
                for name, array in result.diagnostics.items():
                    # Only include diagnostics that are conformable with the
                    # main industry-region-period shape. Formula modules may
                    # also store lower-dimensional internals, but those are not
                    # written by this generic helper.
                    if array.shape == data.values.shape:
                        row[name] = array[i, r, t]
                rows.append(row)

    return pd.DataFrame(rows)


def iter_csv_files(input_dir: str | Path) -> Iterable[Path]:
    """Yield CSV files from a directory in stable sorted order."""

    return sorted(Path(input_dir).glob("*.csv"))
