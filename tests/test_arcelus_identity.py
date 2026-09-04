import numpy as np

from shift_share.formulas.arcelus import arcelus_dynamic
from shift_share.data import ShiftShareData


def test_arcelus_components_reconstruct_change_without_zero_bases():
    data = ShiftShareData(
        industries=["A", "B"],
        regions=["North", "South"],
        periods=["2020", "2021", "2022"],
        values=np.array(
            [
                [[100, 110, 121], [120, 132, 145]],
                [[200, 210, 230], [180, 190, 205]],
            ],
            dtype=float,
        ),
    )

    result = arcelus_dynamic(data, window=2)

    # For positive bases, the decomposition is an accounting identity up to
    # floating-point noise.
    assert np.nanmax(np.abs(result.residual)) < 1e-9
