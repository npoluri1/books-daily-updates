const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = async (endpoint, options = {}) => {
  const url = `${API}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };
  if (config.body && typeof config.body === 'string') {
    config.headers['Content-Type'] = 'application/json';
  }
  const resp = await fetch(url, config);
  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(err);
  }
  return resp.json();
};

export const API_URL = API;
export default api;
