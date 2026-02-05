import { useState, useEffect } from 'react';
import WorldMap from './components/WorldMap';
import CountryPanel from './components/CountryPanel';
import YearSlider from './components/YearSlider';
import KPIBar from './components/KPIBar';
import type { AllData, CountryData } from './types';
import './App.css';

const YEARS = [2020, 2021, 2022, 2023, 2024];

function App() {
  const [data, setData] = useState<AllData | null>(null);
  const [selectedYear, setSelectedYear] = useState(2024);
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null);
  const [selectedCountryData, setSelectedCountryData] = useState<CountryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(import.meta.env.BASE_URL + 'data.json')
      .then((res) => {
        if (!res.ok) throw new Error('Erreur de chargement des données');
        return res.json();
      })
      .then((json: AllData) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Update country data when year changes
  useEffect(() => {
    if (data && selectedCountry) {
      const yearData = data[selectedYear.toString()];
      const countryData = yearData?.countries[selectedCountry];
      if (countryData) {
        setSelectedCountryData(countryData);
      }
    }
  }, [selectedYear, data, selectedCountry]);

  const handleCountrySelect = (isoCode: string | null, countryData: CountryData | null) => {
    setSelectedCountry(isoCode);
    setSelectedCountryData(countryData);
  };

  const handleClosePanel = () => {
    setSelectedCountry(null);
    setSelectedCountryData(null);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Chargement des données...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="error">
        <p>Erreur: {error || 'Données non disponibles'}</p>
      </div>
    );
  }

  const yearData = data[selectedYear.toString()];

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>Carte des créances françaises</h1>
          <p className="subtitle">
            Encours des créances APD et Non APD de la France sur les États étrangers
          </p>
        </div>
      </header>

      <main className="main">
        <div className="map-section">
          <WorldMap
            data={yearData}
            selectedCountry={selectedCountry}
            onCountrySelect={handleCountrySelect}
          />
          <CountryPanel
            countryCode={selectedCountry}
            countryData={selectedCountryData}
            year={selectedYear}
            onClose={handleClosePanel}
          />
        </div>

        <YearSlider
          years={YEARS}
          selectedYear={selectedYear}
          onYearChange={setSelectedYear}
        />

        <KPIBar totals={yearData.totals} year={selectedYear} />
      </main>

      <footer className="footer">
        <p>
          Données: Encours de créances de la France sur les États étrangers (hors intérêts de retard) •
          Source: Direction Générale du Trésor
        </p>
      </footer>
    </div>
  );
}

export default App;
