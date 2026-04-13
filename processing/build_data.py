#!/usr/bin/env python3
"""Build data.json from the 4 CSV sources in /sources.

Usage: python3 processing/build_data.py [--check]
  --check: fail if the generated data.json differs from the existing one
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'sources'
OUT = ROOT / 'data.json'


def load_countries():
    rows = {}
    with (SRC / 'countries.csv').open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows[r['iso']] = {'name_fr': r['name_fr'], 'name_en': r['name_en']}
    return rows


def load_urls():
    by_iso_role = {}
    with (SRC / 'country_urls.csv').open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            by_iso_role[(r['iso'], r['role'])] = {
                'url_fr': r['url_fr'] or None,
                'url_en': r['url_en'] or None,
            }
    return by_iso_role


def load_debtors():
    rows = []
    with (SRC / 'debtors.csv').open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append({
                'year': r['year'],
                'iso': r['iso'],
                'apd': float(r['apd_eur']) if r['apd_eur'] else 0.0,
                'napd': float(r['napd_eur']) if r['napd_eur'] else 0.0,
            })
    return rows


def load_creditors():
    rows = []
    with (SRC / 'creditors.csv').open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append({
                'year': r['year'],
                'iso': r['iso'],
                'nb_accords': int(r['nb_accords']) if r['nb_accords'] else 0,
                'statut': r['statut'] or None,
                'premiere': int(r['premiere_participation']) if r['premiere_participation'] else None,
            })
    return rows


def _clean(v):
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def build():
    countries = load_countries()
    urls = load_urls()
    debtors = load_debtors()
    creditors = load_creditors()

    years = {}
    for row in debtors + creditors:
        year = row['year']
        iso = row['iso']
        if iso not in countries:
            raise SystemExit(f'Unknown ISO in {year}: {iso} (missing from countries.csv)')
        years.setdefault(year, {}).setdefault(iso, {
            'country': countries[iso]['name_fr'],
        })

    for r in debtors:
        entry = years[r['year']][r['iso']]
        url = urls.get((r['iso'], 'debtor'), {}).get('url_fr')
        entry['debtor'] = {
            'apd': _clean(round(r['apd'], 2)),
            'napd': _clean(round(r['napd'], 2)),
            'total': _clean(round(r['apd'] + r['napd'], 2)),
            'url': url,
        }

    for r in creditors:
        entry = years[r['year']][r['iso']]
        url = urls.get((r['iso'], 'creditor'), {}).get('url_fr')
        entry['creditor'] = {
            'nbAccords': r['nb_accords'],
            'statut': r['statut'],
            'premiereParticipation': r['premiere'],
            'url': url,
        }

    final = {}
    for year in sorted(years):
        countries_year = years[year]
        tot_apd = tot_napd = tot = 0
        n_deb = n_cred = 0
        for entry in countries_year.values():
            if 'debtor' in entry:
                tot_apd += entry['debtor']['apd']
                tot_napd += entry['debtor']['napd']
                tot += entry['debtor']['total']
                n_deb += 1
            if 'creditor' in entry:
                n_cred += 1
        final[year] = {
            'countries': countries_year,
            'totals': {
                'debtorApd': _clean(round(tot_apd, 2)),
                'debtorNapd': _clean(round(tot_napd, 2)),
                'debtorTotal': _clean(round(tot, 2)),
                'debtorCount': n_deb,
                'creditorCount': n_cred,
            },
        }
    return final


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true', help='fail if data.json would change')
    args = p.parse_args()

    final = build()
    serialized = json.dumps(final, ensure_ascii=False, indent=2) + '\n'

    if args.check:
        if not OUT.exists():
            print(f'error: {OUT} does not exist', file=sys.stderr)
            sys.exit(1)
        if OUT.read_text(encoding='utf-8') != serialized:
            print(f'error: {OUT} is out of date. Run: python3 processing/build_data.py', file=sys.stderr)
            sys.exit(1)
        print('data.json is up to date.')
        return

    OUT.write_text(serialized, encoding='utf-8')
    n_years = len(final)
    print(f'Wrote {OUT} ({n_years} years)')


if __name__ == '__main__':
    main()
