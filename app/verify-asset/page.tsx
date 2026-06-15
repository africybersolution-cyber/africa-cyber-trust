'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { config } from '@/lib/config';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

function VerifyAssetContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [assetDomain, setAssetDomain] = useState('');

  useEffect(() => {
    const assetId = searchParams.get('asset');
    const token = searchParams.get('token');

    if (!assetId || !token) {
      setStatus('error');
      setMessage('Invalid verification link. Missing asset ID or token.');
      return;
    }

    // Call verification endpoint
    verifyAsset(assetId, token);
  }, [searchParams]);

  const verifyAsset = async (assetId: string, token: string) => {
    try {
      const response = await fetch(`${config.apiUrl}/api/assets/verify/${assetId}/${token}`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        setStatus('success');
        setMessage('Domain verified successfully!');
        setAssetDomain(data.domain);

        // Redirect to assets page after 3 seconds
        setTimeout(() => {
          router.push('/dashboard/assets');
        }, 3000);
      } else {
        const errorData = await response.json();
        setStatus('error');
        setMessage(errorData.detail || 'Verification failed. The link may have expired.');
      }
    } catch (err) {
      console.error('Verification error:', err);
      setStatus('error');
      setMessage('Verification failed. Please try again or contact support.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #0A0E27 0%, #1a1f3a 100%)' }}>
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
        {status === 'loading' && (
          <>
            <div className="w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center" style={{ background: `${BLUE}20` }}>
              <svg className="animate-spin h-10 w-10" style={{ color: BLUE }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h1 className="text-2xl font-bold mb-2" style={{ color: BLUE }}>Verifying Domain...</h1>
            <p className="text-gray-600">Please wait while we verify your domain ownership</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-green-600 mb-2">✓ Verification Successful!</h1>
            <p className="text-gray-700 mb-4">
              <strong>{assetDomain}</strong> has been successfully verified.
            </p>
            <p className="text-sm text-gray-500 mb-6">
              You can now run deep security scans on this asset.
            </p>
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <p className="text-sm text-green-700">
                Redirecting to your assets page in 3 seconds...
              </p>
            </div>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center bg-red-100">
              <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-red-600 mb-2">Verification Failed</h1>
            <p className="text-gray-700 mb-6">{message}</p>
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
              <p className="text-sm text-red-700">
                The verification link may have expired or been used already.
              </p>
            </div>
            <button
              onClick={() => router.push('/dashboard/assets')}
              className="w-full py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
              style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
            >
              Go to Assets Page
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default function VerifyAssetPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #0A0E27 0%, #1a1f3a 100%)' }}>
        <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center" style={{ background: `${BLUE}20` }}>
            <svg className="animate-spin h-10 w-10" style={{ color: BLUE }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-2" style={{ color: BLUE }}>Loading...</h1>
        </div>
      </div>
    }>
      <VerifyAssetContent />
    </Suspense>
  );
}
