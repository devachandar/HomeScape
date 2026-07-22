import React, { createContext, useContext, useEffect, useState } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("homescape_access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    client
      .get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem("homescape_access_token");
        localStorage.removeItem("homescape_refresh_token");
      })
      .finally(() => setLoading(false));
  }, []);

  function persistSession({ user, accessToken, refreshToken }) {
    localStorage.setItem("homescape_access_token", accessToken);
    if (refreshToken) localStorage.setItem("homescape_refresh_token", refreshToken);
    setUser(user);
  }

  async function login(email, password) {
    const res = await client.post("/auth/login", { email, password });
    persistSession(res.data);
    return res.data.user;
  }

  async function register(payload) {
    const res = await client.post("/auth/register", payload);
    persistSession(res.data);
    return res.data.user;
  }

  function logout() {
    const refreshToken = localStorage.getItem("homescape_refresh_token");
    client.post("/auth/logout", { refreshToken }).catch(() => {});
    localStorage.removeItem("homescape_access_token");
    localStorage.removeItem("homescape_refresh_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
