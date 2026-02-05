import type { CountryData } from '../types';

interface CountryPanelProps {
  countryCode: string | null;
  countryData: CountryData | null;
  year: number;
  onClose: () => void;
}

const formatCurrency = (value: number) => {
  if (value >= 1e9) {
    return `${(value / 1e9).toFixed(2)} Md€`;
  }
  if (value >= 1e6) {
    return `${(value / 1e6).toFixed(1)} M€`;
  }
  if (value === 0) {
    return '0 €';
  }
  return `${value.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} €`;
};

const CountryPanel = ({
  countryCode,
  countryData,
  year,
  onClose,
}: CountryPanelProps) => {
  if (!countryCode || !countryData) {
    return (
      <div className="country-panel empty">
        <div className="panel-content">
          <h3>Sélectionnez un pays</h3>
          <p>Cliquez sur un pays sur la carte pour voir les détails de ses créances.</p>
        </div>
      </div>
    );
  }

  const apdPercent = countryData.total > 0
    ? ((countryData.apd / countryData.total) * 100).toFixed(1)
    : 0;
  const napdPercent = countryData.total > 0
    ? ((countryData.napd / countryData.total) * 100).toFixed(1)
    : 0;

  return (
    <div className="country-panel">
      <button className="close-button" onClick={onClose}>
        ×
      </button>

      <div className="panel-header">
        <h2>{countryData.country}</h2>
        <p className="subtitle">Encours des créances</p>
      </div>

      <div className="panel-content">
        <div className="stat-item apd">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <div className="stat-info">
            <span className="stat-label">Créances APD</span>
            <span className="stat-value">{formatCurrency(countryData.apd)}</span>
            <span className="stat-percent">{apdPercent}% du total</span>
          </div>
        </div>

        <div className="stat-item napd">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <line x1="3" y1="9" x2="21" y2="9" />
              <line x1="9" y1="21" x2="9" y2="9" />
            </svg>
          </div>
          <div className="stat-info">
            <span className="stat-label">Créances Non APD</span>
            <span className="stat-value">{formatCurrency(countryData.napd)}</span>
            <span className="stat-percent">{napdPercent}% du total</span>
          </div>
        </div>

        <div className="stat-item total">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div className="stat-info">
            <span className="stat-label">Total</span>
            <span className="stat-value highlight">{formatCurrency(countryData.total)}</span>
          </div>
        </div>

        <div className="update-info">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          <div>
            <span className="update-label">Données au</span>
            <span className="update-date">31 décembre {year}</span>
          </div>
        </div>
      </div>

      <div className="panel-bar">
        <div
          className="bar-apd"
          style={{ width: `${apdPercent}%` }}
          title={`APD: ${apdPercent}%`}
        />
        <div
          className="bar-napd"
          style={{ width: `${napdPercent}%` }}
          title={`Non APD: ${napdPercent}%`}
        />
      </div>
      <div className="bar-legend">
        <span><span className="dot apd" /> APD</span>
        <span><span className="dot napd" /> Non APD</span>
      </div>
    </div>
  );
};

export default CountryPanel;
