import { useState, useRef, useEffect } from 'react';
import type { YearData, CountryData } from '../types';

// Country names in French with ISO codes
const countryList: Array<{ iso: string; name: string }> = [
  { iso: 'ZAF', name: 'Afrique du Sud' }, { iso: 'ALB', name: 'Albanie' },
  { iso: 'DZA', name: 'Algérie' }, { iso: 'AGO', name: 'Angola' },
  { iso: 'ATG', name: 'Antigua-et-Barbuda' }, { iso: 'SAU', name: 'Arabie Saoudite' },
  { iso: 'ARG', name: 'Argentine' }, { iso: 'ARM', name: 'Arménie' },
  { iso: 'AZE', name: 'Azerbaïdjan' }, { iso: 'BGD', name: 'Bangladesh' },
  { iso: 'BEN', name: 'Bénin' }, { iso: 'BOL', name: 'Bolivie' },
  { iso: 'BIH', name: 'Bosnie-Herzégovine' }, { iso: 'BWA', name: 'Botswana' },
  { iso: 'BRA', name: 'Brésil' }, { iso: 'BFA', name: 'Burkina Faso' },
  { iso: 'BDI', name: 'Burundi' }, { iso: 'KHM', name: 'Cambodge' },
  { iso: 'CMR', name: 'Cameroun' }, { iso: 'CPV', name: 'Cap-Vert' },
  { iso: 'CAF', name: 'Centrafrique' }, { iso: 'CHL', name: 'Chili' },
  { iso: 'CHN', name: 'Chine' }, { iso: 'COL', name: 'Colombie' },
  { iso: 'COM', name: 'Comores' }, { iso: 'COG', name: 'Congo' },
  { iso: 'COD', name: 'RD Congo' }, { iso: 'PRK', name: 'Corée du Nord' },
  { iso: 'KOR', name: 'Corée du Sud' }, { iso: 'CRI', name: 'Costa Rica' },
  { iso: 'CIV', name: "Côte d'Ivoire" }, { iso: 'HRV', name: 'Croatie' },
  { iso: 'CUB', name: 'Cuba' }, { iso: 'DJI', name: 'Djibouti' },
  { iso: 'DMA', name: 'Dominique' }, { iso: 'EGY', name: 'Égypte' },
  { iso: 'SLV', name: 'El Salvador' }, { iso: 'ARE', name: 'Émirats Arabes Unis' },
  { iso: 'ECU', name: 'Équateur' }, { iso: 'ERI', name: 'Érythrée' },
  { iso: 'ETH', name: 'Éthiopie' }, { iso: 'GAB', name: 'Gabon' },
  { iso: 'GMB', name: 'Gambie' }, { iso: 'GEO', name: 'Géorgie' },
  { iso: 'GHA', name: 'Ghana' }, { iso: 'GRC', name: 'Grèce' },
  { iso: 'GRD', name: 'Grenade' }, { iso: 'GTM', name: 'Guatemala' },
  { iso: 'GIN', name: 'Guinée' }, { iso: 'GNB', name: 'Guinée-Bissau' },
  { iso: 'GNQ', name: 'Guinée Équatoriale' }, { iso: 'GUY', name: 'Guyana' },
  { iso: 'HTI', name: 'Haïti' }, { iso: 'HND', name: 'Honduras' },
  { iso: 'IND', name: 'Inde' }, { iso: 'IDN', name: 'Indonésie' },
  { iso: 'IRQ', name: 'Irak' }, { iso: 'IRN', name: 'Iran' },
  { iso: 'JAM', name: 'Jamaïque' }, { iso: 'JOR', name: 'Jordanie' },
  { iso: 'KAZ', name: 'Kazakhstan' }, { iso: 'KEN', name: 'Kenya' },
  { iso: 'KGZ', name: 'Kirghizistan' }, { iso: 'KWT', name: 'Koweït' },
  { iso: 'LAO', name: 'Laos' }, { iso: 'LSO', name: 'Lesotho' },
  { iso: 'LBN', name: 'Liban' }, { iso: 'LBR', name: 'Liberia' },
  { iso: 'LBY', name: 'Libye' }, { iso: 'MKD', name: 'Macédoine du Nord' },
  { iso: 'MDG', name: 'Madagascar' }, { iso: 'MYS', name: 'Malaisie' },
  { iso: 'MWI', name: 'Malawi' }, { iso: 'MDV', name: 'Maldives' },
  { iso: 'MLI', name: 'Mali' }, { iso: 'MAR', name: 'Maroc' },
  { iso: 'MUS', name: 'Maurice' }, { iso: 'MRT', name: 'Mauritanie' },
  { iso: 'MEX', name: 'Mexique' }, { iso: 'MDA', name: 'Moldavie' },
  { iso: 'MNG', name: 'Mongolie' }, { iso: 'MNE', name: 'Monténégro' },
  { iso: 'MOZ', name: 'Mozambique' }, { iso: 'MMR', name: 'Myanmar' },
  { iso: 'NAM', name: 'Namibie' }, { iso: 'NPL', name: 'Népal' },
  { iso: 'NIC', name: 'Nicaragua' }, { iso: 'NER', name: 'Niger' },
  { iso: 'NGA', name: 'Nigeria' }, { iso: 'OMN', name: 'Oman' },
  { iso: 'UGA', name: 'Ouganda' }, { iso: 'UZB', name: 'Ouzbékistan' },
  { iso: 'PAK', name: 'Pakistan' }, { iso: 'PAN', name: 'Panama' },
  { iso: 'PNG', name: 'Papouasie-Nouvelle-Guinée' }, { iso: 'PRY', name: 'Paraguay' },
  { iso: 'PER', name: 'Pérou' }, { iso: 'PHL', name: 'Philippines' },
  { iso: 'POL', name: 'Pologne' }, { iso: 'DOM', name: 'République Dominicaine' },
  { iso: 'ROU', name: 'Roumanie' }, { iso: 'RUS', name: 'Russie' },
  { iso: 'RWA', name: 'Rwanda' }, { iso: 'LCA', name: 'Sainte-Lucie' },
  { iso: 'VCT', name: 'Saint-Vincent-et-les-Grenadines' },
  { iso: 'STP', name: 'Sao Tomé-et-Principe' }, { iso: 'SEN', name: 'Sénégal' },
  { iso: 'SRB', name: 'Serbie' }, { iso: 'SYC', name: 'Seychelles' },
  { iso: 'SLE', name: 'Sierra Leone' }, { iso: 'SVN', name: 'Slovénie' },
  { iso: 'SOM', name: 'Somalie' }, { iso: 'SDN', name: 'Soudan' },
  { iso: 'LKA', name: 'Sri Lanka' }, { iso: 'SUR', name: 'Suriname' },
  { iso: 'SYR', name: 'Syrie' }, { iso: 'TJK', name: 'Tadjikistan' },
  { iso: 'TZA', name: 'Tanzanie' }, { iso: 'TCD', name: 'Tchad' },
  { iso: 'THA', name: 'Thaïlande' }, { iso: 'TGO', name: 'Togo' },
  { iso: 'TTO', name: 'Trinité-et-Tobago' }, { iso: 'TUN', name: 'Tunisie' },
  { iso: 'TKM', name: 'Turkménistan' }, { iso: 'TUR', name: 'Turquie' },
  { iso: 'UKR', name: 'Ukraine' }, { iso: 'URY', name: 'Uruguay' },
  { iso: 'VEN', name: 'Venezuela' }, { iso: 'VNM', name: 'Vietnam' },
  { iso: 'YEM', name: 'Yémen' }, { iso: 'ZMB', name: 'Zambie' },
  { iso: 'ZWE', name: 'Zimbabwe' }, { iso: 'XKX', name: 'Kosovo' },
];

interface CountrySearchProps {
  data: YearData;
  onSelect: (iso: string, countryData: CountryData) => void;
}

const CountrySearch = ({ data, onSelect }: CountrySearchProps) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<typeof countryList>([]);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (value: string) => {
    setQuery(value);
    if (value.length > 0) {
      const filtered = countryList
        .filter((c) =>
          c.name.toLowerCase().includes(value.toLowerCase()) &&
          data.countries[c.iso]
        )
        .slice(0, 6);
      setSuggestions(filtered);
      setIsOpen(true);
    } else {
      setSuggestions([]);
      setIsOpen(false);
    }
  };

  const handleSelect = (country: typeof countryList[0]) => {
    const countryData = data.countries[country.iso];
    if (countryData) {
      onSelect(country.iso, { ...countryData, country: country.name });
      setQuery('');
      setIsOpen(false);
    }
  };

  return (
    <div className="country-search" ref={wrapperRef}>
      <div className="search-input-wrapper">
        <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="text"
          className="search-input"
          placeholder="Rechercher un pays..."
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
          onFocus={() => query.length > 0 && setIsOpen(true)}
        />
      </div>
      {isOpen && suggestions.length > 0 && (
        <ul className="search-suggestions">
          {suggestions.map((country) => (
            <li
              key={country.iso}
              className="search-suggestion"
              onClick={() => handleSelect(country)}
            >
              {country.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CountrySearch;
