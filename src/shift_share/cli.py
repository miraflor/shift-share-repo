"""Command-line interface for shift_share."""

from __future__ import annotations

import argparse
from pathlib import Path

from .io import component_table, diagnostics_table, iter_csv_files, read_wide_csv
from .registry import get_formula, list_methods


def process_file(
    input_file: Path,
    output_dir: Path,
    method: str,
    window: int,
    eps: float,
) -> tuple[Path, Path]:
    """Run one registered formula on one input CSV and save output files."""

    data = read_wide_csv(input_file)
    formula = get_formula(method)
    result = formula.function(data, window=window, eps=eps)

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = input_file.stem
    components_file = output_dir / f"{stem}_{method}_components.csv"
    diagnostics_file = output_dir / f"{stem}_{method}_diagnostics.csv"

    component_table(data, result).to_csv(components_file, index=False)
    diagnostics_table(data, result).to_csv(diagnostics_file, index=False)

    return components_file, diagnostics_file


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="shift-share",
        description="Run shift-share decompositions on wide industry-region-time CSV files.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("examples/input"),
        help="Directory containing input CSV files. Default: examples/input",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("examples/output"),
        help="Directory for output CSV files. Default: examples/output",
    )
    parser.add_argument(
        "--method",
        default="arcelus-dynamic",
        choices=sorted(list_methods()),
        help="Shift-share formula to use. Default: arcelus-dynamic",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=5,
        help="Trailing window length for dynamic methods. Default: 5",
    )
    parser.add_argument(
        "--eps",
        type=float,
        default=1e-12,
        help="Tolerance for zero denominators. Default: 1e-12",
    )
    parser.add_argument(
        "--list-methods",
        action="store_true",
        help="List implemented methods and exit.",
    )
    return parser


def main() -> None:
    """Entry point used by ``python -m shift_share`` and the console script."""

    parser = build_parser()
    args = parser.parse_args()

    if args.list_methods:
        for name, description in list_methods().items():
            print(f"{name}: {description}")
        return

    input_files = list(iter_csv_files(args.input_dir))
    if not input_files:
        print(f"No CSV files found in {args.input_dir.resolve()}")
        return

    for input_file in input_files:
        print(f"Processing {input_file} using method={args.method}")
        components_file, diagnostics_file = process_file(
            input_file=input_file,
            output_dir=args.output_dir,
            method=args.method,
            window=args.window,
            eps=args.eps,
        )
        print(f"  components  -> {components_file}")
        print(f"  diagnostics -> {diagnostics_file}")
