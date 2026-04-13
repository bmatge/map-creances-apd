# Data pipeline — Club de Paris map

Generates `../data.json` (consumed by `../index.html`) from a CSV or Excel
source describing, for each year, the debtor and creditor countries of the
Club de Paris.

```
sources/*.csv | sources/*.xlsx
              │
              ▼
         build_data.py  ◀──  countries.yml   (ISO mapping, URL slugs, names)
              │
              ▼
        ../data.json
```

## 1. Install

```
pip install -r requirements.txt
```

`openpyxl` is optional; only required if your source is `.xlsx`.

## 2. Run

```
python build_data.py --input sources/my_file.csv
python build_data.py --input sources/my_file.xlsx --sheet "Données consolidées"
python build_data.py --check           # validate countries.yml only
```

Default output is `../data.json` (i.e. next to `index.html` at the repo root).

## 3. Input schema

One row per (year, country, role). Column order does not matter.
Column names are matched case-insensitively; accented French headers from the
legacy 2010–2024 workbook are recognized (`année`, `apd`, `napd`, …) and
normalized to the canonical names below.

| Column                   | Type  | Required | Used by   | Description                                                                 |
|--------------------------|-------|----------|-----------|-----------------------------------------------------------------------------|
| `annee`                  | int   | yes      | both      | Year (1900–2099).                                                           |
| `pays`                   | str   | yes      | both      | Country name as it appears in the source. Matched against `countries.yml` aliases (whitespace-collapsed, accent-insensitive). |
| `role`                   | str   | no       | both      | `debtor` or `creditor`. If omitted, UPPERCASE `pays` → creditor, Title-case → debtor (legacy convention). |
| `apd_meur`               | float | debtor   | debtor    | APD creance in millions of EUR.                                             |
| `napd_meur`              | float | debtor   | debtor    | Non-APD creance in millions of EUR.                                         |
| `nb_accords`             | int   | creditor | creditor  | Total number of Club de Paris agreements.                                   |
| `statut`                 | str   | creditor | creditor  | `""` (permanent), `"Ad hoc"`, or `"Prospectif"`.                            |
| `premiere_participation` | int   | creditor | creditor  | Year of first Club de Paris participation.                                  |

### Example CSV

```csv
annee,pays,role,apd_meur,napd_meur,nb_accords,statut,premiere_participation
2024,Afghanistan,debtor,111,957,,,
2024,Argentine,debtor,0,1234.5,,,
2024,FRANCE,creditor,,,452,,1956
2024,Arabie Saoudite,creditor,,,3,Ad hoc,
```

### Notes on role detection

The legacy workbook `Club_de_Paris_Consolidé_2010-2024.xlsx` distinguished
creditors from debtors purely by letter case in the `pays` column. That
convention is still supported as a fallback when `role` is absent. **New CSV
sources should always include an explicit `role` column** — it is less
fragile (e.g. "EGYPTE" vs "Égypte") and readable by humans reviewing the
source file.

## 4. Output schema

```json
{
  "2024": {
    "countries": {
      "AFG": {
        "country": "Afghanistan",
        "debtor": {
          "apd": 111000000,
          "napd": 957000000,
          "total": 1068000000,
          "url": "https://clubdeparis.org/.../afghanistan.html"
        }
      },
      "FRA": {
        "country": "France",
        "creditor": {
          "nbAccords": 452,
          "statut": null,
          "premiereParticipation": 1956,
          "url": "https://clubdeparis.org/.../france.html"
        }
      }
    },
    "totals": {
      "debtorApd": 3456789000,
      "debtorNapd": 9876543210,
      "debtorTotal": 13333332210,
      "debtorCount": 42,
      "creditorCount": 22
    }
  }
}
```

- Amounts are in EUR (the source's M€ are multiplied by 1 000 000).
- A country can have both a `debtor` and a `creditor` block in the same year.
- `statut: null` means the creditor is a permanent member.
- `url` is `null` when no `url_slug_*` is defined for that country in
  `countries.yml`.

## 5. countries.yml

Source of truth for country ingestion and display. One entry per ISO-3 code:

```yaml
FRA:
  name_fr: 'France'
  name_en: 'France'
  aliases:
    - 'FRANCE'
    - 'France'
  url_slug_debtor: null
  url_slug_creditor: 'france'
```

When the pipeline reports an unmapped country, **do not** rewrite the source
file — add the variant to the `aliases:` list of the appropriate ISO entry
and re-run `build_data.py`. This keeps the source CSV/Excel readable for
non-technical contributors.

Matching is:

1. whitespace-collapsed (multiple spaces → single space, strip ends),
2. accent-insensitive,
3. case-insensitive.

So `"  CÔTE D'IVOIRE  "`, `"cote d'ivoire"`, and `"Côte d'Ivoire"` all
resolve to `CIV` provided any equivalent alias is declared.

## 6. Validation

`build_data.py` fails (exit code 1) on:

- unmapped country names,
- invalid year (not in 1900..2099),
- duplicate `(year, iso, role)` rows,
- negative `apd_meur` / `napd_meur`,
- CSV/Excel missing required columns.

It warns (non-fatal) on:

- unexpected `statut` values (not `""`, `"Ad hoc"`, `"Prospectif"`).

## 7. Smoke test against the legacy workbook

As long as `Club_de_Paris_Consolidé_2010-2024.xlsx` is placed in `sources/`,
the pipeline reproduces the live `data.json` byte-for-byte (up to JSON
formatting):

```
python build_data.py \
    --input sources/Club_de_Paris_Consolidé_2010-2024.xlsx \
    --sheet "Données consolidées" \
    --out ../data.json
```
