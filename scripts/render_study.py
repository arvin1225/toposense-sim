"""Build the standalone numerical-study page from recorded output."""
from pathlib import Path
from html import escape
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "artifacts/bounded-loop-study/summary.json"
data = json.loads(source.read_text(encoding="utf-8"))
data_rows = [[family.replace("_", " "), method.replace("_", " "), values["releases"], values["wrong_releases"], f'{100*values["coverage"]:.0f}%'] for family, methods in data["by_family"].items() for method, values in methods.items()]
headers = ["Loop family", "Method", "Released", "Wrong", "Coverage"]
lead = "The bounded method released 240 of 600 inputs without a wrong release. It rejected every near-origin, high-frequency and missing-sector input."
explanation = "On each interval, the observed segment must stay farther from the origin than max(endpoint errors) + L × angular gap / 2. The resulting homotopy preserves the received-loop winding under the supplied assumptions."
limitation = "The global derivative bound L must be justified independently. Adjacent sample slopes cannot supply it. Noise is bounded by construction here; these are not H1/H2 photon-noise or physical-receiver results."
command = "python scripts/run_bound_study.py"
result = "40% release coverage"
method = "Measured complex samples → error discs → global derivative bound → origin exclusion"
output = ROOT / "web/public"
output.mkdir(parents=True, exist_ok=True)
downloads = output / "study-data"
downloads.mkdir(exist_ok=True)
shutil.copyfile(source, downloads / "summary.json")
shutil.copyfile(ROOT / "artifacts/bounded-loop-study/trials.csv", downloads / "trials.csv")
table = "<thead><tr>" + "".join("<th>" + escape(str(x)) + "</th>" for x in headers) + "</tr></thead><tbody>"
for row in data_rows:
    table += "<tr>" + "".join("<td>" + escape(str(x)) + "</td>" for x in row) + "</tr>"
table += "</tbody>"
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>When a winding is determined · toposense-sim</title>
<style>
:root{{color-scheme:dark;--accent:#91d4cb}}*{{box-sizing:border-box}}
body{{margin:0;background:#08281f;color:#e2ece5;font:16px/1.65 "Segoe UI Variable Text","Aptos",system-ui,sans-serif}}
main{{max-width:1120px;margin:auto;padding:36px 30px 80px}}
nav{{display:flex;justify-content:space-between;gap:24px;border-bottom:1px solid #416356;padding-bottom:20px}}
a{{color:var(--accent);text-underline-offset:5px}}nav a{{text-decoration:none}}.tag{{color:#a0b9ac;font-size:13px}}
header{{padding:62px 0 30px;max-width:840px}}h1{{font:500 clamp(36px,5vw,62px)/1.06 "Segoe UI Variable Display","Aptos Display",system-ui;letter-spacing:-.045em;margin:16px 0 22px}}
header p{{font-size:22px;color:#b6cbbf}}.result{{border-left:3px solid var(--accent);padding:5px 0 5px 24px;margin:22px 0 34px}}
.result strong{{font-size:30px;font-weight:500;color:var(--accent)}}.result p{{max-width:780px;margin:10px 0}}
section{{border-top:1px solid #416356;padding:24px 0}}h2{{font-size:20px;font-weight:500}}
.formula{{padding:18px;background:#12392c;border-radius:6px;font:14px/1.6 Consolas,monospace;color:var(--accent)}}
.table-scroll{{overflow:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}th{{text-align:left;color:#a7c0b2;font-weight:500}}
td,th{{padding:13px 14px;border-bottom:1px solid #2c4e40}}td:not(:first-child){{font-variant-numeric:tabular-nums}}
tr:hover td{{background:#143b2c}}.note{{color:#abc3b5;max-width:800px}}code{{word-break:break-all}}.downloads{{display:flex;gap:24px;flex-wrap:wrap}}
details{{color:#96ad9f;font-size:13px;margin-top:30px}}summary{{cursor:pointer}}@media(max-width:600px){{main{{padding:22px 18px}}header{{padding-top:36px}}}}
</style></head><body><main>
<nav><a href="./">← toposense-sim</a><span class="tag">Analytic-loop stress study</span></nav>
<header><span class="tag">NUMERICAL STUDY / SEPTEMBER 2026</span><h1>When a winding is determined</h1><p>A bound on every unsampled interval.</p></header>
<div class="result"><strong>{escape(result)}</strong><p>{escape(lead)}</p></div>
<section><h2>Method</h2><p>{escape(explanation)}</p><p class="formula">{escape(method)}</p></section>
<section><h2>Recorded results</h2><div class="table-scroll"><table>{table}</table></div></section>
<section><h2>Interpretation</h2><p class="note">{escape(limitation)}</p></section>
<section><h2>Reproduce</h2><p class="formula">{escape(command)}<br>python scripts/render_study.py</p>
<div class="downloads"><a href="study-data/trials.csv" download>Row-level CSV</a><a href="study-data/summary.json" download>Summary JSON</a></div>
<details><summary>Source checksum</summary><p><code>{hashlib.sha256(source.read_bytes()).hexdigest()}</code></p></details></section>
</main></body></html>"""
(output / "study.html").write_text(page, encoding="utf-8")
print(output / "study.html")
