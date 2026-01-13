'use client';

import { createContext, useContext, ReactNode } from 'react';
import { useAuth as useBetterAuth } from 'better-auth/react';
import { User } from '@/types/user';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signIn: (provider: string, credentials: any) => Promise<any>;
  signUp: (userData: any) => Promise<any>;
  signOut: () => Promise<void>;
  getToken: () => Promise<string | null>; // Add method to get JWT token
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const {
    session,
    signIn: betterSignIn,
    signUp: betterSignUp,
    signOut: betterSignOut,
    setSession
  } = useBetterAuth();

  // Transform Better Auth session to our User type
  const currentUser = session?.user
    ? {
        id: session.user.id,
        email: session.user.email,
        name: session.user.name || session.user.email.split('@')[0],
        created_at: session.user.createdAt || new Date().toISOString(),
        updated_at: session.user.updatedAt || new Date().toISOString(),
        is_active: true,
      } as User
    : null;

  // Method to get the JWT token from Better Auth
  const getToken = async (): Promise<string | null> => {
    // In Better Auth, the token is typically part of the session
    if (session?.token) {
      return session.token;
    }
    return null;
  };

  const value = {
    user: currentUser,
    isLoading: session === undefined, // session is undefined while loading
    signIn: betterSignIn,
    signUp: betterSignUp,
    signOut: betterSignOut,
    getToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};