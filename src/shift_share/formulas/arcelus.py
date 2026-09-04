"""Dynamic Arcelus-style shift-share decomposition.

This is the first implemented formula in the package.

Why this is described cautiously
--------------------------------
The original user script strongly resembles Arcelus' extension of shift-share
analysis because it uses homothetic values and splits national, industry,
regional-growth, and regional-industry terms into expected and differential
components. The script also accumulates annual decompositions over a rolling
window, which makes it dynamic in the broad Barff-Knight sense.

Because the source paper was inferred from the code rather than provided, this
module calls the method ``arcelus_dynamic`` instead of claiming exact textual
fidelity to one paper. Academic use should verify the formulas against the
primary source.

Notation
--------
Let ``e[i, r, t]`` be the observed value for industry ``i`` in region ``r`` at
period ``t``.

Aggregates:
    * ``E_i``: national total for industry i
    * ``E_r``: regional total for region r
    * ``E``: national total across all industries and regions

Homothetic value:
    ``h[i, r, t] = E_i[t] * E_r[t] / E[t]``

This is the value expected in industry-region cell ``(i, r)`` if region ``r``
had the same industry mix as the nation.
"""

from __future__ import annotations

from typing import Dict

import numpy as np

from ..data import ShiftShareData, ShiftShareResult


COMPONENT_LABELS: Dict[str, str] = {
    "ENG": "Expected National Growth Effect",
    "DNG": "Differential National Growth Effect",
    "ENI": "Expected National Industry Mix Effect",
    "DNI": "Differential National Industry Mix Effect",
    "ERG": "Expected Regional Growth Effect",
    "DRG": "Differential Regional Growth Effect",
    "ERI": "Expected Regional Industry Mix Effect",
    "DRI": "Differential Regional Industry Mix Effect",
}


def safe_growth(values: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Compute growth rates along the last axis with zero-denominator safety.

    Classical shift-share is awkward when a sector appears from a zero base.
    Returning zero growth for undefined denominators keeps the program stable,
    but it should be treated as a practical convention, not a theoretical fix.
    """

    growth = np.zeros_like(values, dtype=float)
    current = values[..., 1:]
    previous = values[..., :-1]
    numerator = current - previous

    growth[..., 1:] = np.divide(
        numerator,
        previous,
        out=np.zeros_like(numerator, dtype=float),
        where=np.abs(previous) > eps,
    )
    return growth


def arcelus_dynamic(
    data: ShiftShareData,
    window: int = 5,
    eps: float = 1e-12,
) -> ShiftShareResult:
    """Compute a rolling Arcelus-style shift-share decomposition.

    Parameters
    ----------
    data:
        Industry-region-time dataset.
    window:
        Trailing number of annual / period intervals to accumulate. ``window=1``
        gives a one-period decomposition; ``window=5`` reports a five-interval
        rolling decomposition where possible.
    eps:
        Numerical tolerance used when denominators are zero or close to zero.

    Returns
    -------
    ShiftShareResult
        Eight component arrays, the accounting residual, and diagnostic arrays.

    One-period formula
    ------------------
    For interval ``k-1 -> k``, evaluated on the previous-period base:

    * ``ENG = h * g_n``
    * ``DNG = (e - h) * g_n``
    * ``ENI = h * (g_i - g_n)``
    * ``DNI = (e - h) * (g_i - g_n)``
    * ``ERG = h * (g_r - g_n)``
    * ``DRG = (e - h) * (g_r - g_n)``
    * ``ERI = h * (g_ir - g_r - g_i + g_n)``
    * ``DRI = (e - h) * (g_ir - g_r - g_i + g_n)``

    The expected terms use the homothetic benchmark ``h``. The differential
    terms use ``e - h``, i.e. specialization above or below that benchmark.
    """

    if window < 1:
        raise ValueError("window must be a positive integer")

    e = data.values.astype(float, copy=False)
    n_industries, n_regions, n_periods = e.shape

    # Core totals. These are reused by almost every shift-share variant, so
    # keeping the pattern clear makes the package easier to extend.
    regional_total = e.sum(axis=0)       # shape: (region, period)
    industry_total = e.sum(axis=1)       # shape: (industry, period)
    national_total = e.sum(axis=(0, 1))  # shape: (period,)

    # Growth rates. The last axis is always time.
    g_region = safe_growth(regional_total, eps=eps)   # g_r
    g_industry = safe_growth(industry_total, eps=eps) # g_i
    g_national = safe_growth(national_total, eps=eps) # g_n
    g_cell = safe_growth(e, eps=eps)                  # g_ir

    # Broadcast to industry-region-period arrays. This avoids slow triple loops.
    g_region_full = g_region[np.newaxis, :, :]
    g_industry_full = g_industry[:, np.newaxis, :]
    g_national_full = g_national[np.newaxis, np.newaxis, :]

    # Homothetic value: expected cell size under national industry shares.
    h = np.divide(
        industry_total[:, np.newaxis, :] * regional_total[np.newaxis, :, :],
        national_total[np.newaxis, np.newaxis, :],
        out=np.zeros_like(e, dtype=float),
        where=np.abs(national_total[np.newaxis, np.newaxis, :]) > eps,
    )

    # Location quotient. Useful diagnostic: LQ > 1 means above-benchmark
    # specialization; LQ < 1 means below-benchmark specialization.
    location_quotient = np.divide(
        e,
        h,
        out=np.ones_like(e, dtype=float),
        where=np.abs(h) > eps,
    )

    components = {code: np.zeros_like(e, dtype=float) for code in COMPONENT_LABELS}

    # Rolling accumulation. For ending period t, add all one-period intervals
    # k-1 -> k where k = max(1, t-window+1), ..., t.
    #
    # This corrects the original script's accidental k=0 edge case, which made
    # Python read h[:, :, -1]. It often looked harmless because growth at k=0
    # was zero, but the indexing was still wrong and should not survive in a
    # public package.
    for t in range(1, n_periods):
        first_interval = max(1, t - window + 1)
        for k in range(first_interval, t + 1):
            base = k - 1
            observed_base = e[:, :, base]
            homothetic_base = h[:, :, base]
            specialization_base = observed_base - homothetic_base

            national_growth = g_national_full[:, :, k]
            industry_mix = g_industry_full[:, :, k] - national_growth
            regional_growth = g_region_full[:, :, k] - national_growth
            regional_industry_mix = (
                g_cell[:, :, k]
                - g_region_full[:, :, k]
                - g_industry_full[:, :, k]
                + national_growth
            )

            components["ENG"][:, :, t] += homothetic_base * national_growth
            components["DNG"][:, :, t] += specialization_base * national_growth
            components["ENI"][:, :, t] += homothetic_base * industry_mix
            components["DNI"][:, :, t] += specialization_base * industry_mix
            components["ERG"][:, :, t] += homothetic_base * regional_growth
            components["DRG"][:, :, t] += specialization_base * regional_growth
            components["ERI"][:, :, t] += homothetic_base * regional_industry_mix
            components["DRI"][:, :, t] += specialization_base * regional_industry_mix

    # Accounting check. Compare the sum of components against observed rolling
    # change over the same window.
    actual_rolling_change = np.zeros_like(e, dtype=float)
    for t in range(1, n_periods):
        first_interval = max(1, t - window + 1)
        base_period = first_interval - 1
        actual_rolling_change[:, :, t] = e[:, :, t] - e[:, :, base_period]

    reconstructed_change = sum(components.values())
    residual = actual_rolling_change - reconstructed_change

    diagnostics = {
        "homothetic_value": h,
        "location_quotient": location_quotient,
        "observed_rolling_change": actual_rolling_change,
        "reconstructed_change": reconstructed_change,
    }

    return ShiftShareResult(
        method="arcelus-dynamic",
        components=components,
        residual=residual,
        diagnostics=diagnostics,
        metadata={
            "window": window,
            "eps": eps,
            "component_labels": COMPONENT_LABELS,
            "method_note": (
                "Dynamic / rolling Arcelus-style extension using homothetic "
                "values; inferred from the original script's formula structure."
            ),
        },
    )
