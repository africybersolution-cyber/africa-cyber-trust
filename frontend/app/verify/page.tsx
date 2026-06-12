'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

function VerifyContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [message, setMessage] = useState('');
  const [domain, setDomain] = useState('');

  useEffect(() => {
    const assetId = searchParams.get('asset');
    const token = searchParams.get('token');

    if (!assetId || !token) {
      setStatus('error');
      setMessage('Invalid verification link');
      return;
    }

    verifyDomain(assetId, token);
  }, [searchParams]);

  const verifyDomain = async (assetId: string, token: string) => {
    try {
      const response = await fetch(`/api/assets/verify/${assetId}/${token}`);

      if (response.ok) {
        const data = await response.json();
        setStatus('success');
        setDomain(data.domain);
        setMessage('Domain verified successfully!');
      } else {
        const errorData = await response.json();
        setStatus('error');
        setMessage(errorData.detail || 'Verification failed');
      }
    } catch (err) {
      setStatus('error');
      setMessage('Verification failed. Please try again.');
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-3xl shadow-2xl p-12 text-center">
          {status === 'verifying' && (
            <>
              <div className="w-20 h-20 border-4 border-t-blue-600 border-blue-200 rounded-full animate-spin mx-auto mb-6"></div>
              <h1 className="text-3xl font-bold mb-4" style={{ color: '#0047AB' }}>
                Verifying Domain...
              </h1>
              <p className="text-gray-600">
                Please wait while we verify your domain ownership
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h1 className="text-4xl font-bold mb-4 text-green-700">
                ✅ Domain Verified!
              </h1>
              <p className="text-xl text-gray-700 mb-2">
                <strong>{domain}</strong>
              </p>
              <p className="text-gray-600 mb-8">
                Your domain has been successfully verified and is now being monitored for security threats.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => router.push('/dashboard/assets')}
                  className="px-8 py-4 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
                  style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                >
                  Go to Dashboard
                </button>
                <button
                  onClick={() => router.push('/')}
                  className="px-8 py-4 rounded-xl font-semibold border-2 border-gray-300 hover:bg-gray-50 transition-colors"
                >
                  Back to Home
                </button>
              </div>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center bg-red-100">
                <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h1 className="text-4xl font-bold mb-4 text-red-600">
                Verification Failed
              </h1>
              <p className="text-gray-600 mb-8">
                {message}
              </p>
              <button
                onClick={() => router.push('/dashboard/assets')}
                className="px-8 py-4 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
                style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
              >
                Try Again
              </button>
            </>
          )}
        </div>

        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm">
            © 2026 Africa Cyber Trust Infrastructure
          </p>
        </div>
      </div>
    </main>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-t-blue-600 border-blue-200 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <VerifyContent />
    </Suspense>
  );
}
