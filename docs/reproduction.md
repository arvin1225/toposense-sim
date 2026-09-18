# Reproduction guide

## Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[plot]"
python -m unittest discover -s tests -v
```

## Validate the committed study

```powershell
python scripts/validate_artifact.py --artifact artifacts/confirmatory
```

Full validation checks hashes and schema, then regenerates three family/seed trials and compares decisions, observed windings and certificate margins exactly.

## Rebuild publication and browser artifacts

```powershell
$env:MPLBACKEND="Agg"
python figures/gen_fig_certified_goodput.py
python figures/gen_fig_receiver_evidence.py
python scripts/export_dashboard.py
```

Data figures are written as vector PDF and 300-DPI PNG. Browser JSON contains downsampled exact ideal/received loops, finite observations, gates and aggregate metrics.

## Web instrument

```powershell
cd web
pnpm install --frozen-lockfile
pnpm run build
pnpm run preview
```

Vite uses relative paths for repository-subpath hosting.

## Full confirmation

```powershell
python scripts/run_benchmark.py --out artifacts/confirmatory
```

Expected output is 5,000 rows. A changed algorithm or question should use a new protocol and artifact directory rather than overwrite the published study.
