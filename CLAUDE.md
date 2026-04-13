# CLAUDE.md — map-creances-apd

> **Important** : ce fichier ne réécrit pas la doc du projet. Avant toute tâche, **lire d'abord** les docs listées ci-dessous.

## 📚 Documentation à lire en priorité

- [README.md](README.md) — structure du repo, schéma des CSV, pipeline
- Fiche vault : `~/Documents/Obsidian/10-Projects/map-creances-apd.md`

## 🧰 Indices de stack

Site statique **zéro build** :
- `index.html` — Web Component autonome (`<club-paris-map>`), Shadow DOM, D3 v7 + TopoJSON en CDN, i18n FR/EN intégrée.
- `data.json` — dataset généré, **ne pas éditer à la main**.
- `sources/*.csv` — source de vérité (4 CSV : countries, debtors, creditors, country_urls).
- `processing/build_data.py` — stdlib Python pure, transforme les CSV → `data.json`.
- `.github/workflows/` : `build-data.yml` (auto-regen sur modif de `sources/`) + `deploy.yml` (GitHub Pages).

## 🗄️ Contexte Obsidian

- Fiche projet : `~/Documents/Obsidian/10-Projects/map-creances-apd.md`
- ADR historiques : `~/Documents/Obsidian/30-Knowledge/ADR/` (filtrer par `project: map-creances-apd`)
- Sessions précédentes : `~/Documents/Obsidian/20-Sessions/` (frontmatter `projects:` contient `map-creances-apd`)

## ✅ Règles Claude-specific

1. **Toujours lire le README et la fiche vault avant d'agir**. Ne pas supposer le pipeline.
2. **Les données se modifient dans `sources/*.csv` uniquement**. `data.json` est un artefact — si tu dois le regénérer : `python3 processing/build_data.py`.
3. **Toute feature visuelle / comportement** se touche dans `index.html` (unique fichier, Web Component interne). Pas de build, pas de bundler.
4. **Décision structurante** → `/new-adr "<titre>"`.
5. **Fin de session significative** → `/session-end`.
6. **Pas de commit direct sur `main`**, pas de `git push --force`, pas de modification des `.env*`.
7. **Pas d'install de dépendance nouvelle** sans m'en parler. Le build actuel est volontairement stdlib-only.
8. Doc obsolète ou manquante sur un point → **le signaler** et proposer de la mettre à jour.

## 📏 Règle d'or

Ce fichier doit rester **sous 80 lignes**. Son unique rôle : pointer vers la vraie doc et rappeler les règles Claude.
