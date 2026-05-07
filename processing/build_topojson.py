"""Build wb_countries.topojson from the World Bank Official Boundaries GeoJSON.

Pipeline :
  1. Télécharge `World Bank Official Boundaries - Admin 0.geojson` (cache local
     dans `downloads/wb_admin0.geojson`).
  2. Fixe le double-encodage UTF-8 dans le champ `NAM_0` (~7 noms cassés en
     amont par la World Bank, ex. "TÃ¼rkiye" → "Türkiye").
  3. Écrit la version corrigée dans `downloads/wb_admin0_fixed.geojson`.
  4. Lance mapshaper pour filtrer les colonnes, simplifier (1%) et sortir
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
FIXED_GEOJSON = DOWNLOADS / 'wb_admin0_fixed.geojson'
OUT_TOPOJSON = ROOT / 'wb_countries.topojson'

GEOJSON_URL = (
    'https://datacatalogfiles.worldbank.org/ddh-published/0038272/5/DR0095369/'
    'World%20Bank%20Official%20Boundaries%20(GeoJSON)/'
    'World%20Bank%20Official%20Boundaries%20-%20Admin%200.geojson'
)


def _has_mapshaper():
    return shutil.which('mapshaper') is not None


def download_geojson(force=False):
    if RAW_GEOJSON.exists() and not force:
        size = RAW_GEOJSON.stat().st_size
        print(f'Cached {RAW_GEOJSON.relative_to(ROOT)} ({size:,} bytes) — use --force-download to refresh')
        return
    DOWNLOADS.mkdir(exist_ok=True)
    print(f'Downloading {GEOJSON_URL.rsplit("/", 1)[-1]} (~172 MB)...')
    urllib.request.urlretrieve(GEOJSON_URL, RAW_GEOJSON)
    print(f'  saved to {RAW_GEOJSON.relative_to(ROOT)} ({RAW_GEOJSON.stat().st_size:,} bytes)')


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


def fix_encoding():
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
    with FIXED_GEOJSON.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f'  wrote {FIXED_GEOJSON.relative_to(ROOT)} ({FIXED_GEOJSON.stat().st_size:,} bytes)')


def run_mapshaper():
    if not _has_mapshaper():
        sys.exit('error: mapshaper not found in PATH. Install with: npm install -g mapshaper')
    cmd = [
        'mapshaper',
        str(FIXED_GEOJSON),
        '-filter-fields', 'ISO_A3,WB_A3,NAM_0,WB_STATUS,SOVEREIGN',
        # Member State features ahead of Territory features sharing the same
        # ISO_A3 (Spain, GBR, France, Australia have territory enclaves with
        # the same code; we want the principal polygon's metadata to win).
        '-sort', 'WB_STATUS === "Member State" ? 0 : 1',
        '-dissolve2', 'ISO_A3', 'copy-fields=ISO_A3,WB_A3,NAM_0,WB_STATUS,SOVEREIGN',
        '-simplify', '1%', 'keep-shapes',
        '-rename-layers', 'countries',
        '-o', 'format=topojson', str(OUT_TOPOJSON),
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
    fix_encoding()
    run_mapshaper()


if __name__ == '__main__':
    main()
