'use client';

import { useAuth } from '@/contexts/auth-context';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ReactNode } from 'react';

interface AuthGuardProps {
  children: ReactNode;
  fallbackUrl?: string;
}

export const AuthGuard = ({ children, fallbackUrl = '/login' }: AuthGuardProps) => {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push(fallbackUrl as any);
    }
  }, [user, isLoading, router, fallbackUrl]);

  // Show loading state while checking auth
  if (isLoading || (!user && !isLoading)) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <p className="text-sm text-slate-300">Loading...</p>
      </div>
    );
  }

  // If user is authenticated, render children
  return <>{children}</>;
};
