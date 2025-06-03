import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth/';

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData extends LoginData {
  email: string;
  role: 'merchant' | 'admin';
  business_name?: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  tokens: {
    access: string;
    refresh: string;
  };
  user: {
    email: string;
    role: string;
    business_name?: string;
  };
}

const authService = {
  async login(data: LoginData): Promise<AuthResponse> {
    const response = await axios.post(`${API_URL}login/`, data);
    if (response.data.tokens) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await axios.post(`${API_URL}register/`, data);
    if (response.data.tokens) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  },

  logout() {
    localStorage.removeItem('user');
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) return JSON.parse(userStr);
    return null;
  },

  async refreshToken() {
    const user = this.getCurrentUser();
    if (user?.tokens.refresh) {
      const response = await axios.post(`${API_URL}token/refresh/`, {
        refresh: user.tokens.refresh
      });
      if (response.data.access) {
        user.tokens.access = response.data.access;
        localStorage.setItem('user', JSON.stringify(user));
      }
      return response.data;
    }
    return null;
  }
};

export default authService;