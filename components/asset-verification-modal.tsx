'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';

interface VerificationModalProps {
  assetId: string;
  domain: string;
  onClose: () => void;
  onVerified: () => void;
}

export function AssetVerificationModal({ assetId, domain, onClose, onVerified }: VerificationModalProps) {
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [instructions, setInstructions] = useState<any>(null);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    loadVerificationInstructions();
  }, [assetId]);

  const loadVerificationInstructions = async () => {
    try {
      const response = await fetch(`/api/assets/${assetId}/verify/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setInstructions(data.instructions);
      } else {
        setError('Failed to load verification instructions');
      }
    } catch (err) {
      setError('Failed to load verification instructions');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    setVerifying(true);
    setError('');

    try {
      const response = await fetch(`/api/assets/${assetId}/verify/check`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.verified) {
          // Auto-trigger security scan after verification
          try {
            await fetch(`/api/scans/assets/${assetId}/scan`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
          } catch (scanErr) {
            console.log('Auto-scan failed:', scanErr);
          }
          onVerified();
        } else {
          setError(data.message || 'Verification failed. Please check your setup and try again.');
        }
      } else {
        setError('Verification check failed');
      }
    } catch (err) {
      setError('Verification failed. Please try again.');
    } finally {
      setVerifying(false);
    }
  };

  const handleSendEmail = async () => {
    setSendingEmail(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await fetch(`/api/assets/${assetId}/verify/email/send`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEmailSent(true);
        setSuccessMessage(`Verification email sent to ${data.email}. Check your inbox and click the link to verify!`);
      } else {
        setError('Failed to send verification email');
      }
    } catch (err) {
      setError('Failed to send email. Please try again.');
    } finally {
      setSendingEmail(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="w-16 h-16 border-4 border-t-blue-600 border-blue-200 rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full p-8 max-h-[90vh] overflow-y-auto">
        <h2 className="text-3xl font-bold mb-6" style={{ color: '#0047AB' }}>
          Verify Domain Ownership
        </h2>

        <p className="text-gray-600 mb-8">
          Choose one of the following methods to verify ownership of <strong>{domain}</strong>
        </p>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded mb-6">
            <p className="text-green-700">{successMessage}</p>
          </div>
        )}

        {/* DNS TXT Record - Recommended */}
        <div className="border-2 border-blue-500 rounded-2xl p-6 mb-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold mb-2" style={{ color: '#0047AB' }}>
                DNS TXT Record <span className="text-sm text-white bg-blue-500 px-2 py-1 rounded">Recommended</span>
              </h3>
              <p className="text-gray-600 mb-4">
                Add a TXT record to your domain's DNS settings
              </p>
              <div className="bg-gray-100 rounded-xl p-4 font-mono text-sm text-gray-900">
                <div className="mb-2">
                  <span className="font-bold text-gray-900">Name:</span> <span className="text-blue-600">{instructions?.dns_txt?.name}</span>
                </div>
                <div>
                  <span className="font-bold text-gray-900">Value:</span> <span className="text-blue-600 break-all">{instructions?.dns_txt?.value}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* HTML File Upload */}
        <div className="border-2 border-gray-200 rounded-2xl p-6 mb-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 bg-yellow-500">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold mb-2 text-yellow-600">
                HTML File Upload
              </h3>
              <p className="text-gray-600 mb-4">
                Upload a verification file to your website root
              </p>
              <div className="bg-gray-100 rounded-xl p-4 font-mono text-sm text-gray-900">
                <div className="mb-2">
                  <span className="font-bold text-gray-900">File:</span> <span className="text-yellow-600">{instructions?.html_file?.filename}</span>
                </div>
                <div>
                  <span className="font-bold text-gray-900">URL:</span> <span className="text-yellow-600 break-all">{instructions?.html_file?.url}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Email Verification */}
        <div className="border-2 border-green-500 rounded-2xl p-6 mb-8 bg-green-50">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold mb-2 text-green-700">
                Email Verification ⚡ Easiest Method
              </h3>
              <p className="text-gray-700 mb-4">
                We'll send a verification link to <strong>{instructions?.email?.email}</strong>
              </p>
              {emailSent ? (
                <div className="bg-white border-2 border-green-500 rounded-xl p-4">
                  <p className="text-green-700 font-semibold">✅ Email Sent!</p>
                  <p className="text-sm text-gray-600 mt-1">
                    Check your inbox and click the verification link. The page will update automatically.
                  </p>
                </div>
              ) : (
                <button
                  onClick={handleSendEmail}
                  disabled={sendingEmail}
                  className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50"
                  style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
                >
                  {sendingEmail ? 'Sending...' : '📧 Send Verification Email'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={onClose}
            className="flex-1 py-4 rounded-xl font-semibold border-2 border-gray-300 hover:bg-gray-50 transition-colors"
          >
            Back
          </button>
          <button
            onClick={handleVerify}
            disabled={verifying}
            className="flex-1 py-4 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50"
            style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
          >
            {verifying ? 'Verifying...' : 'Verify & Complete Setup'}
          </button>
        </div>
      </div>
    </div>
  );
}
