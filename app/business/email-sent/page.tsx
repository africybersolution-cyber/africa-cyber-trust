'use client';

import { useSearchParams } from 'next/navigation';
import { useState, useEffect, Suspense } from 'react';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

function EmailSentContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get('email') || '';
  const domain = searchParams.get('domain') || '';

  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes in seconds
  const [resending, setResending] = useState(false);
  const [resent, setResent] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleResend = async () => {
    setResending(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    setResending(false);
    setResent(true);
    setTimeLeft(600); // Reset timer

    setTimeout(() => setResent(false), 3000);
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
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
          {/* Success Icon */}
          <div className="text-center mb-12">
            <div className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center"
                 style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>

            <h1 className="text-5xl font-extrabold mb-4 text-white">
              Check Your Email
            </h1>
            <p className="text-xl text-gray-400">
              We've sent a verification link to
            </p>
            <p className="text-2xl font-bold mt-2" style={{ color: GOLD }}>
              {email}
            </p>
          </div>

          {/* Instructions */}
          <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-8 border border-blue-900/30 mb-8">
            <h2 className="text-2xl font-bold text-white mb-6">Next Steps:</h2>

            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                     style={{ background: `${BLUE}33`, color: BLUE }}>
                  <span className="font-bold">1</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-white mb-2">Open your email inbox</h3>
                  <p className="text-gray-400">
                    Check the inbox for <span className="text-white font-mono">{email}</span>
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                     style={{ background: `${BLUE}33`, color: BLUE }}>
                  <span className="font-bold">2</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-white mb-2">Look for our verification email</h3>
                  <p className="text-gray-400">
                    Subject: <span className="text-white">"Verify your domain for Africa Cyber Trust"</span>
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Didn't receive it? Check your spam or junk folder
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                     style={{ background: `${BLUE}33`, color: BLUE }}>
                  <span className="font-bold">3</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-white mb-2">Click the verification link</h3>
                  <p className="text-gray-400">
                    The link will automatically verify your domain and activate your account
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                     style={{ background: `${BLUE}33`, color: BLUE }}>
                  <span className="font-bold">4</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-white mb-2">Start monitoring your assets</h3>
                  <p className="text-gray-400">
                    Once verified, you'll be redirected to your dashboard to begin adding assets
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Email Preview */}
          <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl p-6 border border-blue-900/20 mb-8">
            <h3 className="text-lg font-bold text-white mb-4">Email Preview:</h3>
            <div className="bg-white rounded-xl p-6 text-gray-900">
              <div className="border-b border-gray-200 pb-4 mb-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                       style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}>
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <div className="font-bold">Africa Cyber Trust</div>
                    <div className="text-sm text-gray-600">noreply@africacybertrust.com</div>
                  </div>
                </div>
                <h4 className="font-bold text-lg">Verify your domain for Africa Cyber Trust</h4>
              </div>
              <div className="text-sm space-y-3">
                <p>Hello,</p>
                <p>You're almost ready to start monitoring <strong>{domain}</strong> with Africa Cyber Trust Infrastructure.</p>
                <p>Click the button below to verify your email address and activate your account:</p>
                <div className="text-center py-4">
                  <button
                    className="px-6 py-3 rounded-lg font-bold text-white"
                    style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
                  >
                    Verify Email Address
                  </button>
                </div>
                <p className="text-xs text-gray-600">
                  This link will expire in 24 hours. If you didn't request this verification, please ignore this email.
                </p>
              </div>
            </div>
          </div>

          {/* Timer & Resend */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 mb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <svg className="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-white font-semibold">Link expires in</p>
                  <p className="text-2xl font-bold" style={{ color: GOLD }}>
                    {formatTime(timeLeft)}
                  </p>
                </div>
              </div>
              <button
                onClick={handleResend}
                disabled={resending}
                className="px-6 py-3 rounded-xl font-bold border-2 hover:bg-blue-950/50 transition-all disabled:opacity-50"
                style={{ borderColor: BLUE, color: BLUE }}
              >
                {resending ? 'Sending...' : resent ? 'Email Sent!' : 'Resend Email'}
              </button>
            </div>
          </div>

          {/* Support */}
          <div className="text-center space-y-4">
            <p className="text-gray-400">
              Having trouble? We're here to help
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <a
                href="/contact"
                className="px-6 py-3 rounded-xl font-semibold border-2 hover:bg-blue-950/50 transition-all"
                style={{ borderColor: GOLD, color: GOLD }}
              >
                Contact Support
              </a>
              <a
                href="/business"
                className="px-6 py-3 rounded-xl font-semibold text-gray-400 hover:text-white transition-all"
              >
                Try Another Method
              </a>
            </div>
          </div>
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

export default function EmailSentPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center"><div className="text-white text-xl">Loading...</div></div>}>
      <EmailSentContent />
    </Suspense>
  );
}
