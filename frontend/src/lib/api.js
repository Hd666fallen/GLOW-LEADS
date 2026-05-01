import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("glow_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const saveAuth = (token, user) => {
  localStorage.setItem("glow_token", token);
  localStorage.setItem("glow_user", JSON.stringify(user));
};

export const clearAuth = () => {
  localStorage.removeItem("glow_token");
  localStorage.removeItem("glow_user");
};

export const currentUser = () => {
  try {
    const raw = localStorage.getItem("glow_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const fileToBase64 = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
