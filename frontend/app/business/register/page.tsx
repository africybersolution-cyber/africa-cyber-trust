'use client';

import { useState, useEffect, Suspense } from 'react';
import { config } from '@/lib/config';
import { useRouter, useSearchParams } from 'next/navigation';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

function RegisterContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Get company info from query params
  const companyName = searchParams.get('company_name') || '';
  const email = searchParams.get('email') || '';
  const domain = searchParams.get('domain') || 'example.com';
  const country = searchParams.get('country') || '';
  const industry = searchParams.get('industry') || '';

  const [selectedMethod, setSelectedMethod] = useState<'dns' | 'html' | 'email'>('dns');
  const [loading, setLoading] = useState(false);
  const [clickFeedback, setClickFeedback] = useState('');
  const [verificationToken, setVerificationToken] = useState('acti-loading...');

  // Generate token only on client side to avoid hydration mismatch
  useEffect(() => {
    setVerificationToken(`acti-${Math.random().toString(36).substring(2, 15)}`);
  }, []);

  const handleMethodClick = (method: 'dns' | 'html' | 'email') => {
    console.log('🖱️ CLICKED METHOD:', method);
    setSelectedMethod(method);
    setClickFeedback(`Selected: ${method.toUpperCase()}`);

    // Clear feedback after 2 seconds
    setTimeout(() => setClickFeedback(''), 2000);
  };

  const handleBack = () => {
    console.log('🔙 GOING BACK to /business');
    router.push('/business');
  };

  const sendVerificationEmail = async () => {
    const adminEmail = `admin@${domain}`;

    console.log('📧 SENDING EMAIL to:', adminEmail);

    try {
      // Call backend API to send verification email
      const response = await fetch(`${config.apiUrl}/api/email-verification/send-verification-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: adminEmail,
          company_name: companyName || 'Your Company',
          domain: domain,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to send email');
      }

      console.log('✅ EMAIL SENT:', data);

      // Navigate to email sent page
      const targetUrl = `/business/email-sent?email=${adminEmail}&domain=${domain}`;
      console.log('🚀 NAVIGATING to:', targetUrl);
      router.push(targetUrl);

    } catch (error: any) {
      console.error('❌ EMAIL ERROR:', error);
      alert(`Failed to send email: ${error.message}`);
      throw error;
    }
  };

  const handleContinue = async () => {
    console.log('🚀 CONTINUE CLICKED! Method:', selectedMethod);
    setLoading(true);
    setClickFeedback('Processing...');

    try {
      if (selectedMethod === 'email') {
        console.log('📧 EMAIL METHOD - Sending email...');
        await sendVerificationEmail();
      } else if (selectedMethod === 'dns') {
        console.log('🌐 DNS METHOD - Showing instructions...');
        const targetUrl = `/business/verify-status?method=dns&domain=${domain}&token=${verificationToken}`;
        console.log('🚀 NAVIGATING to:', targetUrl);
        router.push(targetUrl);
      } else if (selectedMethod === 'html') {
        console.log('📄 HTML METHOD - Showing instructions...');
        const targetUrl = `/business/verify-status?method=html&domain=${domain}&token=${verificationToken}`;
        console.log('🚀 NAVIGATING to:', targetUrl);
        router.push(targetUrl);
      }
    } catch (error: any) {
      console.error('❌ ERROR:', error);
      alert(`Error: ${error.message}`);
      setClickFeedback('');
    } finally {
      setTimeout(() => {
        setLoading(false);
      }, 1000);
    }
  };

  const verificationMethods = [
    {
      id: 'dns',
      title: 'DNS TXT Record',
      badge: 'Recommended',
      icon: (
        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      description: "Add a TXT record to your domain's DNS settings",
      details: [
        { label: 'Name:', value: '_acti-verify' },
        { label: 'Value:', value: verificationToken },
      ],
      color: BLUE,
    },
    {
      id: 'html',
      title: 'HTML File Upload',
      badge: null,
      icon: (
        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      description: 'Upload a verification file to your website root',
      details: [
        { label: 'File:', value: 'acti-verify.html' },
        { label: 'URL:', value: `https://${domain}/acti-verify.html` },
      ],
      color: GOLD,
    },
    {
      id: 'email',
      title: 'Email Verification',
      badge: null,
      icon: (
        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      description: `We'll send a verification link to admin@${domain}`,
      details: [],
      color: BLUE,
    },
  ];

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

      {/* Click Feedback Toast - ALWAYS VISIBLE WHEN YOU CLICK */}
      {clickFeedback && (
        <div className="fixed top-20 right-4 z-50 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-8 py-4 rounded-2xl shadow-2xl animate-bounce border-4 border-white">
          <div className="flex items-center gap-3">
            <svg className="w-8 h-8 animate-spin" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-bold text-xl">{clickFeedback}</span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6 border border-blue-400/30 shadow-lg shadow-blue-500/20" style={{ background: 'linear-gradient(135deg, rgba(0, 71, 171, 0.2) 0%, rgba(218, 165, 32, 0.2) 100%)' }}>
              <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-bold text-blue-300 tracking-wide">STEP 2 OF 2</span>
            </div>
            <h1 className="text-5xl font-extrabold mb-4 text-white">
              Choose a verification method:
            </h1>
            <p className="text-gray-400 text-lg">
              Verify ownership of {domain} to unlock deep security scanning
            </p>
          </div>

          {/* Current Selection Indicator */}
          <div className="mb-6 bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: BLUE }}>
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-400">Currently Selected:</p>
                <p className="text-lg font-bold text-white">
                  {selectedMethod === 'dns' && 'DNS TXT Record (Recommended)'}
                  {selectedMethod === 'html' && 'HTML File Upload'}
                  {selectedMethod === 'email' && 'Email Verification'}
                </p>
              </div>
            </div>
          </div>

          {/* Verification Methods */}
          <div className="space-y-6 mb-8">
            {verificationMethods.map((method) => {
              const isSelected = selectedMethod === method.id;

              return (
                <div
                  key={method.id}
                  onClick={() => handleMethodClick(method.id as any)}
                  onMouseEnter={() => console.log('🖱️ HOVER:', method.id)}
                  className={`bg-slate-800/60 backdrop-blur-xl rounded-2xl p-6 border-2 transition-all cursor-pointer transform hover:scale-[1.02] active:scale-[0.98] ${
                    isSelected
                      ? 'border-blue-500 shadow-lg shadow-blue-500/30 ring-2 ring-blue-400/50'
                      : 'border-blue-900/30 hover:border-blue-500/50'
                  }`}
                  style={{
                    transition: 'all 0.2s ease',
                  }}
                >
                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div
                      className="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg"
                      style={{ background: `linear-gradient(135deg, ${method.color} 0%, ${method.color}CC 100%)` }}
                    >
                      {method.icon}
                    </div>

                    {/* Content */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-2xl font-bold text-white">{method.title}</h3>
                        {method.badge && (
                          <span
                            className="px-3 py-1 rounded-full text-xs font-bold animate-pulse"
                            style={{ background: GOLD, color: '#0A1628' }}
                          >
                            {method.badge}
                          </span>
                        )}
                        {isSelected && (
                          <svg className="w-8 h-8 text-green-400 ml-auto animate-bounce" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <p className="text-gray-400 mb-4">{method.description}</p>

                      {/* Details */}
                      {method.details.length > 0 && (
                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                          {method.details.map((detail, index) => (
                            <div key={index} className="font-mono text-sm mb-2 last:mb-0">
                              <span className="text-gray-400">{detail.label}</span>{' '}
                              <span className="text-white font-semibold">{detail.value}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Company Info Summary */}
          {companyName && (
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-8">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div className="text-sm text-gray-300">
                  <p className="font-semibold text-white mb-1">Registering: {companyName}</p>
                  <p>Email: {email}</p>
                  <p>Domain: {domain}</p>
                  {country && <p>Country: {country}</p>}
                  {industry && <p>Industry: {industry}</p>}
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={handleBack}
              disabled={loading}
              className="flex-1 px-8 py-4 rounded-xl font-bold border-2 hover:bg-blue-950/50 transition-all disabled:opacity-50 transform hover:scale-105 active:scale-95"
              style={{ borderColor: GOLD, color: GOLD }}
            >
              Back
            </button>
            <button
              onClick={handleContinue}
              disabled={loading}
              className="flex-1 px-8 py-4 rounded-xl font-bold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50 transform hover:scale-105 active:scale-95"
              style={{ background: loading ? '#666' : `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                'Continue to Registration'
              )}
            </button>
          </div>

          {/* Help Text */}
          <div className="mt-8 text-center">
            <p className="text-gray-500 text-sm">
              Need help? <a href="/contact" className="text-blue-400 hover:text-blue-300 font-semibold">Contact Support</a>
            </p>
          </div>

          {/* Debug Info - Hidden in production, visible in dev */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-8 p-4 bg-slate-800/40 rounded-xl text-xs text-gray-400 font-mono border border-green-500/30">
              <p className="text-green-400 font-bold mb-2">🔍 DEV MODE - Debug Info:</p>
              <p>Selected Method: <span className="text-white">{selectedMethod}</span></p>
              <p>Loading: <span className="text-white">{loading ? 'Yes' : 'No'}</span></p>
              <p>Domain: <span className="text-white">{domain}</span></p>
              <p>Token: <span className="text-white">{verificationToken.substring(0, 20)}</span></p>
              <p className="mt-2 text-green-400 font-bold">✅ Page is interactive - Click any card above!</p>
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

export default function BusinessRegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center"><div className="text-white text-xl">Loading...</div></div>}>
      <RegisterContent />
    </Suspense>
  );
}
