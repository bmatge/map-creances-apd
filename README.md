# Club de Paris — Carte interactive

Standalone HTML map of Club de Paris debtor and creditor countries
(2010–2024), built with D3 v7 + topojson-client. No build step.

**Live file**: [`index.html`](./index.html) — a self-contained web
component (`<club-paris-map>`) that loads [`data.json`](./data.json) and a
world topology from jsDelivr.

Languages: French (default) and English, via `?lang=en`, `lang="en"`
attribute, or `<html lang>`.

## Run locally

```bash
python3 -m http.server 8000
# → http://localhost:8000/
```

That is the whole dev setup. Edit `index.html`, reload the page.

## Regenerate `data.json`

Data is generated from a CSV or Excel source by the offline pipeline in
[`data-pipeline/`](./data-pipeline/). See
[`data-pipeline/README.md`](./data-pipeline/README.md) for the full input
schema.

```bash
pip install -r data-pipeline/requirements.txt
python data-pipeline/build_data.py \
    --input data-pipeline/sources/<file>.csv
```

The pipeline writes `./data.json` at the repo root (same directory as
`index.html`).

## Deploy

Pushing to `main` triggers GitHub Pages via
[`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml): it
uploads `index.html`, `data.json` and `favicon.svg` as-is. No Node, no
bundler.

## Repo layout

```
map-creances-apd/
├── index.html              ← the map (standalone)
├── data.json               ← data consumed by the map
├── favicon.svg
├── data-pipeline/          ← Python pipeline (offline)
│   ├── build_data.py
│   ├── countries.yml
│   ├── requirements.txt
│   ├── README.md           ← input schema spec
│   └── sources/
├── .github/workflows/deploy.yml
├── CLAUDE.md               ← agent memory / repo conventions
└── README.md
```
