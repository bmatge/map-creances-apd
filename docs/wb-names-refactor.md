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

3. **Responsabilités unifiées** :
   - **EN partout (frontend + CSV téléchargeables)** : `NAM_0` du topojson. Source unique de vérité pour l'anglais. `build_data.py` lit le topojson au moment de générer `data.json` et les CSV `downloads/`. Conséquence : libellés affichés = noms officiels WB longs (*"Islamic Republic of Iran"*, *"Lao People's Democratic Republic"*, *"Republic of Yemen"*) plutôt que les noms courts antérieurs.
   - **FR** : `name_fr` de `sources/countries.csv` (saisie manuelle, 181 pays APD). La colonne `name_en` du CSV a été supprimée (devenue redondante).
   - **Fallback FR pour territoires hors APD** : `NAM_0` (anglais), acceptable car ces polygones (~63) ne sont jamais survolés.
   - Suppression du dict JS `COUNTRY_NAMES` côté `index.html` (100 lignes) et de tous les fallbacks morts (`d?.properties?.name`, `|| c.country`).

## Fichiers modifiés

| Fichier | Action |
|---|---|
| `processing/build_topojson.py` | **Nouveau** (~80 lignes) — DL + fix encoding + mapshaper |
| `processing/build_data.py` | `load_countries()` lit `NAM_0` du topojson pour les noms EN (fini la dépendance à `name_en` du CSV) |
| `processing/export_wb_names.py` | **Nouveau** — audit `NAM_0` (topojson) vs `name_fr` (CSV) |
| `sources/countries.csv` | Colonne `name_en` supprimée (devenue redondante) ; CSV passe à 2 colonnes `iso,name_fr` couvrant les 244 ISO du layer `countries` |
| `sources/wb_country_names_audit.csv` | **Nouveau** — sortie de l'audit (244 ISO, colonnes `iso,name_en_wb,wb_status,name_fr_csv,in_apd_dataset`) |
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

- **Bug encoding source WB** : la World Bank publie le GeoJSON avec un double-encodage UTF-8 sur les caractères accentués. Le script Python le corrige ; à surveiller à chaque mise à jour amont.
- **DOM-TOM français** (`MTQ`, `GLP`, `GUF`, `REU`, `MYT`) : dans le GeoJSON WB chacun a un ISO_A3 distinct mais leur `NAM_0` vaut tous "France" — la WB les a fusionnés sémantiquement avec la métropole. Cosmétique uniquement (ces ISO n'ont pas de données APD distinctes).

## Couche `land` en arrière-plan (Natural Earth)

La World Bank omet délibérément certains territoires (ATA Antarctique, ESH Sahara occidental, FLK îles Malouines, TWN Taïwan) pour raisons diplomatiques, et certaines zones administrativement floues (Abyei Soudan/Sud-Soudan, eaux territoriales, micro-bandes entre polygones WB qui ne se tilent pas parfaitement) restent en couleur "mer" si on rend uniquement le layer WB.

Plutôt que de greffer des polygones politiques contestables (essai antérieur via NE countries 10m : alignement imparfait et redondance avec la position éditoriale WB), on ajoute une **couche `land` neutre** depuis Natural Earth 10m (11 multipolygones du contour terrestre, sans aucun attribut politique, ~10 Mo source → ~33 Ko dans le topojson final).

Le frontend la dessine en premier en couleur `DEFAULT_COLOR` (#e8c4b0) avant les polygones politiques WB, sans `pointer-events`. Conséquences :
- Les zones omises par WB reçoivent la couleur "terre" (pas de tooltip, pas de clic) → carte visuellement complète.
- Pas de prise de position politique : on dessine "il y a de la terre ici", pas "voici la frontière X".
- Les micro-trous entre polygones WB sont comblés automatiquement.

## Suites possibles

- Auditer les 14 mismatches EN du CSV et décider d'éventuels overrides frontend.
- Étendre `countries.csv` avec les ~63 territoires hors APD si on veut une couverture FR complète.
- Convertir le pipeline en GitHub Action (build_topojson.py + build_data.py) pour qu'une simple modif de `sources/*.csv` déclenche automatiquement la régénération de `data.json` (déjà partiellement en place via `.github/workflows/build-data.yml`).
