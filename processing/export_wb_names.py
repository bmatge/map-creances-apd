"""Audit cross-source des noms de pays.

Compare les libellés provenant de :
  - wb_countries.topojson  (NAM_0 — anglais uniquement, source WB GeoJSON)
  - sources/countries.csv  (name_fr, name_en — saisie manuelle)
  - index.html             (dict JS COUNTRY_NAMES.fr / .en, en attendant son retrait)

Sortie : sources/wb_country_names_audit.csv (trié par ISO3).

Usage : python3 processing/export_wb_names.py
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPO = ROOT / 'wb_countries.topojson'
CSV_IN = ROOT / 'sources' / 'countries.csv'
INDEX_HTML = ROOT / 'index.html'
CSV_OUT = ROOT / 'sources' / 'wb_country_names_audit.csv'


def load_topojson_names():
    data = json.loads(TOPO.read_text(encoding='utf-8'))
    out = {}
    for g in data['objects']['countries']['geometries']:
        p = g.get('properties') or {}
        iso = p.get('ISO_A3')
        if not iso:
            continue
        out[iso] = {
            'NAM_0': p.get('NAM_0', '') or '',
            'WB_STATUS': p.get('WB_STATUS', '') or '',
        }
    return out


def load_csv_names():
    out = {}
    with CSV_IN.open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            out[r['iso']] = (r['name_en'], r['name_fr'])
    return out


def load_country_names_dict():
    """Extrait les sous-blocs `fr: { ... }` et `en: { ... }` de COUNTRY_NAMES.

    Retourne ({}, {}) si le bloc a déjà été supprimé d'index.html (post-cleanup).
    """
    text = INDEX_HTML.read_text(encoding='utf-8')
    m = re.search(r'const\s+COUNTRY_NAMES\s*=\s*\{(.*?)\n\};', text, re.DOTALL)
    if not m:
        return {}, {}
    body = m.group(1)
    blocks = {}
    for lang in ('fr', 'en'):
        bm = re.search(rf"{lang}\s*:\s*\{{(.*?)\n\s*\}}", body, re.DOTALL)
        blocks[lang] = bm.group(1) if bm else ''
    pair_re = re.compile(r"'([A-Z]{3})'\s*:\s*'([^']*)'")
    return dict(pair_re.findall(blocks['fr'])), dict(pair_re.findall(blocks['en']))


def main():
    wb = load_topojson_names()
    csv_names = load_csv_names()
    dict_fr, dict_en = load_country_names_dict()

    isos = sorted(set(wb) | set(csv_names) | set(dict_fr) | set(dict_en))

    cols = [
        'iso',
        'nam_0_wb', 'wb_status',
        'name_en_csv', 'name_fr_csv',
        'name_en_dict', 'name_fr_dict',
        'is_match_en',
    ]
    with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for iso in isos:
            wb_e = wb.get(iso, {})
            csv_en, csv_fr = csv_names.get(iso, ('', ''))
            d_fr = dict_fr.get(iso, '')
            d_en = dict_en.get(iso, '')
            en_values = {v for v in (wb_e.get('NAM_0'), csv_en, d_en) if v}
            w.writerow([
                iso,
                wb_e.get('NAM_0', ''), wb_e.get('WB_STATUS', ''),
                csv_en, csv_fr,
                d_en, d_fr,
                len(en_values) <= 1,
            ])
    print(f'Wrote {CSV_OUT.relative_to(ROOT)} ({len(isos)} ISO codes)')


if __name__ == '__main__':
    main()
