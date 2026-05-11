"""Build wb_countries.topojson from the World Bank Official Boundaries GeoJSON.

Pipeline :
  1. Télécharge `World Bank Official Boundaries - Admin 0.geojson` (cache local
     dans `downloads/wb_admin0.geojson`).
  2. Télécharge Natural Earth 110m comme source de complément pour les ISO que
     la World Bank omet pour raisons diplomatiques (ATA, ESH, FLK, TWN).
  3. Fixe le double-encodage UTF-8 dans le champ `NAM_0` (~7 noms cassés en
     amont par la World Bank, ex. "TÃ¼rkiye" → "Türkiye") puis ajoute les
     polygones de complément en réécrivant leurs attributs au schéma WB.
  4. Écrit le tout dans `downloads/wb_admin0_fixed.geojson`.
  5. Lance mapshaper pour filtrer les colonnes, simplifier (1%) et sortir
     `wb_countries.topojson` à la racine du projet.

Usage : python3 processing/build_topojson.py [--force-download]

Dépendance externe : mapshaper (npm install -g mapshaper).
"""
import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = ROOT / 'downloads'
RAW_GEOJSON = DOWNLOADS / 'wb_admin0.geojson'
NE_GEOJSON = DOWNLOADS / 'ne_admin0_10m.geojson'
NE_LAND_GEOJSON = DOWNLOADS / 'ne_10m_land.geojson'
FIXED_GEOJSON = DOWNLOADS / 'wb_admin0_fixed.geojson'
OUT_TOPOJSON = ROOT / 'wb_countries.topojson'

GEOJSON_URL = (
    'https://datacatalogfiles.worldbank.org/ddh-published/0038272/5/DR0095369/'
    'World%20Bank%20Official%20Boundaries%20(GeoJSON)/'
    'World%20Bank%20Official%20Boundaries%20-%20Admin%200.geojson'
)
# Natural Earth 10m has the same resolution as the World Bank Admin0_10m
# source (both 1:10,000,000). Picking a coarser NE tier (50m, 110m) makes
# the supplement polygons visibly misaligned with neighbouring WB borders.
NE_URL = (
    'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/'
    'geojson/ne_10m_admin_0_countries.geojson'
)
# Land outline at 10m, drawn behind the country polygons as a neutral
# backdrop to fill visual gaps in disputed/no-data zones (Abyei area,
# unclaimed strips, narrow borders). 11 multipolygon features.
NE_LAND_URL = (
    'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/'
    'geojson/ne_10m_land.geojson'
)

# ISO codes World Bank omits for political reasons but ISO 3166 / Natural
# Earth still tracks. We graft these from Natural Earth to avoid visible
# holes on the map (Sahara, Falklands, Taiwan, Antarctica). Validate by
# rerunning the diff against `ne_admin0_110m.geojson` after each WB refresh.
SUPPLEMENT_ISOS = ('ATA', 'ESH', 'FLK', 'TWN')


def _has_mapshaper():
    return shutil.which('mapshaper') is not None


def _download(url, target, force, label, size_hint):
    if target.exists() and not force:
        print(f'Cached {target.relative_to(ROOT)} ({target.stat().st_size:,} bytes) — use --force-download to refresh')
        return
    DOWNLOADS.mkdir(exist_ok=True)
    print(f'Downloading {label} ({size_hint})...')
    urllib.request.urlretrieve(url, target)
    print(f'  saved to {target.relative_to(ROOT)} ({target.stat().st_size:,} bytes)')


def download_geojson(force=False):
    _download(GEOJSON_URL, RAW_GEOJSON, force, 'World Bank Admin 0 GeoJSON', '~172 MB')
    _download(NE_URL, NE_GEOJSON, force, 'Natural Earth 10m countries', '~13 MB')
    _download(NE_LAND_URL, NE_LAND_GEOJSON, force, 'Natural Earth 10m land outline', '~10 MB')


def _collect_supplement_features():
    """Extract ATA/ESH/FLK/TWN polygons from Natural Earth, mapped to WB schema."""
    with NE_GEOJSON.open(encoding='utf-8') as f:
        data = json.load(f)
    out = []
    for feat in data.get('features', []):
        p = feat.get('properties') or {}
        iso = p.get('ISO_A3')
        if iso not in SUPPLEMENT_ISOS:
            continue
        out.append({
            'type': 'Feature',
            'properties': {
                'ISO_A3': iso,
                'WB_A3': iso,
                'NAM_0': p.get('NAME_EN'),
                'WB_STATUS': 'Supplemented',
                'SOVEREIGN': '',
            },
            'geometry': feat.get('geometry'),
        })
    return out


def _fix_double_utf8(s):
    """Decode strings double-encoded as latin-1→UTF-8 by the WB pipeline.

    "TÃ¼rkiye" (the file's literal bytes for a string that *should* be
    "Türkiye") is reinterpreted by encoding back to latin-1 then decoding as
    UTF-8. Strings that don't carry the double-encoding markers are returned
    unchanged.
    """
    if not s or 'Ã' not in s and 'Â' not in s:
        return s
    try:
        return s.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def prepare_geojson():
    print(f'Loading {RAW_GEOJSON.relative_to(ROOT)} (this takes a few seconds)...')
    with RAW_GEOJSON.open(encoding='utf-8') as f:
        data = json.load(f)
    fixed = 0
    for feat in data.get('features', []):
        props = feat.get('properties') or {}
        original = props.get('NAM_0')
        if not original:
            continue
        new = _fix_double_utf8(original)
        if new != original:
            props['NAM_0'] = new
            fixed += 1
    print(f'  patched {fixed} NAM_0 values')

    supplements = _collect_supplement_features()
    wb_isos = {(f.get('properties') or {}).get('ISO_A3') for f in data['features']}
    grafted = []
    for feat in supplements:
        iso = feat['properties']['ISO_A3']
        if iso in wb_isos:
            print(f'  skipping supplement {iso}: already in WB dataset')
            continue
        data['features'].append(feat)
        grafted.append(iso)
    print(f'  grafted {len(grafted)} Natural Earth supplements: {", ".join(grafted) or "(none)"}')

    with FIXED_GEOJSON.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f'  wrote {FIXED_GEOJSON.relative_to(ROOT)} ({FIXED_GEOJSON.stat().st_size:,} bytes)')


def run_mapshaper():
    if not _has_mapshaper():
        sys.exit('error: mapshaper not found in PATH. Install with: npm install -g mapshaper')
    cmd = [
        'mapshaper',
        '-i', str(FIXED_GEOJSON), 'name=countries',
        '-filter-fields', 'ISO_A3,WB_A3,NAM_0,WB_STATUS,SOVEREIGN',
        # Member State features ahead of Territory features sharing the same
        # ISO_A3 (Spain, GBR, France, Australia have territory enclaves with
        # the same code; we want the principal polygon's metadata to win).
        '-sort', 'WB_STATUS === "Member State" ? 0 : 1',
        '-dissolve2', 'ISO_A3', 'copy-fields=ISO_A3,WB_A3,NAM_0,WB_STATUS,SOVEREIGN',
        '-simplify', '1%', 'keep-shapes',
        # Second input: Natural Earth land outline as a neutral backdrop.
        # `combine-layers` on -o packs both layers into a single topojson.
        '-i', str(NE_LAND_GEOJSON), 'name=land',
        '-filter-fields', 'featurecla',
        '-simplify', '1%', 'keep-shapes',
        '-o', 'format=topojson', 'combine-layers', str(OUT_TOPOJSON),
    ]
    print('Running:', ' '.join(cmd))
    subprocess.run(cmd, check=True)
    print(f'  wrote {OUT_TOPOJSON.relative_to(ROOT)} ({OUT_TOPOJSON.stat().st_size:,} bytes)')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--force-download', action='store_true',
                   help='re-download the GeoJSON even if cached')
    args = p.parse_args()

    download_geojson(force=args.force_download)
    prepare_geojson()
    run_mapshaper()


if __name__ == '__main__':
    main()
