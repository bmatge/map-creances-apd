"""Audit cross-source des noms de pays.

Compare les libellés provenant de :
  - wb_countries.topojson  (NAM_0 — anglais, source autoritaire)
  - sources/countries.csv  (name_fr — traduction française, saisie manuelle)

Sortie : sources/wb_country_names_audit.csv (trié par ISO3).

Usage : python3 processing/export_wb_names.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPO = ROOT / 'wb_countries.topojson'
CSV_IN = ROOT / 'sources' / 'countries.csv'
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
            out[r['iso']] = r['name_fr']
    return out


def main():
    wb = load_topojson_names()
    fr_names = load_csv_names()
    isos = sorted(set(wb) | set(fr_names))

    with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['iso', 'name_en_wb', 'wb_status', 'name_fr_csv', 'in_apd_dataset'])
        for iso in isos:
            wb_e = wb.get(iso, {})
            fr = fr_names.get(iso, '')
            w.writerow([
                iso,
                wb_e.get('NAM_0', ''), wb_e.get('WB_STATUS', ''),
                fr, bool(fr),
            ])
    print(f'Wrote {CSV_OUT.relative_to(ROOT)} ({len(isos)} ISO codes)')


if __name__ == '__main__':
    main()
