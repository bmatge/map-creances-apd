# Refonte des noms de pays — World Bank comme source autoritaire

> Session du 7 mai 2026 · branche `refactor/wb-names-authority`

## Contexte initial

Trois questions soulevées sur l'affichage des noms de pays :

1. **Soupçon de transformation** dans la conversion shapefile → topojson — exemple cité : "Greenland (Den.)" qui apparaissait simplement comme "Greenland" sur la carte.
2. **Origine des traductions FR** non documentée : qui a saisi quoi, peut-on auditer ?
3. **Logique d'affichage** à inverser : le topojson WB devait faire autorité pour les noms, pas un dictionnaire JS hardcodé.

## Ce qu'on a découvert

### Pas de transformation côté pipeline

L'ancienne commande mapshaper (documentée dans le README) ne touchait pas aux noms — elle copiait `NAME_EN` / `NAME_FR` du shapefile WB tels quels. Le format "Greenland (Den.)" venait en réalité d'**une autre colonne** du shapefile (`WB_NAME`) qui n'était pas conservée par le `-filter-fields`.

### Trois sources de noms désynchronisées

Les noms vivaient à trois endroits, tous saisis manuellement, jamais synchronisés :

- `sources/countries.csv` (colonnes `name_fr` / `name_en`) — lu par `build_data.py`.
- `index.html` lignes 195-294 (dict JS `COUNTRY_NAMES.fr` / `.en`, ~180 entrées par langue) — source primaire d'affichage.
- `wb_countries.topojson` (`NAME_EN` / `NAME_FR` du shapefile) — **jamais lu** par le frontend.

Symptôme du désordre : commit `4d97bd4` corrigeant 7 ISO (BHR, BLR, CZE, DOM, PLW, TLS, VUT) qui manquaient au dict JS.

### Bugs structurels du shapefile WB Admin0_10m

En investiguant, deux problèmes côté pipeline mapshaper original :

- **Collision USA** : 3 features partageaient `WB_A3="USA"` (Guantanamo Lease, États-Unis Country, UMI Dependency). Le `-dissolve2 MATCH_ID` copiait les attributs de la **première** feature → "Guantanamo Bay Naval Base" était promu comme libellé pour USA après fusion. Caché tant que `COUNTRY_NAMES` masquait tout.
- **Noms outdated** : NAME_FR du shapefile avait encore "Swaziland" (renommé Eswatini en 2018), "République de Macédoine" (renommée 2019), "Turkey" (Türkiye en 2022).

## Décisions prises

1. **Source autoritaire** : passer du shapefile *Admin0_10m* (juin 2025) à la version GeoJSON *Admin 0* (sept 2025) du même dataset WB. La version récente :
   - Inclut les noms à jour (Eswatini, North Macedonia, Türkiye, Myanmar, Timor-Leste, Viet Nam) ;
   - N'a pas la collision USA/Guantanamo ;
   - A le code Kosovo directement en `XKX` (plus besoin de remap KSV→XKX) ;
   - Inclut les parenthétiques territoires nativement dans `NAM_0` ("Greenland (Den.)", "Puerto Rico (U.S.)") ;
   - **MAIS** : un seul champ nom (`NAM_0`, anglais), pas de NAME_FR.

2. **Pipeline reproductible** via un script Python (au lieu d'une commande mapshaper documentée à exécuter à la main) :
   - DL du GeoJSON dans `downloads/` (cache, gitignored, ~172 Mo) ;
   - Fix d'un bug de double-encodage UTF-8 du fichier source (~7 noms : TUR, CIV, STP, BLM, CUW, ESP×2) ;
   - mapshaper en sous-processus avec `-sort` priorisant les `Member State` avant les `Territory` partageant le même `ISO_A3` (sinon Ceuta/Bonaire/Clipperton remplacent Spain/Netherlands/France comme attributs principaux).

3. **Responsabilités côté frontend** :
   - **EN** : `NAM_0` du topojson — autoritaire, à jour, avec parenthétiques pour territoires.
   - **FR** : champ `country` de `data.json` (peuplé depuis `countries.csv`) — saisie manuelle assumée. Pour les ~63 territoires hors APD non présents dans `countries.csv`, fallback sur `NAM_0` (anglais), acceptable car ces polygones ne sont pas survolés en pratique.
   - Suppression du dict JS `COUNTRY_NAMES` (100 lignes) et de tous les fallbacks morts (`d?.properties?.name`, `|| c.country`).

## Fichiers modifiés

| Fichier | Action |
|---|---|
| `processing/build_topojson.py` | **Nouveau** (~80 lignes) — DL + fix encoding + mapshaper |
| `processing/export_wb_names.py` | **Nouveau** — script d'audit cross-source |
| `sources/wb_country_names_audit.csv` | **Nouveau** — sortie de l'audit (244 ISO, colonnes `nam_0_wb` / CSV / dict / `is_match_en`) |
| `wb_countries.topojson` | Régénéré depuis le nouveau GeoJSON, 456 KB (vs 295 KB avant, simplification 1 % au lieu de 5 %) |
| `index.html` | -90 lignes : suppression `COUNTRY_NAMES`, ajout `_wbNames` lu au load, `_isoToName` lit data.json en FR + topojson en EN |
| `README.md` | Section "Frontières" récrite (passage shapefile → GeoJSON, doc du nouveau script Python) |
| `.gitignore` | Ignore `downloads/wb_admin0*.geojson` (~330 Mo cumulés, regénérables) |

## Comment régénérer

```bash
npm install -g mapshaper           # dépendance externe (CLI)
python3 processing/build_topojson.py
python3 processing/export_wb_names.py    # met à jour le CSV d'audit
python3 processing/build_data.py         # régénère data.json
```

## Points de friction connus

- **Affichage hybride pour territoires non-APD** en mode FR : on voit "Greenland (Den.)" au lieu de "Groenland (Dan.)". Acceptable parce que ces territoires (~63) n'ont pas de données APD donc leur nom n'apparaît jamais ni en tooltip ni en panneau. Si on veut corriger un jour : enrichir `countries.csv` ou ajouter une table de suffixes territoriaux côté JS.
- **Noms WB officiels longs** en EN qui pourraient déranger : "Lao People's Democratic Republic" au lieu de "Laos", "Republic of Yemen" au lieu de "Yemen", "Islamic Republic of Iran" au lieu de "Iran". 14 cas dans l'audit. Si gênant : créer un dict d'overrides côté frontend (~10 entrées) plutôt que d'éditer le pipeline mapshaper.
- **Bug encoding source WB** : la World Bank publie le GeoJSON avec un double-encodage UTF-8 sur les caractères accentués. Le script Python le corrige ; à surveiller à chaque mise à jour amont.

## Suites possibles

- Auditer les 14 mismatches EN du CSV et décider d'éventuels overrides frontend.
- Étendre `countries.csv` avec les ~63 territoires hors APD si on veut une couverture FR complète.
- Convertir le pipeline en GitHub Action (build_topojson.py + build_data.py) pour qu'une simple modif de `sources/*.csv` déclenche automatiquement la régénération de `data.json` (déjà partiellement en place via `.github/workflows/build-data.yml`).
