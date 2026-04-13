#!/usr/bin/env python3
"""Build data.json for the Club de Paris map from a CSV or Excel source.

Input (one row per country-year-role):
    annee                   int   Year.
    pays                    str   Country name as it appears in the source.
    role                    str   "debtor" or "creditor". Optional; if absent,
                                  UPPERCASE pays is treated as creditor,
                                  Title-case pays as debtor (legacy convention).
    apd_meur                float APD in millions of EUR (debtor rows only).
    napd_meur               float Non-APD in millions of EUR (debtor rows only).
    nb_accords              int   Number of Club de Paris agreements (creditor).
    statut                  str   "", "Ad hoc", or "Prospectif" (creditor).
    premiere_participation  int   Year of first participation (creditor).

Country name is resolved to ISO-3 via data-pipeline/countries.yml aliases.
URL slugs for clubdeparis.org are taken from the same file.

Output:
    app/public/data.json-shaped JSON (keyed by year string), written to
    the path given by --out (defaults to ../data.json, i.e. repo root).

Usage:
    python build_data.py --input sources/club_paris_2010_2024.xlsx
    python build_data.py --input sources/club_paris_2010_2024.csv --out ../data.json
    python build_data.py --input ... --sheet "Données consolidées"
    python build_data.py --check            # validate countries.yml only
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_COUNTRIES_YML = HERE / "countries.yml"
DEFAULT_OUT = HERE.parent / "data.json"

DEBTOR_URL_TMPL = (
    "https://clubdeparis.org/sites/clubdeparis/accueil/"
    "accords-signes-avec-le-club-de-p/par%20pays-debiteurs/{slug}.html"
)
CREDITOR_URL_TMPL = (
    "https://clubdeparis.org/sites/clubdeparis/accueil/"
    "accords-signes-avec-le-club-de-p/par-pays-crediteurs/{slug}.html"
)

VALID_STATUTS = {"", "Ad hoc", "Prospectif"}
REQUIRED_COLUMNS = {"annee", "pays"}


# ---------------------------------------------------------------------------
# Country registry
# ---------------------------------------------------------------------------


@dataclass
class CountryEntry:
    iso: str
    name_fr: str
    name_en: str
    url_slug_debtor: str | None
    url_slug_creditor: str | None


class CountryRegistry:
    """Maps raw source strings to ISO-3 via aliases in countries.yml."""

    def __init__(self, entries: dict[str, CountryEntry]):
        self.entries = entries
        self._alias_index: dict[str, str] = {}
        for iso, entry in entries.items():
            for alias in self._aliases_for(iso, entry):
                key = self._normalize(alias)
                existing = self._alias_index.get(key)
                if existing and existing != iso:
                    raise ValueError(
                        f"countries.yml: alias '{alias}' maps to both "
                        f"{existing} and {iso}"
                    )
                self._alias_index[key] = iso

    @staticmethod
    def _aliases_for(iso: str, entry: CountryEntry) -> Iterable[str]:
        yield iso
        yield entry.name_fr
        yield entry.name_en
        yield entry.name_fr.upper()

    @staticmethod
    def _normalize(s: str) -> str:
        # Collapse whitespace, strip, lowercase, drop accents.
        s = s.strip()
        s = re.sub(r"\s+", " ", s)
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.lower()

    def resolve(self, raw: str) -> str | None:
        if raw is None:
            return None
        return self._alias_index.get(self._normalize(str(raw)))

    def __contains__(self, iso: str) -> bool:
        return iso in self.entries

    def __getitem__(self, iso: str) -> CountryEntry:
        return self.entries[iso]


def load_country_registry(path: Path) -> CountryRegistry:
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    entries: dict[str, CountryEntry] = {}
    for iso, obj in raw.items():
        if not isinstance(iso, str) or not re.fullmatch(r"[A-Z]{3}", iso):
            raise ValueError(f"countries.yml: invalid ISO key '{iso}'")
        if not isinstance(obj, dict):
            raise ValueError(f"countries.yml: {iso} must be a mapping")
        name_fr = obj.get("name_fr")
        name_en = obj.get("name_en") or name_fr
        if not name_fr:
            raise ValueError(f"countries.yml: {iso} missing name_fr")
        aliases = obj.get("aliases") or []
        if not isinstance(aliases, list):
            raise ValueError(f"countries.yml: {iso}.aliases must be a list")
        entry = CountryEntry(
            iso=iso,
            name_fr=str(name_fr),
            name_en=str(name_en),
            url_slug_debtor=obj.get("url_slug_debtor") or None,
            url_slug_creditor=obj.get("url_slug_creditor") or None,
        )
        entries[iso] = entry
        # Inject YAML-provided aliases into the index after construction.
        entry._extra_aliases = [str(a) for a in aliases]  # type: ignore[attr-defined]
    registry = CountryRegistry(entries)
    # Second pass: add the aliases from the YAML file itself.
    for iso, entry in entries.items():
        for alias in getattr(entry, "_extra_aliases", []):
            key = CountryRegistry._normalize(alias)
            existing = registry._alias_index.get(key)
            if existing and existing != iso:
                raise ValueError(
                    f"countries.yml: alias '{alias}' (under {iso}) already "
                    f"resolves to {existing}"
                )
            registry._alias_index[key] = iso
    return registry


# ---------------------------------------------------------------------------
# Source row ingestion
# ---------------------------------------------------------------------------


@dataclass
class SourceRow:
    annee: int
    pays: str
    role: str | None  # "debtor", "creditor", or None (infer from case)
    apd_meur: float | None
    napd_meur: float | None
    nb_accords: int | None
    statut: str
    premiere_participation: int | None
    source_lineno: int


def _to_int(v: Any) -> int | None:
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        raise ValueError("bool not allowed")
    return int(float(v))


def _to_float(v: Any) -> float | None:
    if v is None or v == "":
        return None
    return float(v)


def _to_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def read_csv_rows(path: Path) -> Iterator[SourceRow]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV missing required columns: {sorted(missing)}")
        for i, row in enumerate(reader, start=2):
            yield SourceRow(
                annee=_to_int(row.get("annee")) or 0,
                pays=_to_str(row.get("pays")),
                role=(_to_str(row.get("role")) or None),
                apd_meur=_to_float(row.get("apd_meur")),
                napd_meur=_to_float(row.get("napd_meur")),
                nb_accords=_to_int(row.get("nb_accords")),
                statut=_to_str(row.get("statut")),
                premiere_participation=_to_int(row.get("premiere_participation")),
                source_lineno=i,
            )


def read_excel_rows(path: Path, sheet: str | None) -> Iterator[SourceRow]:
    try:
        import openpyxl
    except ImportError as exc:
        raise SystemExit(
            "Excel input requires 'openpyxl'. Install with: "
            "pip install -r data-pipeline/requirements.txt"
        ) from exc

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet] if sheet else wb.active
    rows_iter = ws.iter_rows(values_only=True)
    header = next(rows_iter, None)
    if header is None:
        return
    cols = [str(c).strip() if c is not None else "" for c in header]

    # Accept both the canonical schema (annee/pays/...) and the legacy
    # 2010-2024 workbook (année/pays/apd/napd/...). Normalize to canonical.
    legacy_map = {
        "année": "annee",
        "annee": "annee",
        "pays": "pays",
        "role": "role",
        "rôle": "role",
        "apd": "apd_meur",
        "apd_meur": "apd_meur",
        "apd (m€)": "apd_meur",
        "napd": "napd_meur",
        "napd_meur": "napd_meur",
        "napd (m€)": "napd_meur",
        "nb_accords": "nb_accords",
        "nombre d'accords": "nb_accords",
        "nombre daccords": "nb_accords",
        "statut": "statut",
        "premiere_participation": "premiere_participation",
        "première participation": "premiere_participation",
        "premiere participation": "premiere_participation",
    }
    normalized = [legacy_map.get(c.lower().strip(), c) for c in cols]

    missing = REQUIRED_COLUMNS - set(normalized)
    if missing:
        raise ValueError(
            f"Excel sheet '{sheet or ws.title}' missing required columns: "
            f"{sorted(missing)} (found: {cols})"
        )

    def col(row: tuple, name: str) -> Any:
        if name in normalized:
            return row[normalized.index(name)]
        return None

    for lineno, row in enumerate(rows_iter, start=2):
        if row is None or all(c is None for c in row):
            continue
        yield SourceRow(
            annee=_to_int(col(row, "annee")) or 0,
            pays=_to_str(col(row, "pays")),
            role=(_to_str(col(row, "role")) or None),
            apd_meur=_to_float(col(row, "apd_meur")),
            napd_meur=_to_float(col(row, "napd_meur")),
            nb_accords=_to_int(col(row, "nb_accords")),
            statut=_to_str(col(row, "statut")),
            premiere_participation=_to_int(col(row, "premiere_participation")),
            source_lineno=lineno,
        )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


@dataclass
class BuildErrors:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unmapped_countries: set[str] = field(default_factory=set)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def fail_if_errors(self) -> None:
        if self.errors:
            for e in self.errors:
                print(f"ERROR: {e}", file=sys.stderr)
            if self.unmapped_countries:
                print(
                    "ERROR: unmapped countries (add them to countries.yml "
                    "aliases):",
                    file=sys.stderr,
                )
                for c in sorted(self.unmapped_countries):
                    print(f"  - {c!r}", file=sys.stderr)
            raise SystemExit(1)


def infer_role(pays: str) -> str:
    """Fallback when the source has no explicit 'role' column.

    Matches the legacy 2010-2024 workbook convention: creditors are written
    in UPPERCASE, debtors in Title Case.
    """
    letters = [c for c in pays if c.isalpha()]
    if not letters:
        return "debtor"
    return "creditor" if all(c.isupper() for c in letters) else "debtor"


def build(
    rows: Iterable[SourceRow],
    registry: CountryRegistry,
) -> tuple[dict[str, Any], BuildErrors]:
    errors = BuildErrors()
    per_year: dict[int, dict[str, dict[str, Any]]] = {}
    seen_keys: set[tuple[int, str, str]] = set()

    for row in rows:
        loc = f"line {row.source_lineno}"
        if not row.pays:
            continue
        if not (1900 < row.annee < 2100):
            errors.error(f"{loc}: invalid year {row.annee!r}")
            continue

        iso = registry.resolve(row.pays)
        if iso is None:
            errors.unmapped_countries.add(row.pays)
            continue

        role = row.role or infer_role(row.pays)
        if role not in ("debtor", "creditor"):
            errors.error(f"{loc}: invalid role {role!r}")
            continue

        key = (row.annee, iso, role)
        if key in seen_keys:
            errors.error(
                f"{loc}: duplicate row for ({row.annee}, {iso}, {role})"
            )
            continue
        seen_keys.add(key)

        country_entry = registry[iso]
        year_bucket = per_year.setdefault(row.annee, {})
        entry = year_bucket.setdefault(iso, {"country": country_entry.name_fr})

        if role == "debtor":
            apd = (row.apd_meur or 0) * 1_000_000
            napd = (row.napd_meur or 0) * 1_000_000
            if apd < 0 or napd < 0:
                errors.error(f"{loc}: negative APD/NAPD for {iso}")
                continue
            slug = country_entry.url_slug_debtor
            entry["debtor"] = {
                "apd": round(apd, 2),
                "napd": round(napd, 2),
                "total": round(apd + napd, 2),
                "url": DEBTOR_URL_TMPL.format(slug=slug) if slug else None,
            }
        else:  # creditor
            statut = row.statut or ""
            if statut not in VALID_STATUTS:
                errors.warn(
                    f"{loc}: unknown statut {statut!r} for {iso} "
                    "(expected '', 'Ad hoc', or 'Prospectif')"
                )
            slug = country_entry.url_slug_creditor
            entry["creditor"] = {
                "nbAccords": row.nb_accords or 0,
                "statut": statut or None,
                "premiereParticipation": row.premiere_participation,
                "url": CREDITOR_URL_TMPL.format(slug=slug) if slug else None,
            }

    final: dict[str, Any] = {}
    for year in sorted(per_year.keys()):
        countries = per_year[year]
        debtor_apd = debtor_napd = debtor_total = 0.0
        debtor_count = creditor_count = 0
        for country in countries.values():
            if "debtor" in country:
                debtor_apd += country["debtor"]["apd"]
                debtor_napd += country["debtor"]["napd"]
                debtor_total += country["debtor"]["total"]
                debtor_count += 1
            if "creditor" in country:
                creditor_count += 1
        final[str(year)] = {
            "countries": countries,
            "totals": {
                "debtorApd": round(debtor_apd, 2),
                "debtorNapd": round(debtor_napd, 2),
                "debtorTotal": round(debtor_total, 2),
                "debtorCount": debtor_count,
                "creditorCount": creditor_count,
            },
        }
    return final, errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, help="CSV or XLSX source file")
    ap.add_argument("--sheet", type=str, default=None, help="Excel sheet name")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output data.json path")
    ap.add_argument("--countries", type=Path, default=DEFAULT_COUNTRIES_YML)
    ap.add_argument("--check", action="store_true", help="Only validate countries.yml and exit")
    args = ap.parse_args()

    try:
        registry = load_country_registry(args.countries)
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Loaded {len(registry.entries)} countries from {args.countries}")

    if args.check:
        return 0

    if args.input is None:
        ap.error("--input is required unless --check is used")

    suffix = args.input.suffix.lower()
    if suffix in (".xlsx", ".xlsm"):
        rows = list(read_excel_rows(args.input, args.sheet))
    elif suffix == ".csv":
        rows = list(read_csv_rows(args.input))
    else:
        print(f"ERROR: unsupported input extension {suffix!r}", file=sys.stderr)
        return 1

    print(f"Read {len(rows)} rows from {args.input}")
    data, errors = build(rows, registry)

    for w in errors.warnings:
        print(f"WARN:  {w}", file=sys.stderr)
    errors.fail_if_errors()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    years = sorted(data.keys())
    print(f"Wrote {args.out} — {len(years)} years ({years[0]}..{years[-1]})")
    for y in years:
        t = data[y]["totals"]
        print(
            f"  {y}: {t['debtorCount']:>3} debtors, "
            f"{t['creditorCount']:>3} creditors, "
            f"total {t['debtorTotal']/1e9:>6.1f} G€"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
