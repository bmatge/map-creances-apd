# Repo memory — Club de Paris map

## Target file

**The live file for this project is `index.html` at the repo root.**

It is a standalone HTML document built around a Web Component
(`<club-paris-map>`) that uses D3 v7 + topojson-client. It is self-contained:
translations (`TRANSLATIONS`), country name dictionaries (`COUNTRY_NAMES`),
styles (`_getStyles()`), and all component logic live inside the single
`<script>` block. No build step.

The map fetches `./data.json` (same directory as `index.html`) at runtime.

## Repo layout

```
map-creances-apd/
├── index.html              ← the live map (standalone)
├── data.json               ← data consumed by the map, produced by the pipeline
├── favicon.svg
├── data-pipeline/          ← offline Python pipeline
│   ├── build_data.py       ← CSV/Excel → data.json
│   ├── countries.yml       ← ISO-3 mapping, aliases, URL slugs, FR/EN names
│   ├── requirements.txt
│   ├── README.md           ← **input schema spec lives here**
│   └── sources/            ← raw CSV/XLSX inputs (xlsx is .gitignored)
├── .github/workflows/deploy.yml   ← GitHub Pages (no build, uploads root)
└── CLAUDE.md               ← this file
```

## Data source

- `./data.json` — loaded at runtime by the component
  (`fetch(base + 'data.json')` with `base = new URL('.', location.href).href`).
- Produced by `python data-pipeline/build_data.py --input sources/<file>`.
- World topology: `https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json`
  (Natural Earth via `world-atlas@2`, **not** the IMF boundaries).

## Data pipeline — how to regenerate data.json

```
pip install -r data-pipeline/requirements.txt
python data-pipeline/build_data.py \
    --input data-pipeline/sources/<file>.csv \
    --out data.json
```

For the legacy Excel workbook:

```
python data-pipeline/build_data.py \
    --input data-pipeline/sources/Club_de_Paris_Consolidé_2010-2024.xlsx \
    --sheet "Données consolidées"
```

When the pipeline reports an unmapped country, add the variant to the
relevant ISO entry's `aliases:` list in `data-pipeline/countries.yml`
(do **not** modify the raw source file).

Input schema is documented in full at `data-pipeline/README.md`.

## i18n

- Languages: `fr` (default), `en`. Detected from `lang` attribute,
  `?lang=` query param, or `<html lang>`.
- To add a UI string: extend `TRANSLATIONS.fr` and `TRANSLATIONS.en` inside
  `index.html`, then use `this._t('key')` in markup.
- To fix a country name: edit `COUNTRY_NAMES.fr` / `COUNTRY_NAMES.en` inside
  `index.html` **and** the matching `name_fr` / `name_en` in
  `data-pipeline/countries.yml` (they must stay in sync for the ingestion
  aliases to work).
- Reference list: clubdeparis.org (FR and `/en/` mirror). `WebFetch` is
  blocked (HTTP 403) so fetching the site programmatically from the sandbox
  does not work — apply corrections manually from a pasted list.

## Visual conventions (current)

- Debtor color: `#f97316` (orange).
- Creditor color: `#1e40af` (blue).
- Default / no-data fill: `#e8c4b0`.
- Stroke color for selected country: `#fbbf24`.
- Mode "Tous" : dual-status countries (debtor AND creditor) render in the
  debtor color (orange takes precedence).
- Legend uses two fixed swatches, **no gradient scale**.
- Creditor section title in the panel is dynamic:
  `Pays créancier (permanent | ad hoc | prospectif)`, based on
  `creditor.statut` (`null` → permanent, `'Ad hoc'`, `'Prospectif'`).

## Dev & deploy

- **Local dev**: `python3 -m http.server 8000` at the repo root, open
  http://localhost:8000/. No Node, no npm, no Vite. Editing `index.html` and
  reloading the page is all you need.
- **Deploy**: pushing to `main` triggers `.github/workflows/deploy.yml` which
  uploads the repo root (minus `.git`, `.github`, `data-pipeline`) to GitHub
  Pages. No build step.

## Git workflow

- Default working branch for automated cleanup/feature work:
  `claude/cleanup-data-pipeline-RdemJ`.
- Commit message style: conventional (`fix:`, `feat:`, `chore:`, `refactor:`)
  in French, no PR unless explicitly asked.
