# Adding another shift-share formula

The repository is named `shift-share` so it can grow into a small package of related formulas.

## 1. Add a formula module

Create a new file under:

```text
src/shift_share/formulas/
```

For example:

```text
src/shift_share/formulas/classic.py
```

Your function should accept a `ShiftShareData` object and return a `ShiftShareResult`.

```python
from shift_share.data import ShiftShareData, ShiftShareResult


def classic(data: ShiftShareData, **kwargs) -> ShiftShareResult:
    ...
```

## 2. Register the formula

Open:

```text
src/shift_share/registry.py
```

Import the formula and add it to `FORMULAS`:

```python
from .formulas.classic import classic

FORMULAS = {
    "classic": FormulaSpec(
        name="classic",
        function=classic,
        description="Classical national-share / industry-mix / regional-shift decomposition.",
    ),
    ...
}
```

## 3. Run it from the CLI

```bash
shift-share --method classic --input-dir examples/input --output-dir examples/output
```

## Suggested future methods

Good next formulas to implement:

1. Classical shift-share: national growth, industry mix, regional competitive effect.
2. Esteban-Marquillas shift-share: adds homothetic employment and allocation effect.
3. Arcelus extension: already implemented here as a rolling version.
4. Dynamic shift-share: explicit first-to-last versus chained annual versions.
5. Spatial shift-share: regional effects weighted by neighboring regions.

Keep one formula per module. That will stop the repository from becoming one heroic script with a cape and no tests.
