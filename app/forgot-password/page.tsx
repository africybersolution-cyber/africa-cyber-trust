'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
      const response = await fetch(`${apiUrl}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to send reset email');
      }

      setSent(true);
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-slate-800/50 backdrop-blur-sm border-2 rounded-2xl p-6 md:p-8 shadow-2xl text-center" style={{ borderColor: 'rgba(0, 71, 171, 0.3)' }}>
            {/* Success Icon */}
            <div className="w-16 h-16 md:w-20 md:h-20 rounded-full mx-auto mb-6 flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
              <svg className="w-8 h-8 md:w-10 md:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <h1 className="text-2xl md:text-3xl font-bold text-white mb-4">Check Your Email</h1>
            <p className="text-gray-300 mb-6 text-sm md:text-base">
              We've sent password reset instructions to <strong style={{ color: GOLD }}>{email}</strong>
            </p>

            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-6">
              <p className="text-sm text-gray-300 text-left">
                <strong className="text-blue-400">Next steps:</strong><br/>
                1. Check your inbox (and spam folder)<br/>
                2. Click the reset link in the email<br/>
                3. Create your new password
              </p>
            </div>

            <button
              onClick={() => router.push('/login')}
              className="w-full py-3 md:py-4 rounded-xl font-bold text-white shadow-lg hover:scale-105 transition-all"
              style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}
            >
              Back to Login
            </button>

            <p className="text-sm text-gray-400 mt-4">
              Didn't receive the email?{' '}
              <button
                onClick={() => setSent(false)}
                className="font-bold hover:underline"
                style={{ color: GOLD }}
              >
                Try again
              </button>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <a href="/" className="block text-center mb-6 md:mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 md:w-14 md:h-14 rounded-xl flex items-center justify-center shadow-lg" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}>
              <svg className="w-7 h-7 md:w-8 md:h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <div className="text-xl md:text-2xl font-bold">
                <span style={{ color: BLUE }}>AFRICA CYBER </span>
                <span style={{ color: GOLD }}>TRUST</span>
              </div>
              <div className="text-xs text-gray-400">INFRASTRUCTURE</div>
            </div>
          </div>
        </a>

        {/* Form */}
        <div className="bg-slate-800/50 backdrop-blur-sm border-2 rounded-2xl p-6 md:p-8 shadow-2xl" style={{ borderColor: 'rgba(0, 71, 171, 0.3)' }}>
          <div className="mb-6 md:mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">Forgot Password?</h2>
            <p className="text-sm md:text-base text-gray-400">No worries! Enter your email and we'll send you reset instructions.</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="forgot-email" className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
              <input
                id="forgot-email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 md:py-4 bg-slate-900/50 border rounded-lg text-white placeholder-gray-500 focus:outline-none transition-all text-base"
                style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                onFocus={(e) => e.currentTarget.style.borderColor = BLUE}
                onBlur={(e) => e.currentTarget.style.borderColor = 'rgba(71, 85, 105, 0.5)'}
                placeholder="you@company.com"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 md:py-4 text-white rounded-xl font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:scale-105"
              style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Sending...
                </span>
              ) : (
                'Send Reset Instructions'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <a
              href="/login"
              className="text-sm font-medium hover:underline inline-flex items-center gap-2"
              style={{ color: GOLD }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Login
            </a>
          </div>
        </div>

        <p className="text-center text-xs text-gray-500 mt-6">
          © 2026 Africa Cyber Trust Infrastructure
        </p>
      </div>
    </div>
  );
}
