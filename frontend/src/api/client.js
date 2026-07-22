import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8080/api";

const client = axios.create({ baseURL });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("homescape_access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default client;
