'use client';

import { useState, useEffect, Suspense } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter, useSearchParams } from 'next/navigation';

export const dynamic = 'force-dynamic';

function SignupContent() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Get plan from URL or default to 'personal'
  const plan = searchParams.get('plan') || 'personal';
  const planInfo = {
    'personal': { name: 'Personal', price: '$5/month', trial: '7 days', color: '#0047AB' },
    'professional': { name: 'Professional', price: '$49/month', trial: '14 days', color: '#DAA520' }
  };
  const currentPlan = planInfo[plan as keyof typeof planInfo] || planInfo['personal'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      await signup(email, password, name, plan);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <a href="/" className="block text-center mb-8">
          <div className="w-20 h-20 rounded-2xl mx-auto flex items-center justify-center mb-4 shadow-2xl shadow-blue-500/30" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
            <svg className="w-11 h-11 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold mb-2">
            <span style={{ color: '#0047AB' }}>Create </span>
            <span style={{ color: '#DAA520' }}>Account</span>
          </h1>
          <p className="text-gray-400">Join Africa Cyber Trust Infrastructure</p>
        </a>

        {/* Signup Form */}
        <div className="bg-slate-800/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-blue-900/30">
          {/* Plan Info Banner */}
          <div className="mb-6 p-4 rounded-xl border-2" style={{ borderColor: currentPlan.color, backgroundColor: `${currentPlan.color}15` }}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-white text-lg">{currentPlan.name} Plan</h3>
                <p className="text-gray-300 text-sm">{currentPlan.price} • {currentPlan.trial} free trial</p>
              </div>
              <div className="text-2xl">🎉</div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                <p className="text-red-400 text-sm font-medium">{error}</p>
              </div>
            )}

            <div>
              <label htmlFor="signup-name" className="block text-sm font-bold mb-2 text-gray-300">Full Name</label>
              <input
                id="signup-name"
                name="name"
                type="text"
                autoComplete="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none transition-all bg-slate-900/50 text-white placeholder-gray-500"
                placeholder="John Doe"
                required
              />
            </div>

            <div>
              <label htmlFor="signup-email" className="block text-sm font-bold mb-2 text-gray-300">Email Address</label>
              <input
                id="signup-email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none transition-all bg-slate-900/50 text-white placeholder-gray-500"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label htmlFor="signup-password" className="block text-sm font-bold mb-2 text-gray-300">Password</label>
              <input
                id="signup-password"
                name="new-password"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none transition-all bg-slate-900/50 text-white placeholder-gray-500"
                placeholder="••••••••"
                required
                minLength={8}
              />
              <p className="text-xs text-gray-500 mt-1">At least 8 characters</p>
            </div>

            <div>
              <label htmlFor="signup-confirm-password" className="block text-sm font-bold mb-2 text-gray-300">Confirm Password</label>
              <input
                id="signup-confirm-password"
                name="confirm-password"
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none transition-all bg-slate-900/50 text-white placeholder-gray-500"
                placeholder="••••••••"
                required
              />
            </div>

            <div className="flex items-start pt-2">
              <input
                id="signup-terms"
                name="terms"
                type="checkbox"
                className="mt-1 mr-3 w-4 h-4 rounded border-gray-600 bg-slate-900"
                required
              />
              <label htmlFor="signup-terms" className="text-sm text-gray-400">
                I agree to the{' '}
                <a href="/terms" className="text-blue-400 hover:text-blue-300 font-semibold">
                  Terms of Service
                </a>{' '}
                and{' '}
                <a href="/privacy" className="text-blue-400 hover:text-blue-300 font-semibold">
                  Privacy Policy
                </a>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 rounded-xl font-bold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-lg mt-6"
              style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating account...
                </span>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-700 text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <a href="/login" className="text-blue-400 hover:text-blue-300 font-bold">
                Sign in →
              </a>
            </p>
          </div>
        </div>

        <div className="mt-6 text-center">
          <a href="/" className="text-gray-400 hover:text-gray-300 text-sm inline-flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to home
          </a>
        </div>
      </div>
    </main>
  );
}

export default function SignupPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-t-blue-600 border-blue-200 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <SignupContent />
    </Suspense>
  );
}
