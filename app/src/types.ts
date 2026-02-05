export interface CountryData {
  country: string;
  apd: number;
  napd: number;
  total: number;
}

export interface YearTotals {
  apd: number;
  napd: number;
  total: number;
  countryCount: number;
}

export interface YearData {
  countries: Record<string, CountryData>;
  totals: YearTotals;
}

export interface AllData {
  [year: string]: YearData;
}
