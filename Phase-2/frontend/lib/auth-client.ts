import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  user: AuthUser;
}

class AuthClient {
  private client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async signIn(credentials: { email: string; password: string }) {
    const response = await this.client.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  }

  async signUp(userData: { email: string; password: string; name?: string }) {
    const response = await this.client.post<AuthResponse>('/auth/register', {
      email: userData.email,
      password: userData.password,
      name: userData.name ?? '',
    });
    return response.data;
  }

  async getMe(token: string) {
    const response = await this.client.get<AuthUser>('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }
}

export const authClient = new AuthClient();
