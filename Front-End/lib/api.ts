const BASE_URL = 'http://localhost:8000';
//const BASE_URL = `http://${window.location.hostname}:8000`;

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

// >>> Função nova para registrar usuário
export const registerUser = async (name: string, email: string, password: string) => {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  if (!res.ok) {
    const errData = await res.json();
    throw new Error(errData.detail || 'Failed to register user');
  }
  return res.json();
};

export const resetPassword = async (email: string, newPassword: string) => {
  const res = await fetch(`${BASE_URL}/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, new_password: newPassword }),
  });
  if (!res.ok) throw new Error("Failed to reset password");
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


//Adicionado 07/04
export const downloadReportPDF = async (text: string, filename: string = "relatorio_mro.pdf") => {
  const token = localStorage.getItem('mro_token');
  const res = await fetch(`${BASE_URL}/chat/download-pdf`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ text, filename }),
  });
  if (!res.ok) throw new Error('Download failed');
  
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};