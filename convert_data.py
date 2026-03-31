#!/usr/bin/env python3
"""Convert Club_de_Paris_Consolidé_2010-2024.xlsx to data.json for the React app."""

import json
import unicodedata
import openpyxl

# Mapping from French country names (normalized) to ISO Alpha-3 codes
COUNTRY_TO_ISO = {
    # Debtors (Title case in Excel)
    'Afghanistan': 'AFG',
    'Albanie': 'ALB',
    'Algérie': 'DZA',
    'Angola': 'AGO',
    'Antigua-et-Barbuda': 'ATG',
    'Argentine': 'ARG',
    'Bolivie': 'BOL',
    'Bosnie-Herzégovine': 'BIH',
    'Brésil': 'BRA',
    'Bulgarie': 'BGR',
    'Burkina Faso': 'BFA',
    'BurkinaFaso': 'BFA',
    'Burundi': 'BDI',
    'Bénin': 'BEN',
    'Cambodge': 'KHM',
    'Cameroun': 'CMR',
    'Cap-Vert': 'CPV',
    'Chili': 'CHL',
    'Comores': 'COM',
    'Congo': 'COG',
    'Costa Rica': 'CRI',
    'CostaRica': 'CRI',
    'Croatie': 'HRV',
    "Côte d'Ivoire": 'CIV',
    "Côted'Ivoire": 'CIV',
    'Djibouti': 'DJI',
    'Dominique': 'DMA',
    'Egypte': 'EGY',
    'El Salvador': 'SLV',
    'ElSalvador': 'SLV',
    'Equateur': 'ECU',
    'Ethiopie': 'ETH',
    'Fédération de Russie': 'RUS',
    'Gabon': 'GAB',
    'Gambie': 'GMB',
    'Georgie': 'GEO',
    'Ghana': 'GHA',
    'Grenade': 'GRD',
    'Guatemala': 'GTM',
    'Guinée': 'GIN',
    'Guinée Equatoriale': 'GNQ',
    'Guinée-Bissau': 'GNB',
    'Guyana': 'GUY',
    'Haïti': 'HTI',
    'Honduras': 'HND',
    'Indonésie': 'IDN',
    'Irak': 'IRQ',
    'Jamaïque': 'JAM',
    'Jordanie': 'JOR',
    'Kenya': 'KEN',
    'Laos': 'LAO',
    'Liban': 'LBN',
    'Libéria': 'LBR',
    'Liberia': 'LBR',
    'Madagascar': 'MDG',
    'Malawi': 'MWI',
    'Mali': 'MLI',
    'Maroc': 'MAR',
    'Maurice': 'MUS',
    'Mauritanie': 'MRT',
    'Mexique': 'MEX',
    'Moldavie': 'MDA',
    'Mongolie': 'MNG',
    'Monténégro': 'MNE',
    'Montenegro': 'MNE',
    'Mozambique': 'MOZ',
    'Myanmar': 'MMR',
    'Nicaragua': 'NIC',
    'Niger': 'NER',
    'Nigéria': 'NGA',
    'Nigeria': 'NGA',
    'Ouganda': 'UGA',
    'Pakistan': 'PAK',
    'Panama': 'PAN',
    'Papouasie-Nouvelle-Guinée': 'PNG',
    'Paraguay': 'PRY',
    'Philippines': 'PHL',
    'Pologne': 'POL',
    'Pérou': 'PER',
    'Peru': 'PER',
    'RD Congo': 'COD',
    'RDCongo': 'COD',
    'République Centrafricaine': 'CAF',
    'RépubliqueCentrafricaine': 'CAF',
    'République Dominicaine': 'DOM',
    'RépubliqueDominicaine': 'DOM',
    'Rwanda': 'RWA',
    'Sainte Lucie': 'LCA',
    'SainteLucie': 'LCA',
    'Sao Tomé et Principe': 'STP',
    'SaoToméetPrincipe': 'STP',
    'Serbie': 'SRB',
    'Sierra Leone': 'SLE',
    'SierraLeone': 'SLE',
    'Somalie': 'SOM',
    'Soudan': 'SDN',
    'Sri Lanka': 'LKA',
    'SriLanka': 'LKA',
    'St Vincent': 'VCT',
    'StVincent': 'VCT',
    'Suriname': 'SUR',
    'Syrie': 'SYR',
    'Sénégal': 'SEN',
    'Senegal': 'SEN',
    'Tadjikistan': 'TJK',
    'Tanzanie': 'TZA',
    'Tchad': 'TCD',
    'Togo': 'TGO',
    'Trinité-et-Tobago': 'TTO',
    'Tunisie': 'TUN',
    'Turquie': 'TUR',
    'Ukraine': 'UKR',
    'Vietnam': 'VNM',
    'Yémen': 'YEM',
    'Yemen': 'YEM',
    'Zambie': 'ZMB',
    'Centrafrique': 'CAF',
    'Seychelles': 'SYC',
    'Slovénie': 'SVN',
    'Érythrée': 'ERI',
    'Erythrée': 'ERI',
    'Ethiopie': 'ETH',
    'Éthiopie': 'ETH',
    'Cuba': 'CUB',
    'Iran': 'IRN',
    'Corée du Nord': 'PRK',
    'CoréeduNord': 'PRK',
    'République dominicaine': 'DOM',
    'Kirghizie': 'KGZ',
    'Népal': 'NPL',
    'Saint-Vincent-et-les-Grenadines': 'VCT',
    'Saint-Vincent et les Grenadines': 'VCT',
    'République centrafriaine': 'CAF',
    'République centrafricaine': 'CAF',
    'Macédoine, ex-RépubliqueYougoslavede': 'MKD',
    'Macédoine, ex Yougoslavie': 'MKD',
    'Macédoine, ex République yougoslave de': 'MKD',
    'Géorgie': 'GEO',
    'Sao Tomé-et-Principe': 'STP',
    'SaoTomé-et-Principe': 'STP',
    'FédérationdeRussie': 'RUS',
    'République démocratique du Congo': 'COD',
    'Guinée équatoriale': 'GNQ',
    'Guinéeéquatoriale': 'GNQ',
    'Saint-Christophe-et-Niévès': 'KNA',
    'Saint-Christophe et Niévès': 'KNA',
    'Roumanie': 'ROU',
    'Sainte-Lucie': 'LCA',
    'Haiti': 'HTI',
    'Papouasie Nouvelle Guinée': 'PNG',
    'Fidji': 'FJI',
    'Samoa': 'WSM',
    'Maldives': 'MDV',
    'Lesotho': 'LSO',

    # ex-Yugoslavia variants (skip these or map to SRB)
    'ex Yougoslavie': None,
    'ex Yugoslavie': None,
    'ex-Yougoslavie': None,
    'exYougoslavie': None,

    # Creditors (UPPERCASE in Excel)
    'AFRIQUE DU SUD': 'ZAF',
    'ALLEMAGNE': 'DEU',
    'ARABIE SAOUDITE': 'SAU',
    'AUSTRALIE': 'AUS',
    'AUTRICHE': 'AUT',
    'BELGIQUE': 'BEL',
    'BRESIL': 'BRA',
    'CANADA': 'CAN',
    'CHINE': 'CHN',
    'DANEMARK': 'DNK',
    'EMIRATS ARABES UNIS': 'ARE',
    'ESPAGNE': 'ESP',
    "ETATS-UNIS D'AMERIQUE": 'USA',
    'FEDERATION DE RUSSIE': 'RUS',
    'FINLANDE': 'FIN',
    'FRANCE': 'FRA',
    'HONGRIE': 'HUN',
    'INDE': 'IND',
    'IRLANDE': 'IRL',
    'ISRAEL': 'ISR',
    'ITALIE': 'ITA',
    'JAPON': 'JPN',
    'KOWEIT': 'KWT',
    'NORVEGE': 'NOR',
    'NOUVELLE-ZELANDE': 'NZL',
    'PAYS-BAS': 'NLD',
    'PORTUGAL': 'PRT',
    'REPUBLIQUE DE COREE': 'KOR',
    'REPUBLIQUE TCHEQUE': 'CZE',
    'ROYAUME-UNI': 'GBR',
    'SUEDE': 'SWE',
    'SUISSE': 'CHE',
    'TRINITE & TOBAGGO': 'TTO',
}

# French display names for ISO codes
ISO_TO_NAME = {
    'AFG': 'Afghanistan', 'ALB': 'Albanie', 'DZA': 'Algérie', 'AGO': 'Angola',
    'ATG': 'Antigua-et-Barbuda', 'ARG': 'Argentine', 'AUS': 'Australie',
    'AUT': 'Autriche', 'AZE': 'Azerbaïdjan', 'BGD': 'Bangladesh',
    'BEL': 'Belgique', 'BEN': 'Bénin', 'BOL': 'Bolivie',
    'BIH': 'Bosnie-Herzégovine', 'BWA': 'Botswana', 'BRA': 'Brésil',
    'BFA': 'Burkina Faso', 'BDI': 'Burundi', 'KHM': 'Cambodge',
    'CMR': 'Cameroun', 'CAN': 'Canada', 'CPV': 'Cap-Vert',
    'CAF': 'Centrafrique', 'TCD': 'Tchad', 'CHL': 'Chili', 'CHN': 'Chine',
    'COL': 'Colombie', 'COM': 'Comores', 'COG': 'Congo', 'COD': 'RD Congo',
    'CRI': 'Costa Rica', 'CIV': "Côte d'Ivoire", 'HRV': 'Croatie',
    'CUB': 'Cuba', 'CZE': 'Rép. Tchèque', 'DNK': 'Danemark',
    'DJI': 'Djibouti', 'DMA': 'Dominique', 'DOM': 'Rép. Dominicaine',
    'ECU': 'Équateur', 'EGY': 'Égypte', 'SLV': 'El Salvador',
    'GNQ': 'Guinée Équatoriale', 'ERI': 'Érythrée', 'ETH': 'Éthiopie',
    'FIN': 'Finlande', 'FRA': 'France', 'GAB': 'Gabon', 'GMB': 'Gambie',
    'GEO': 'Géorgie', 'DEU': 'Allemagne', 'GHA': 'Ghana', 'GRC': 'Grèce',
    'GRD': 'Grenade', 'GTM': 'Guatemala', 'GIN': 'Guinée',
    'GNB': 'Guinée-Bissau', 'GUY': 'Guyana', 'HTI': 'Haïti',
    'HND': 'Honduras', 'HUN': 'Hongrie', 'IND': 'Inde', 'IDN': 'Indonésie',
    'IRN': 'Iran', 'IRQ': 'Irak', 'IRL': 'Irlande', 'ISR': 'Israël',
    'ITA': 'Italie', 'JAM': 'Jamaïque', 'JPN': 'Japon', 'JOR': 'Jordanie',
    'KAZ': 'Kazakhstan', 'KEN': 'Kenya', 'KOR': 'Corée du Sud',
    'KWT': 'Koweït', 'KGZ': 'Kirghizistan', 'LAO': 'Laos', 'LBN': 'Liban',
    'LSO': 'Lesotho', 'LBR': 'Liberia', 'LBY': 'Libye',
    'MKD': 'Macédoine du Nord', 'MDG': 'Madagascar', 'MWI': 'Malawi',
    'MYS': 'Malaisie', 'MDV': 'Maldives', 'MLI': 'Mali', 'MAR': 'Maroc',
    'MRT': 'Mauritanie', 'MUS': 'Maurice', 'MEX': 'Mexique',
    'MDA': 'Moldavie', 'MNG': 'Mongolie', 'MNE': 'Monténégro',
    'MOZ': 'Mozambique', 'MMR': 'Myanmar', 'NAM': 'Namibie', 'NPL': 'Népal',
    'NLD': 'Pays-Bas', 'NZL': 'Nouvelle-Zélande', 'NIC': 'Nicaragua',
    'NER': 'Niger', 'NGA': 'Nigeria', 'NOR': 'Norvège', 'OMN': 'Oman',
    'PAK': 'Pakistan', 'PAN': 'Panama', 'PNG': 'Papouasie-N.-Guinée',
    'PRY': 'Paraguay', 'PER': 'Pérou', 'PHL': 'Philippines',
    'POL': 'Pologne', 'PRT': 'Portugal', 'PRK': 'Corée du Nord',
    'QAT': 'Qatar', 'ROU': 'Roumanie', 'RUS': 'Russie', 'RWA': 'Rwanda',
    'SAU': 'Arabie Saoudite', 'SEN': 'Sénégal', 'SRB': 'Serbie',
    'SYC': 'Seychelles', 'SLE': 'Sierra Leone', 'SVN': 'Slovénie',
    'SOM': 'Somalie', 'ZAF': 'Afrique du Sud', 'ESP': 'Espagne',
    'LKA': 'Sri Lanka', 'LCA': 'Sainte-Lucie',
    'VCT': 'Saint-Vincent-et-les-Grenadines', 'SDN': 'Soudan',
    'SUR': 'Suriname', 'SWZ': 'Eswatini', 'SWE': 'Suède', 'CHE': 'Suisse',
    'SYR': 'Syrie', 'TJK': 'Tadjikistan', 'TZA': 'Tanzanie',
    'THA': 'Thaïlande', 'TGO': 'Togo', 'TTO': 'Trinité-et-Tobago',
    'TUN': 'Tunisie', 'TUR': 'Turquie', 'TKM': 'Turkménistan',
    'UGA': 'Ouganda', 'UKR': 'Ukraine', 'ARE': 'Émirats Arabes Unis',
    'GBR': 'Royaume-Uni', 'USA': 'États-Unis', 'URY': 'Uruguay',
    'UZB': 'Ouzbékistan', 'VEN': 'Venezuela', 'VNM': 'Vietnam',
    'YEM': 'Yémen', 'ZMB': 'Zambie', 'ZWE': 'Zimbabwe',
    'STP': 'Sao Tomé-et-Principe', 'BRB': 'Barbade',
    'SSD': 'Soudan du Sud', 'XKX': 'Kosovo',
    'KNA': 'Saint-Christophe-et-Niévès', 'FJI': 'Fidji', 'WSM': 'Samoa',
}


def slugify(name):
    """Convert a country name to a URL slug."""
    # Remove accents
    slug = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode()
    slug = slug.lower()
    # Replace special chars with hyphens
    slug = slug.replace("'", '-').replace(' ', '-').replace('&', '-')
    # Remove consecutive hyphens
    while '--' in slug:
        slug = slug.replace('--', '-')
    slug = slug.strip('-')
    return slug


# Custom URL slugs for countries that don't follow the simple pattern
DEBTOR_URL_SLUGS = {
    'DZA': 'algerie', 'AGO': 'angola', 'ARG': 'argentine', 'BEN': 'benin',
    'BOL': 'bolivie', 'BIH': 'bosnie-herzegovine', 'BRA': 'bresil',
    'BGR': 'bulgarie', 'BFA': 'burkina-faso', 'BDI': 'burundi',
    'KHM': 'cambodge', 'CMR': 'cameroun', 'CPV': 'cap-vert',
    'CAF': 'centrafrique', 'TCD': 'tchad', 'CHL': 'chili', 'COM': 'comores',
    'COG': 'congo', 'COD': 'rd-congo', 'CRI': 'costa-rica',
    'CIV': 'cote-d-ivoire', 'HRV': 'croatie', 'CUB': 'cuba',
    'DJI': 'djibouti', 'DMA': 'dominique', 'DOM': 'republique-dominicaine',
    'ECU': 'equateur', 'EGY': 'egypte', 'SLV': 'el-salvador',
    'GNQ': 'guinee-equatoriale', 'ERI': 'erythree', 'ETH': 'ethiopie',
    'GAB': 'gabon', 'GMB': 'gambie', 'GEO': 'georgie', 'GHA': 'ghana',
    'GRD': 'grenade', 'GTM': 'guatemala', 'GIN': 'guinee',
    'GNB': 'guinee-bissau', 'GUY': 'guyana', 'HTI': 'haiti',
    'HND': 'honduras', 'IDN': 'indonesie', 'IRQ': 'irak', 'IRN': 'iran',
    'JAM': 'jamaique', 'JOR': 'jordanie', 'KEN': 'kenya',
    'KGZ': 'kirghizistan', 'LAO': 'laos', 'LBN': 'liban', 'LBR': 'liberia',
    'LBY': 'libye', 'MKD': 'macedoine-du-nord', 'MDG': 'madagascar',
    'MWI': 'malawi', 'MLI': 'mali', 'MAR': 'maroc', 'MRT': 'mauritanie',
    'MUS': 'maurice', 'MEX': 'mexique', 'MDA': 'moldavie', 'MNG': 'mongolie',
    'MNE': 'montenegro', 'MOZ': 'mozambique', 'MMR': 'myanmar',
    'NIC': 'nicaragua', 'NER': 'niger', 'NGA': 'nigeria', 'PAK': 'pakistan',
    'PAN': 'panama', 'PNG': 'papouasie-nouvelle-guinee', 'PRY': 'paraguay',
    'PER': 'perou', 'PHL': 'philippines', 'POL': 'pologne',
    'RUS': 'federation-de-russie', 'RWA': 'rwanda',
    'LCA': 'sainte-lucie', 'VCT': 'st-vincent',
    'STP': 'sao-tome-et-principe', 'SEN': 'senegal', 'SRB': 'serbie',
    'SYC': 'seychelles', 'SLE': 'sierra-leone', 'SVN': 'slovenie',
    'SOM': 'somalie', 'SDN': 'soudan', 'LKA': 'sri-lanka',
    'SUR': 'suriname', 'SYR': 'syrie', 'TJK': 'tadjikistan',
    'TZA': 'tanzanie', 'TGO': 'togo', 'TTO': 'trinite-et-tobago',
    'TUN': 'tunisie', 'TUR': 'turquie', 'UKR': 'ukraine', 'UGA': 'ouganda',
    'VNM': 'vietnam', 'YEM': 'yemen', 'ZMB': 'zambie',
    'AFG': 'afghanistan', 'ALB': 'albanie', 'ATG': 'antigua-et-barbuda',
    'PRK': 'coree-du-nord', 'NPL': 'nepal', 'LSO': 'lesotho',
    'KNA': 'saint-christophe-et-nieves', 'FJI': 'fidji', 'WSM': 'samoa',
    'MDV': 'maldives', 'ROU': 'roumanie', 'KGZ': 'kirghizie',
    'BGR': 'bulgarie',
}

CREDITOR_URL_SLUGS = {
    'ZAF': 'afrique-du-sud', 'DEU': 'allemagne', 'SAU': 'arabie-saoudite',
    'AUS': 'australie', 'AUT': 'autriche', 'BEL': 'belgique', 'BRA': 'bresil',
    'CAN': 'canada', 'CHN': 'chine', 'DNK': 'danemark',
    'ARE': 'emirats-arabes-unis', 'ESP': 'espagne',
    'USA': 'etats-unis-d-amerique', 'RUS': 'federation-de-russie',
    'FIN': 'finlande', 'FRA': 'france', 'HUN': 'hongrie', 'IND': 'inde',
    'IRL': 'irlande', 'ISR': 'israel', 'ITA': 'italie', 'JPN': 'japon',
    'KWT': 'koweit', 'NOR': 'norvege', 'NZL': 'nouvelle-zelande',
    'NLD': 'pays-bas', 'PRT': 'portugal', 'KOR': 'republique-de-coree',
    'CZE': 'republique-tcheque', 'GBR': 'royaume-uni', 'SWE': 'suede',
    'CHE': 'suisse', 'TTO': 'trinite-tobaggo',
}


def get_debtor_url(iso):
    slug = DEBTOR_URL_SLUGS.get(iso)
    if slug:
        return f"https://clubdeparis.org/sites/clubdeparis/accueil/accords-signes-avec-le-club-de-p/par%20pays-debiteurs/{slug}.html"
    return None


def get_creditor_url(iso):
    slug = CREDITOR_URL_SLUGS.get(iso)
    if slug:
        return f"https://clubdeparis.org/sites/clubdeparis/accueil/accords-signes-avec-le-club-de-p/par-pays-crediteurs/{slug}.html"
    return None


def main():
    wb = openpyxl.load_workbook('Club_de_Paris_Consolidé_2010-2024.xlsx', read_only=True)
    ws = wb['Données consolidées']
    rows = list(ws.iter_rows(values_only=True))

    # Build data structure
    all_data = {}
    unmapped = set()

    for row in rows[1:]:
        year, pays, apd, napd, nb_accords, statut, premiere_part = row
        if pays is None:
            continue

        iso = COUNTRY_TO_ISO.get(pays)
        if iso is None and pays in COUNTRY_TO_ISO:
            continue  # Explicitly skipped (ex-Yugoslavia)
        if iso is None:
            unmapped.add(pays)
            continue

        year_str = str(year)
        if year_str not in all_data:
            all_data[year_str] = {}

        if iso not in all_data[year_str]:
            all_data[year_str][iso] = {
                'country': ISO_TO_NAME.get(iso, pays),
            }

        entry = all_data[year_str][iso]

        is_creditor = (pays == pays.upper())

        if is_creditor:
            entry['creditor'] = {
                'nbAccords': nb_accords or 0,
                'statut': statut,
                'premiereParticipation': int(premiere_part) if premiere_part else None,
                'url': get_creditor_url(iso),
            }
        else:
            # APD values are in M€ in the Excel, convert to euros
            apd_val = (apd or 0) * 1_000_000
            napd_val = (napd or 0) * 1_000_000
            entry['debtor'] = {
                'apd': round(apd_val, 2),
                'napd': round(napd_val, 2),
                'total': round(apd_val + napd_val, 2),
                'url': get_debtor_url(iso),
            }

    if unmapped:
        print(f"WARNING: Unmapped countries: {unmapped}")

    # Build final JSON with totals
    final = {}
    for year_str in sorted(all_data.keys()):
        countries = all_data[year_str]
        debtor_apd = 0
        debtor_napd = 0
        debtor_total = 0
        debtor_count = 0
        creditor_count = 0

        for iso, entry in countries.items():
            if 'debtor' in entry:
                debtor_apd += entry['debtor']['apd']
                debtor_napd += entry['debtor']['napd']
                debtor_total += entry['debtor']['total']
                debtor_count += 1
            if 'creditor' in entry:
                creditor_count += 1

        final[year_str] = {
            'countries': countries,
            'totals': {
                'debtorApd': round(debtor_apd, 2),
                'debtorNapd': round(debtor_napd, 2),
                'debtorTotal': round(debtor_total, 2),
                'debtorCount': debtor_count,
                'creditorCount': creditor_count,
            }
        }

    with open('app/public/data.json', 'w', encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"Generated data.json with {len(final)} years")
    for y in sorted(final.keys()):
        t = final[y]['totals']
        print(f"  {y}: {t['debtorCount']} debtors, {t['creditorCount']} creditors")


if __name__ == '__main__':
    main()
