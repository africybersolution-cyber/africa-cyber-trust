'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

export const dynamic = 'force-dynamic';

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const token = searchParams.get('token') || '';
  const email = searchParams.get('email') || '';

  const [verifying, setVerifying] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      verifyEmail();
    } else {
      setVerifying(false);
      setError('Invalid verification link');
    }
  }, [token]);

  const verifyEmail = async () => {
    try {
      // Simulate API call to verify email
      await new Promise(resolve => setTimeout(resolve, 2000));

      // In real app, call backend API:
      // const response = await fetch('/api/verify-email', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ token }),
      // });

      // For now, simulate success
      setSuccess(true);
      setVerifying(false);

      // Redirect to dashboard after 3 seconds
      setTimeout(() => {
        router.push('/dashboard');
      }, 3000);
    } catch (err: any) {
      setError(err.message || 'Verification failed');
      setVerifying(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-blue-900/50 bg-slate-900/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <a href="/" className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}>
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <div className="font-bold text-xl tracking-tight">
                <span style={{ color: BLUE }}>AFRICA </span>
                <span style={{ color: GOLD }}>CYBER TRUST</span>
              </div>
              <div className="text-xs text-gray-400 tracking-widest">INFRASTRUCTURE</div>
            </div>
          </a>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-2xl mx-auto">
          {verifying && (
            <div className="text-center">
              {/* Loading Animation */}
              <div className="w-24 h-24 mx-auto mb-8 relative">
                <div className="absolute inset-0 rounded-full border-4 border-blue-500/20"></div>
                <div className="absolute inset-0 rounded-full border-4 border-t-blue-500 animate-spin"></div>
                <svg className="absolute inset-0 m-auto w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>

              <h1 className="text-4xl font-bold text-white mb-4">
                Verifying your email...
              </h1>
              <p className="text-gray-400 text-lg">
                Please wait while we confirm your email address
              </p>
            </div>
          )}

          {success && !verifying && (
            <div className="text-center">
              {/* Success Animation */}
              <div className="w-24 h-24 mx-auto mb-8 rounded-full flex items-center justify-center"
                   style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>

              <h1 className="text-5xl font-bold text-white mb-4">
                Email Verified!
              </h1>
              <p className="text-gray-400 text-lg mb-8">
                Your domain ownership has been confirmed
              </p>

              <div className="bg-blue-500/10 border border-blue-500/30 rounded-2xl p-6 mb-8">
                <div className="flex items-start gap-4">
                  <svg className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div className="text-left flex-1">
                    <h3 className="font-bold text-white mb-2">What happens next?</h3>
                    <ul className="text-gray-300 space-y-2 text-sm">
                      <li className="flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        <span>Your account is now activated</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        <span>You can start adding assets to monitor</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        <span>Deep security scanning is now available</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        <span>Redirecting to your dashboard...</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <button
                onClick={() => router.push('/dashboard')}
                className="px-8 py-4 rounded-xl font-bold text-white shadow-lg hover:shadow-xl transition-all"
                style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
              >
                Go to Dashboard Now →
              </button>
            </div>
          )}

          {error && !verifying && !success && (
            <div className="text-center">
              {/* Error Icon */}
              <div className="w-24 h-24 mx-auto mb-8 rounded-full flex items-center justify-center bg-red-500/20 border-4 border-red-500/50">
                <svg className="w-12 h-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>

              <h1 className="text-4xl font-bold text-white mb-4">
                Verification Failed
              </h1>
              <p className="text-red-400 text-lg mb-8">
                {error}
              </p>

              <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 mb-8">
                <div className="text-left text-gray-300 space-y-3">
                  <p className="font-semibold text-white">Common issues:</p>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">•</span>
                      <span>The verification link may have expired (valid for 24 hours)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">•</span>
                      <span>The link may have already been used</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">•</span>
                      <span>The token may be invalid or corrupted</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => router.push('/business')}
                  className="px-8 py-4 rounded-xl font-bold border-2 hover:bg-blue-950/50 transition-all"
                  style={{ borderColor: GOLD, color: GOLD }}
                >
                  Start Over
                </button>
                <button
                  onClick={() => router.push('/contact')}
                  className="px-8 py-4 rounded-xl font-bold text-white shadow-lg hover:shadow-xl transition-all"
                  style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
                >
                  Contact Support
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/50 backdrop-blur-xl mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-sm text-gray-500">
            <p>© 2026 Africa Cyber Trust Infrastructure. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
