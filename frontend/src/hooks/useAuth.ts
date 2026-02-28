"use client";
import { useState, useEffect } from "react";

export function useAuth() {
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    setAuthenticated(!!localStorage.getItem("token"));
  }, []);

  const setToken = (token: string) => {
    localStorage.setItem("token", token);
    setAuthenticated(true);
  };

  const clearToken = () => {
    localStorage.removeItem("token");
    setAuthenticated(false);
  };

  return { authenticated, setToken, clearToken };
}
