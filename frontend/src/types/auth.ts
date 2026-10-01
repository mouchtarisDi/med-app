export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
}

export interface CurrentUser {
  email: string;
  full_name: string;
  id: number;
}
