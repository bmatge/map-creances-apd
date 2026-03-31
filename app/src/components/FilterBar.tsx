import type { FilterMode, DebtFilter } from '../types';

interface FilterBarProps {
  filterMode: FilterMode;
  debtFilter: DebtFilter;
  onFilterModeChange: (mode: FilterMode) => void;
  onDebtFilterChange: (filter: DebtFilter) => void;
}

const FilterBar = ({
  filterMode,
  debtFilter,
  onFilterModeChange,
  onDebtFilterChange,
}: FilterBarProps) => {
  return (
    <div className="filter-bar">
      <div className="filter-group">
        <span className="filter-label">Afficher :</span>
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterMode === 'all' ? 'active' : ''}`}
            onClick={() => onFilterModeChange('all')}
          >
            Tous
          </button>
          <button
            className={`filter-btn filter-btn-debtor ${filterMode === 'débiteur' ? 'active' : ''}`}
            onClick={() => onFilterModeChange('débiteur')}
          >
            Débiteurs
          </button>
          <button
            className={`filter-btn filter-btn-creditor ${filterMode === 'créditeur' ? 'active' : ''}`}
            onClick={() => onFilterModeChange('créditeur')}
          >
            Créditeurs
          </button>
        </div>
      </div>

      {filterMode === 'débiteur' && (
        <div className="filter-group">
          <span className="filter-label">Type :</span>
          <div className="filter-buttons">
            <button
              className={`filter-btn filter-btn-small ${debtFilter === 'apd' ? 'active' : ''}`}
              onClick={() => onDebtFilterChange('apd')}
            >
              APD
            </button>
            <button
              className={`filter-btn filter-btn-small ${debtFilter === 'napd' ? 'active' : ''}`}
              onClick={() => onDebtFilterChange('napd')}
            >
              Hors APD
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterBar;
