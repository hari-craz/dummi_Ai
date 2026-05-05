const API_BASE = 'http://localhost:8000';

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

// ── Users ──────────────────────────────────────
export const getUsers = () => request('/users/');
export const getUser = (id) => request(`/users/${id}`);
export const createUser = (data) =>
  request('/users/', { method: 'POST', body: JSON.stringify(data) });
export const updateUser = (id, data) =>
  request(`/users/${id}`, { method: 'PUT', body: JSON.stringify(data) });

// ── Content ────────────────────────────────────
export const getContent = () => request('/content/');
export const getContentItem = (id) => request(`/content/${id}`);
export const createContent = (data) =>
  request('/content/', { method: 'POST', body: JSON.stringify(data) });
export const getContentByCategory = (cat) => request(`/content/category/${cat}`);

// ── Recommendations ────────────────────────────
export const getRecommendations = (data) =>
  request('/recommendations/', { method: 'POST', body: JSON.stringify(data) });
export const submitFeedback = (data) =>
  request('/recommendations/feedback', { method: 'POST', body: JSON.stringify(data) });
export const recordInteraction = (data) =>
  request('/recommendations/interact', { method: 'POST', body: JSON.stringify(data) });

// ── Training ───────────────────────────────────
export const trainModels = (data) =>
  request('/training/train', { method: 'POST', body: JSON.stringify(data) });
export const getTrainingStatus = () => request('/training/status');

// ── Health ─────────────────────────────────────
export const healthCheck = () => request('/health');
