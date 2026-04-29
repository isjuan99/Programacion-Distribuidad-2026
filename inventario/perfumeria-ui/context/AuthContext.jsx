/*import { createContext, useContext, useState, useCallback } from "react";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("aroma_user"));
    } catch {
      return null;
    }
  });

  const login = useCallback((userData) => {
    localStorage.setItem("aroma_user", JSON.stringify(userData));
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("aroma_user");
    setUser(null);
  }, []);

  return (
    <AuthCtx.Provider value={{ user, login, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);*/

// src/context/AuthContext.jsx
import { createContext, useContext, useState, useCallback } from "react";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem("aroma_user");
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem("aroma_token") || null;
  });

  const login = useCallback((userData, accessToken) => {
    // userData debe contener: { id, nombre, email, rol }
    const userToStore = {
      id: userData.id,
      nombre: userData.nombre,
      email: userData.email,
      rol: userData.rol
    };
    
    localStorage.setItem("aroma_user", JSON.stringify(userToStore));
    localStorage.setItem("aroma_token", accessToken);
    localStorage.setItem("aroma_rol", userData.rol);
    
    setUser(userToStore);
    setToken(accessToken);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("aroma_user");
    localStorage.removeItem("aroma_token");
    localStorage.removeItem("aroma_rol");
    setUser(null);
    setToken(null);
  }, []);

  const isAdmin = useCallback(() => {
    return user?.rol === "admin";
  }, [user]);

  const isCliente = useCallback(() => {
    return user?.rol === "cliente";
  }, [user]);

  return (
    <AuthCtx.Provider value={{ 
      user, 
      token, 
      login, 
      logout, 
      isAdmin, 
      isCliente,
      rol: user?.rol
    }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthCtx);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de AuthProvider");
  }
  return context;
};
