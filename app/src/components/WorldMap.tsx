import { useState, memo } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';
import type { YearData, CountryData, FilterMode, DebtFilter } from '../types';

const geoUrl = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

// Mapping ISO numeric codes to ISO_A3 codes (used in our data)
const numericToAlpha3: Record<string, string> = {
  '004': 'AFG', '008': 'ALB', '012': 'DZA', '024': 'AGO', '028': 'ATG',
  '032': 'ARG', '036': 'AUS', '040': 'AUT', '051': 'ARM', '031': 'AZE',
  '050': 'BGD', '052': 'BRB', '056': 'BEL', '084': 'BLZ', '204': 'BEN',
  '068': 'BOL', '070': 'BIH', '072': 'BWA', '076': 'BRA', '096': 'BRN',
  '100': 'BGR', '854': 'BFA', '108': 'BDI', '116': 'KHM', '120': 'CMR',
  '124': 'CAN', '132': 'CPV', '140': 'CAF', '148': 'TCD', '152': 'CHL',
  '156': 'CHN', '170': 'COL', '174': 'COM', '178': 'COG', '180': 'COD',
  '188': 'CRI', '384': 'CIV', '191': 'HRV', '192': 'CUB', '196': 'CYP',
  '203': 'CZE', '208': 'DNK', '262': 'DJI', '212': 'DMA', '214': 'DOM',
  '218': 'ECU', '818': 'EGY', '222': 'SLV', '226': 'GNQ', '232': 'ERI',
  '233': 'EST', '231': 'ETH', '242': 'FJI', '246': 'FIN', '250': 'FRA',
  '266': 'GAB', '270': 'GMB', '268': 'GEO', '276': 'DEU', '288': 'GHA',
  '300': 'GRC', '308': 'GRD', '320': 'GTM', '324': 'GIN', '624': 'GNB',
  '328': 'GUY', '332': 'HTI', '340': 'HND', '348': 'HUN', '352': 'ISL',
  '356': 'IND', '360': 'IDN', '364': 'IRN', '368': 'IRQ', '372': 'IRL',
  '376': 'ISR', '380': 'ITA', '388': 'JAM', '392': 'JPN', '400': 'JOR',
  '398': 'KAZ', '404': 'KEN', '408': 'PRK', '410': 'KOR', '414': 'KWT',
  '417': 'KGZ', '418': 'LAO', '428': 'LVA', '422': 'LBN', '426': 'LSO',
  '430': 'LBR', '434': 'LBY', '440': 'LTU', '442': 'LUX', '807': 'MKD',
  '450': 'MDG', '454': 'MWI', '458': 'MYS', '462': 'MDV', '466': 'MLI',
  '470': 'MLT', '478': 'MRT', '480': 'MUS', '484': 'MEX', '498': 'MDA',
  '496': 'MNG', '499': 'MNE', '504': 'MAR', '508': 'MOZ', '104': 'MMR',
  '516': 'NAM', '524': 'NPL', '528': 'NLD', '554': 'NZL', '558': 'NIC',
  '562': 'NER', '566': 'NGA', '578': 'NOR', '512': 'OMN', '586': 'PAK',
  '591': 'PAN', '598': 'PNG', '600': 'PRY', '604': 'PER', '608': 'PHL',
  '616': 'POL', '620': 'PRT', '634': 'QAT', '642': 'ROU', '643': 'RUS',
  '646': 'RWA', '882': 'WSM', '678': 'STP', '682': 'SAU', '686': 'SEN',
  '688': 'SRB', '690': 'SYC', '694': 'SLE', '702': 'SGP', '703': 'SVK',
  '705': 'SVN', '090': 'SLB', '706': 'SOM', '710': 'ZAF', '728': 'SSD',
  '724': 'ESP', '144': 'LKA', '662': 'LCA', '670': 'VCT', '729': 'SDN',
  '740': 'SUR', '748': 'SWZ', '752': 'SWE', '756': 'CHE', '760': 'SYR',
  '762': 'TJK', '834': 'TZA', '764': 'THA', '768': 'TGO', '780': 'TTO',
  '788': 'TUN', '792': 'TUR', '795': 'TKM', '800': 'UGA', '804': 'UKR',
  '784': 'ARE', '826': 'GBR', '840': 'USA', '858': 'URY', '860': 'UZB',
  '862': 'VEN', '704': 'VNM', '887': 'YEM', '894': 'ZMB', '716': 'ZWE',
  '-99': 'XKX', '659': 'KNA',
};

// Country names in French
const countryNames: Record<string, string> = {
  'ZAF': 'Afrique du Sud', 'ALB': 'Albanie', 'DZA': 'Algérie', 'AGO': 'Angola',
  'ATG': 'Antigua-et-Barbuda', 'SAU': 'Arabie Saoudite', 'ARG': 'Argentine',
  'ARM': 'Arménie', 'AUS': 'Australie', 'AUT': 'Autriche',
  'AZE': 'Azerbaïdjan', 'BGD': 'Bangladesh', 'BEL': 'Belgique', 'BEN': 'Bénin',
  'BOL': 'Bolivie', 'BIH': 'Bosnie-Herzégovine', 'BWA': 'Botswana', 'BRA': 'Brésil',
  'BFA': 'Burkina Faso', 'BDI': 'Burundi', 'KHM': 'Cambodge', 'CMR': 'Cameroun',
  'CAN': 'Canada', 'CPV': 'Cap-Vert', 'CAF': 'Centrafrique', 'CHL': 'Chili',
  'CHN': 'Chine', 'COL': 'Colombie', 'COM': 'Comores', 'COG': 'Congo',
  'COD': 'RD Congo', 'PRK': 'Corée du Nord', 'KOR': 'Corée du Sud',
  'CRI': 'Costa Rica', 'CIV': "Côte d'Ivoire", 'HRV': 'Croatie', 'CUB': 'Cuba',
  'CZE': 'Rép. Tchèque', 'DNK': 'Danemark', 'DJI': 'Djibouti', 'DMA': 'Dominique',
  'DOM': 'Rép. Dominicaine', 'EGY': 'Égypte', 'SLV': 'El Salvador',
  'ARE': 'Émirats Arabes Unis', 'ECU': 'Équateur', 'ERI': 'Érythrée',
  'ESP': 'Espagne', 'ETH': 'Éthiopie', 'FJI': 'Fidji', 'FIN': 'Finlande',
  'FRA': 'France', 'GAB': 'Gabon', 'GMB': 'Gambie', 'GEO': 'Géorgie',
  'DEU': 'Allemagne', 'GHA': 'Ghana', 'GRC': 'Grèce', 'GRD': 'Grenade',
  'GTM': 'Guatemala', 'GIN': 'Guinée', 'GNB': 'Guinée-Bissau',
  'GNQ': 'Guinée Équatoriale', 'GUY': 'Guyana', 'HTI': 'Haïti',
  'HND': 'Honduras', 'HUN': 'Hongrie', 'IND': 'Inde', 'IDN': 'Indonésie',
  'IRQ': 'Irak', 'IRN': 'Iran', 'IRL': 'Irlande', 'ISR': 'Israël',
  'ITA': 'Italie', 'JAM': 'Jamaïque', 'JPN': 'Japon', 'JOR': 'Jordanie',
  'KAZ': 'Kazakhstan', 'KEN': 'Kenya', 'KGZ': 'Kirghizistan', 'KNA': 'Saint-Christophe-et-Niévès',
  'KWT': 'Koweït', 'LAO': 'Laos', 'LSO': 'Lesotho', 'LBN': 'Liban',
  'LBR': 'Liberia', 'LBY': 'Libye', 'MKD': 'Macédoine du Nord',
  'MDG': 'Madagascar', 'MYS': 'Malaisie', 'MWI': 'Malawi', 'MDV': 'Maldives',
  'MLI': 'Mali', 'MAR': 'Maroc', 'MUS': 'Maurice', 'MRT': 'Mauritanie',
  'MEX': 'Mexique', 'MDA': 'Moldavie', 'MNG': 'Mongolie', 'MNE': 'Monténégro',
  'MOZ': 'Mozambique', 'MMR': 'Myanmar', 'NAM': 'Namibie', 'NPL': 'Népal',
  'NLD': 'Pays-Bas', 'NZL': 'Nouvelle-Zélande', 'NIC': 'Nicaragua',
  'NER': 'Niger', 'NGA': 'Nigeria', 'NOR': 'Norvège', 'OMN': 'Oman',
  'UGA': 'Ouganda', 'UZB': 'Ouzbékistan', 'PAK': 'Pakistan', 'PAN': 'Panama',
  'PNG': 'Papouasie-N.-Guinée', 'PRY': 'Paraguay', 'PER': 'Pérou',
  'PHL': 'Philippines', 'POL': 'Pologne', 'PRT': 'Portugal',
  'ROU': 'Roumanie', 'RUS': 'Russie', 'RWA': 'Rwanda',
  'LCA': 'Sainte-Lucie', 'VCT': 'Saint-Vincent-et-les-Grenadines',
  'STP': 'Sao Tomé-et-Principe', 'SEN': 'Sénégal', 'SRB': 'Serbie',
  'SYC': 'Seychelles', 'SLE': 'Sierra Leone', 'SVN': 'Slovénie',
  'SOM': 'Somalie', 'SDN': 'Soudan', 'LKA': 'Sri Lanka', 'SUR': 'Suriname',
  'SWE': 'Suède', 'CHE': 'Suisse', 'SYR': 'Syrie', 'TJK': 'Tadjikistan',
  'TZA': 'Tanzanie', 'TCD': 'Tchad', 'THA': 'Thaïlande', 'TGO': 'Togo',
  'TTO': 'Trinité-et-Tobago', 'TUN': 'Tunisie', 'TKM': 'Turkménistan',
  'TUR': 'Turquie', 'UKR': 'Ukraine', 'GBR': 'Royaume-Uni',
  'USA': 'États-Unis', 'URY': 'Uruguay', 'VEN': 'Venezuela', 'VNM': 'Vietnam',
  'WSM': 'Samoa', 'YEM': 'Yémen', 'ZMB': 'Zambie', 'ZWE': 'Zimbabwe',
  'XKX': 'Kosovo',
};

interface WorldMapProps {
  data: YearData;
  selectedCountry: string | null;
  filterMode: FilterMode;
  debtFilter: DebtFilter;
  onCountrySelect: (isoCode: string | null, data: CountryData | null) => void;
}

const WorldMap = memo(({ data, selectedCountry, filterMode, debtFilter, onCountrySelect }: WorldMapProps) => {
  const [tooltipContent, setTooltipContent] = useState<string>('');
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  // Compute max values for color scales
  const debtorValues = Object.values(data.countries)
    .filter((c) => c.debtor)
    .map((c) => debtFilter === 'apd' ? c.debtor!.apd : c.debtor!.napd);
  const creditorValues = Object.values(data.countries)
    .filter((c) => c.creditor)
    .map((c) => c.creditor!.nbAccords);

  const maxDebtor = Math.max(...debtorValues, 1);
  const maxCreditor = Math.max(...creditorValues, 1);

  // Orange scale for debtors
  const debtorColorScale = scaleLinear<string>()
    .domain([0, maxDebtor / 4, maxDebtor / 2, maxDebtor])
    .range(['#fef3e2', '#fdba74', '#f97316', '#c2410c']);

  // Green scale for creditors
  const creditorColorScale = scaleLinear<string>()
    .domain([0, maxCreditor / 4, maxCreditor / 2, maxCreditor])
    .range(['#ecfdf5', '#6ee7b7', '#10b981', '#047857']);

  const getIsoAlpha3 = (geoId: string): string => {
    return numericToAlpha3[geoId] || geoId;
  };

  const getCountryColor = (geoId: string) => {
    const isoCode = getIsoAlpha3(geoId);
    const country = data.countries[isoCode];
    if (!country) return '#e5e7eb';

    const isDebtor = country.debtor && country.debtor.total > 0;
    const isCreditor = !!country.creditor;

    if (filterMode === 'créditeur') {
      if (!isCreditor) return '#e5e7eb';
      return creditorColorScale(country.creditor!.nbAccords);
    }

    if (filterMode === 'débiteur') {
      if (!isDebtor) return '#e5e7eb';
      const val = debtFilter === 'apd' ? country.debtor!.apd : country.debtor!.napd;
      if (val === 0) return '#e5e7eb';
      return debtorColorScale(val);
    }

    // Mode "all": show both
    if (isDebtor && isCreditor) {
      // Dual: use a blended indicator — show debtor color by default
      return debtorColorScale(country.debtor!.apd);
    }
    if (isCreditor) {
      return creditorColorScale(country.creditor!.nbAccords);
    }
    if (isDebtor) {
      return debtorColorScale(country.debtor!.apd);
    }
    return '#e5e7eb';
  };

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)} Md€`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)} M€`;
    return `${value.toLocaleString('fr-FR')} €`;
  };

  const handleMouseEnter = (geoId: string, geoName: string, event: React.MouseEvent) => {
    const isoCode = getIsoAlpha3(geoId);
    const country = data.countries[isoCode];
    const displayName = countryNames[isoCode] || geoName;

    if (!country) {
      setTooltipContent(`${displayName}: Pas de données`);
    } else {
      const parts = [displayName];
      if (country.debtor && country.debtor.total > 0) {
        parts.push(`Dette: ${formatCurrency(country.debtor.total)}`);
      }
      if (country.creditor) {
        parts.push(`Créditeur (${country.creditor.nbAccords} accords)`);
      }
      setTooltipContent(parts.join(' — '));
    }
    setTooltipPosition({ x: event.clientX, y: event.clientY });
  };

  const handleMouseLeave = () => {
    setTooltipContent('');
  };

  const handleClick = (geoId: string) => {
    const isoCode = getIsoAlpha3(geoId);
    const countryData = data.countries[isoCode];
    if (countryData) {
      const enrichedData = {
        ...countryData,
        country: countryNames[isoCode] || countryData.country,
      };
      onCountrySelect(isoCode, enrichedData);
    } else {
      onCountrySelect(null, null);
    }
  };

  return (
    <div className="map-container">
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          scale: 130,
          center: [10, 20],
        }}
        style={{ width: '100%', height: '100%' }}
      >
        <ZoomableGroup>
          <Geographies geography={geoUrl}>
            {({ geographies }: { geographies: Array<{ rsmKey: string; id: string; properties: { name: string } }> }) =>
              geographies.map((geo) => {
                const geoId = geo.id;
                const isoCode = getIsoAlpha3(geoId);
                const isSelected = selectedCountry === isoCode;
                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={getCountryColor(geoId)}
                    stroke={isSelected ? '#1e40af' : '#fff'}
                    strokeWidth={isSelected ? 2 : 0.5}
                    style={{
                      default: { outline: 'none' },
                      hover: {
                        fill: '#3b82f6',
                        outline: 'none',
                        cursor: 'pointer',
                      },
                      pressed: { outline: 'none' },
                    }}
                    onMouseEnter={(event: React.MouseEvent) =>
                      handleMouseEnter(geoId, geo.properties.name, event)
                    }
                    onMouseLeave={handleMouseLeave}
                    onClick={() => handleClick(geoId)}
                  />
                );
              })
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>

      {tooltipContent && (
        <div
          className="tooltip"
          style={{
            left: tooltipPosition.x + 10,
            top: tooltipPosition.y - 30,
          }}
        >
          {tooltipContent}
        </div>
      )}

      <div className="map-legend">
        {(filterMode === 'all' || filterMode === 'débiteur') && (
          <div className="legend-section">
            <div className="legend-title">Débiteurs ({debtFilter === 'apd' ? 'APD' : 'Hors APD'})</div>
            <div
              className="gradient-bar"
              style={{
                background: 'linear-gradient(to right, #fef3e2, #fdba74, #f97316, #c2410c)',
              }}
            />
            <div className="legend-labels">
              <span>0</span>
              <span>{formatCurrency(maxDebtor)}</span>
            </div>
          </div>
        )}
        {(filterMode === 'all' || filterMode === 'créditeur') && (
          <div className="legend-section">
            <div className="legend-title">Créditeurs (nb accords)</div>
            <div
              className="gradient-bar"
              style={{
                background: 'linear-gradient(to right, #ecfdf5, #6ee7b7, #10b981, #047857)',
              }}
            />
            <div className="legend-labels">
              <span>0</span>
              <span>{maxCreditor}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

WorldMap.displayName = 'WorldMap';

export default WorldMap;
