const BASE_URL = 'http://localhost:8000';

const authHeaders = () => {
  const token = localStorage.getItem('mro_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

export const login = async (email: string, password: string) => {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error('Invalid credentials');
  return res.json();
};

export const getDocuments = async () => {
  const res = await fetch(`${BASE_URL}/documents`, { headers: authHeaders() });
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
};

export const uploadDocuments = async (files: FileList) => {
  const token = localStorage.getItem('mro_token');
  const form = new FormData();
  Array.from(files).forEach(f => form.append('files', f));
  const res = await fetch(`${BASE_URL}/documents/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: form,
  });
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
};

export const deleteDocument = async (id: string) => {
  const res = await fetch(`${BASE_URL}/documents/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Delete failed');
  return res.json();
};

export const clearCollection = async () => {
  const res = await fetch(`${BASE_URL}/collection`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Clear failed');
  return res.json();
};

export const sendMessage = async (question: string) => {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error('Chat failed');
  return res.json();
};
