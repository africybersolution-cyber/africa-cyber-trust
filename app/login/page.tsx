'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';

export default function BrandedLoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    console.log('📝 Form submitted with email:', email);

    try {
      await login(email, password);
      console.log('✅ Login successful, redirecting to dashboard...');
      router.push('/dashboard');
    } catch (err: any) {
      console.error('❌ Login failed:', err);
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8">
        {/* Left Side - Branding */}
        <div className="hidden lg:flex flex-col justify-center p-12">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-14 h-14 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold">
                  <span style={{ color: '#0047AB' }}>AFRICA CYBER </span>
                  <span style={{ color: '#DAA520' }}>TRUST</span>
                </div>
                <div className="text-xs text-gray-400">INFRASTRUCTURE</div>
              </div>
            </div>

            <h1 className="text-4xl font-bold text-white mb-4">
              Welcome Back to<br />
              <span className="bg-gradient-to-r from-blue-500 to-yellow-500 bg-clip-text text-transparent">
                Secure Monitoring
              </span>
            </h1>
            <p className="text-gray-300 text-lg mb-8">
              Access your cybersecurity dashboard and protect your digital infrastructure
            </p>
          </div>

          <div className="space-y-6">
            <div className="bg-slate-800/30 border rounded-xl p-6" style={{ borderColor: 'rgba(0, 71, 171, 0.3)' }}>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1e40af 100%)' }}>
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-white font-bold">Real-time Protection</div>
                  <div className="text-gray-400 text-sm">24/7 threat monitoring active</div>
                </div>
              </div>
            </div>

            <div className="bg-slate-800/30 border rounded-xl p-6" style={{ borderColor: 'rgba(218, 165, 32, 0.3)' }}>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #DAA520 0%, #b8860b 100%)' }}>
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <div>
                  <div className="text-white font-bold">Secure Access</div>
                  <div className="text-gray-400 text-sm">Enterprise-grade encryption</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="flex items-center">
          <div className="w-full bg-slate-800/50 backdrop-blur-sm border-2 rounded-2xl p-8 shadow-2xl" style={{ borderColor: 'rgba(0, 71, 171, 0.3)' }}>
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-white mb-2">Sign In</h2>
              <p className="text-gray-400">Access your security dashboard</p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900/50 border rounded-lg text-white placeholder-gray-500 focus:outline-none transition-all"
                  style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                  onFocus={(e) => e.target.style.borderColor = '#0047AB'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(71, 85, 105, 0.5)'}
                  placeholder="you@company.com"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-300">Password</label>
                  <a href="/forgot-password" className="text-sm font-medium hover:underline" style={{ color: '#DAA520' }}>
                    Forgot password?
                  </a>
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900/50 border rounded-lg text-white placeholder-gray-500 focus:outline-none transition-all"
                  style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                  onFocus={(e) => e.target.style.borderColor = '#0047AB'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(71, 85, 105, 0.5)'}
                  placeholder="Enter your password"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 text-white rounded-xl font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:scale-105"
                style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Signing in...
                  </span>
                ) : (
                  '🔐 Sign In'
                )}
              </button>
            </form>

            <div className="mt-8">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t" style={{ borderColor: 'rgba(71, 85, 105, 0.3)' }}></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-slate-800 text-gray-400">New to Africa Cyber Trust?</span>
                </div>
              </div>

              <div className="mt-6 text-center">
                <a
                  href="/signup"
                  className="inline-block px-8 py-3 border-2 rounded-xl font-semibold text-white transition-all hover:scale-105"
                  style={{ borderColor: '#DAA520', color: '#DAA520' }}
                >
                  Create Account - Start Free Trial
                </a>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t" style={{ borderColor: 'rgba(0, 71, 171, 0.2)' }}>
              <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
                <a href="/terms" className="hover:text-gray-300">Terms</a>
                <span>•</span>
                <a href="/privacy" className="hover:text-gray-300">Privacy</a>
                <span>•</span>
                <a href="/contact" className="hover:text-gray-300">Support</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
