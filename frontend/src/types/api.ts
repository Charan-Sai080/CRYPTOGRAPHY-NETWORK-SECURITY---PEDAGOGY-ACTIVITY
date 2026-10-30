export interface ErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ErrorResponse {
  error: string;
  detail: string;
  timestamp?: string;
  errors?: ErrorDetail[];
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp?: string;
  modules: {
    number_theory: string;
    otp: string;
    lcg: string;
    elgamal: string;
    dsa: string;
  };
}

export interface RootResponse {
  app: string;
  version: string;
  docs_url: string;
  redoc_url: string;
  endpoints_prefix: string;
}

export type Theme = 'dark' | 'light';

export interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}
