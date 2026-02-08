'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  const { signIn } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await signIn({
        email,
        password,
      });

      // If successful, redirect to dashboard
      router.push('/dashboard');
      router.refresh();
    } catch (err: any) {
      setError(err?.message || error?.toString() || 'Login failed. Please check your credentials.');
      console.error(err);
    }
  };

  return (
    <div className="mx-auto flex min-h-[80vh] max-w-5xl items-center justify-center px-4">
      <div className="grid w-full grid-cols-1 gap-10 rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-blue-500/10 backdrop-blur-xl md:grid-cols-2">
        <div className="flex flex-col justify-center space-y-4">
          <span className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-300">Welcome back</span>
          <h1 className="text-3xl font-semibold text-white md:text-4xl">Sign in to manage your tasks.</h1>
          <p className="text-sm text-slate-300">
            Stay organized with a clean, focused workspace. Your tasks sync instantly across devices.
          </p>
          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-blue-500/20 to-indigo-500/20 p-4 text-sm text-slate-200">
            <p className="font-medium text-white">Tip</p>
            <p>Use priorities and due dates to keep your week on track.</p>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-6 shadow-inner">
          <h2 className="text-xl font-semibold text-white">Login</h2>
          <p className="mt-1 text-sm text-slate-400">Enter your credentials to continue.</p>

          {error && (
            <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label htmlFor="email" className="block text-xs font-medium uppercase tracking-wide text-slate-400">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                placeholder="you@domain.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-medium uppercase tracking-wide text-slate-400">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition hover:from-blue-400 hover:to-indigo-500"
            >
              Login
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-400">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="font-semibold text-blue-300 hover:text-blue-200">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
