import type { YearTotals } from '../types';

interface KPIBarProps {
  totals: YearTotals;
  year: number;
}

const formatCurrency = (value: number) => {
  if (value >= 1e9) {
    return `${(value / 1e9).toFixed(1)} Md€`;
  }
  if (value >= 1e6) {
    return `${(value / 1e6).toFixed(0)} M€`;
  }
  return `${value.toLocaleString('fr-FR')} €`;
};

const KPIBar = ({ totals, year }: KPIBarProps) => {
  const kpis = [
    {
      label: 'Créances APD',
      value: formatCurrency(totals.apd),
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
      ),
      color: '#f97316',
    },
    {
      label: 'Créances Non APD',
      value: formatCurrency(totals.napd),
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <line x1="3" y1="9" x2="21" y2="9" />
          <line x1="9" y1="21" x2="9" y2="9" />
        </svg>
      ),
      color: '#3b82f6',
    },
    {
      label: 'Total des créances',
      value: formatCurrency(totals.total),
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="12" y1="1" x2="12" y2="23" />
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
        </svg>
      ),
      color: '#10b981',
    },
    {
      label: 'Pays débiteurs',
      value: `${totals.countryCount}`,
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="2" y1="12" x2="22" y2="12" />
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        </svg>
      ),
      color: '#8b5cf6',
    },
    {
      label: 'Année',
      value: `${year}`,
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
        </svg>
      ),
      color: '#6b7280',
    },
  ];

  return (
    <div className="kpi-bar">
      <h3 className="kpi-title">Statistiques des créances françaises</h3>
      <div className="kpi-grid">
        {kpis.map((kpi, index) => (
          <div key={index} className="kpi-item">
            <div className="kpi-icon" style={{ color: kpi.color }}>
              {kpi.icon}
            </div>
            <div className="kpi-content">
              <span className="kpi-value" style={{ color: kpi.color }}>
                {kpi.value}
              </span>
              <span className="kpi-label">{kpi.label}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KPIBar;
