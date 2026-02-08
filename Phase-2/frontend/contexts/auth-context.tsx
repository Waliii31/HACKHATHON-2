"use client";

import { createContext, useContext, ReactNode, useState, useEffect } from 'react';
import { authClient } from '@/lib/auth-client';

interface User {
  id: string;
  email: string;
  name?: string | null;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signIn: (credentials: { email: string; password: string }) => Promise<any>;
  signUp: (userData: { email: string; password: string; name?: string }) => Promise<any>;
  signOut: () => Promise<void>;
  getToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load session on mount
  useEffect(() => {
    authClient.getSession()
      .then((session) => {
        if (session?.data?.user) {
          setUser({
            id: session.data.user.id,
            email: session.data.user.email,
            name: session.data.user.name
          });
        }
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const signIn = async (credentials: { email: string; password: string }) => {
    try {
      const result = await authClient.signIn.email({
        email: credentials.email,
        password: credentials.password,
      });

      if (result?.data?.user) {
        setUser({
          id: result.data.user.id,
          email: result.data.user.email,
          name: result.data.user.name
        });
      }

      return result;
    } catch (err) {
      throw err;
    }
  };

  const signUp = async (userData: { email: string; password: string; name?: string }) => {
    try {
      const result = await authClient.signUp.email({
        email: userData.email,
        password: userData.password,
        name: userData.name || "",
      });

      if (result?.data?.user) {
        setUser({
          id: result.data.user.id,
          email: result.data.user.email,
          name: result.data.user.name
        });
      }

      return result;
    } catch (err) {
      throw err;
    }
  };

  const signOut = async () => {
    await authClient.signOut();
    setUser(null);
  };

  const getToken = async () => {
    const session = await authClient.getSession();
    return session?.data?.session?.token || session?.data?.session?.id || null;
  };

  const value = { user, isLoading, signIn, signUp, signOut, getToken };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};