const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ScanRequest {
  url: string;
  html_snapshot?: string;
  image?: File;
}

export interface ScanResponse {
  checkout_id: number;
  domain: string;
  risk_score: number;
  events: Array<{
    kind: string;
    score: number;
    detail: any;
  }>;
  clean_overlay: {
    true_total: number | null;
    callouts: string[];
  };
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface VirtualCardRequest {
  merchant_domain: string;
  max_amount: number;
  expires_at: string;
  merchant_lock: boolean;
}

export interface VirtualCardResponse {
  id: number;
  user_id: number;
  merchant_domain: string;
  pan_last4: string;
  alias_token: string;
  max_amount: number;
  currency: string;
  expires_at: string;
  status: string;
  controls: {
    merchant_lock: boolean;
    spend_cap: boolean;
    auto_expire: boolean;
  };
  created_at: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = API_URL;
    this.token = localStorage.getItem('access_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async register(email: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.token = response.access_token;
    localStorage.setItem('access_token', response.access_token);
    return response;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.token = response.access_token;
    localStorage.setItem('access_token', response.access_token);
    return response;
  }

  async scanCheckout(data: ScanRequest): Promise<ScanResponse> {
    const formData = new FormData();
    formData.append('url', data.url);
    
    if (data.html_snapshot) {
      formData.append('html_snapshot', data.html_snapshot);
    }
    
    if (data.image) {
      formData.append('image', data.image);
    }

    const response = await fetch(`${this.baseUrl}/detect/scan`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async createVirtualCard(data: VirtualCardRequest): Promise<VirtualCardResponse> {
    return this.request<VirtualCardResponse>('/virtual-cards/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getImpactSummary(): Promise<{
    blocked_transactions: number;
    fees_blocked_usd: number;
    subscriptions_paused: number;
    disputes_filed: number;
    estimated_savings_usd: number;
  }> {
    return this.request('/impact/summary');
  }
}

export const api = new ApiClient();

