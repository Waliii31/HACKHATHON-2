"use client";

import { createContext, useContext, ReactNode, useState, useEffect } from 'react';
import { authClient, AuthUser } from '@/lib/auth-client';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  signIn: (credentials: { email: string; password: string }) => Promise<any>;
  signUp: (userData: { email: string; password: string; name?: string }) => Promise<any>;
  signOut: () => Promise<void>;
  getToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadSession = async () => {
      try {
        const storedToken = localStorage.getItem('todo_token');
        const storedUser = localStorage.getItem('todo_user');
        if (storedToken && storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    loadSession();
  }, []);

  const signIn = async (credentials: { email: string; password: string }) => {
    try {
      const result = await authClient.signIn(credentials);
      localStorage.setItem('todo_token', result.access_token);
      localStorage.setItem('todo_user', JSON.stringify(result.user));
      setUser(result.user);
      return result;
    } catch (err) {
      throw err;
    }
  };

  const signUp = async (userData: { email: string; password: string; name?: string }) => {
    try {
      const result = await authClient.signUp(userData);
      localStorage.setItem('todo_token', result.access_token);
      localStorage.setItem('todo_user', JSON.stringify(result.user));
      setUser(result.user);
      return result;
    } catch (err) {
      throw err;
    }
  };

  const signOut = async () => {
    localStorage.removeItem('todo_token');
    localStorage.removeItem('todo_user');
    setUser(null);
  };

  const getToken = async () => {
    return localStorage.getItem('todo_token');
  };

  const value = { user, isLoading, signIn, signUp, signOut, getToken };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
