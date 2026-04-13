# Repo memory — Club de Paris map

## Target file

**The live file for this project is `app/public/club-paris-map-v2.html`.**

All feature work, bug fixes, and design changes for the Club de Paris map must
be made in this file. It is a standalone HTML document built around a Web
Component (`<club-paris-map>`) that uses D3 v7 + topojson-client. It is
self-contained: translations (`TRANSLATIONS`), country name dictionaries
(`COUNTRY_NAMES`), styles (`_getStyles()`), and all component logic live inside
the single `<script>` block.

### Do NOT modify for feature work
- `app/src/**` — a legacy React/Vite + `react-simple-maps` implementation.
  Kept in the repo but no longer the live file. Do not add features there.
  Existing code may remain in sync for parity, but the v2 HTML is canonical.
- `app/public/club-paris-map.html` — earlier standalone version, superseded.
- `club-paris-map.html` (repo root) — older copy.

### Data source
- `app/public/data.json` — loaded at runtime by the component
  (`fetch(base + 'data.json')`).
- World topology: `https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json`
  (Natural Earth via `world-atlas@2`, **not** the IMF boundaries).

### i18n
- Languages: `fr` (default), `en`. Detected from `lang` attribute,
  `?lang=` query param, or `<html lang>`.
- To add a UI string: extend `TRANSLATIONS.fr` and `TRANSLATIONS.en`, then use
  `this._t('key')` in markup.
- To fix a country name: edit `COUNTRY_NAMES.fr` / `COUNTRY_NAMES.en`.
  Reference list: clubdeparis.org (FR and `/en/` mirror). `WebFetch` is
  blocked (HTTP 403) so fetching the site programmatically from the sandbox
  does not work — apply corrections manually from a pasted list.

### Visual conventions (current)
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

### Dev & build
- `cd app && npm install --legacy-peer-deps` (react-simple-maps peer conflict).
- `npm run dev` → http://localhost:5173/club-paris-map-v2.html
- `npm run build` → copies `public/` to `dist/`. Dist is git-ignored.
- `npm run lint` — 2 pre-existing errors in `app/src/App.tsx:45` and
  `app/src/i18n/LangContext.tsx:54` unrelated to v2.html.

### Git workflow
- Current feature branch: `claude/fix-paris-club-map-FvT21`.
- Commit message style: conventional (`fix:`, `feat:`) in French, no PR
  unless explicitly asked.
