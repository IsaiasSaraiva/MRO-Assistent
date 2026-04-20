export const saveToken = (token: string) => {
  localStorage.setItem('mro_token', token);
  document.cookie = `mro_token=${token}; path=/; max-age=${8 * 60 * 60}`;
};

export const getToken = () => localStorage.getItem('mro_token');

export const clearToken = () => {
  localStorage.removeItem('mro_token');
  document.cookie = 'mro_token=; path=/; max-age=0';
};

export const isAuthenticated = () => !!getToken();

export interface JWTPayload {
  user_id: string;
  email: string;
  name: string;
  exp: number;
}

export const decodeToken = (token: string): JWTPayload | null => {
  try {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
};
