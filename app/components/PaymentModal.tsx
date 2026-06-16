'use client';

import { useState, useEffect } from 'react';
import { config } from '@/lib/config';

interface PaymentModalProps {
  plan: string;
  amount?: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function PaymentModal({ plan, amount, onClose, onSuccess }: PaymentModalProps) {
  const [paymentMethod, setPaymentMethod] = useState<'mobile' | 'crypto'>('mobile');
  const [step, setStep] = useState<'details' | 'processing' | 'success'>('details');
  const [country, setCountry] = useState('RW');
  const [operator, setOperator] = useState('MTN');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [cryptoToken, setCryptoToken] = useState('USDT');
  const [walletAddress, setWalletAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pricing, setPricing] = useState<any>(null);
  const [depositAddress, setDepositAddress] = useState('');
  const [depositAmount, setDepositAmount] = useState('');

  useEffect(() => {
    const fetchPricing = async () => {
      try {
        const res = await fetch(`${config.apiUrl}/api/payments/pricing/${country}`);
        if (res.ok) {
          const data = await res.json();
          setPricing(data);
        }
      } catch (error) {
        console.error('Failed to fetch pricing:', error);
      }
    };

    fetchPricing();
  }, [country]);

  const operators: Record<string, string[]> = {
    RW: ['MTN', 'AIRTEL'],
    KE: ['MPESA', 'AIRTEL'],
    UG: ['MTN', 'AIRTEL'],
    TZ: ['VODACOM', 'AIRTEL', 'TIGO'],
    ZM: ['MTN', 'AIRTEL'],
    GH: ['MTN', 'VODAFONE', 'AIRTELTIGO'],
    CM: ['MTN', 'ORANGE'],
    CI: ['MTN', 'ORANGE', 'MOOV'],
    SN: ['ORANGE', 'FREE'],
    BJ: ['MTN', 'MOOV'],
  };

  const countries = [
    { code: 'RW', name: 'Rwanda', flag: '🇷🇼' },
    { code: 'KE', name: 'Kenya', flag: '🇰🇪' },
    { code: 'UG', name: 'Uganda', flag: '🇺🇬' },
    { code: 'TZ', name: 'Tanzania', flag: '🇹🇿' },
    { code: 'ZM', name: 'Zambia', flag: '🇿🇲' },
    { code: 'GH', name: 'Ghana', flag: '🇬🇭' },
    { code: 'CM', name: 'Cameroon', flag: '🇨🇲' },
    { code: 'CI', name: 'Côte d\'Ivoire', flag: '🇨🇮' },
    { code: 'SN', name: 'Senegal', flag: '🇸🇳' },
    { code: 'BJ', name: 'Benin', flag: '🇧🇯' },
  ];

  const handlePayment = async () => {
    if (paymentMethod === 'mobile' && !phoneNumber) {
      setError('Please enter your phone number');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('auth_token');

      if (paymentMethod === 'mobile') {
        const res = await fetch(`${config.apiUrl}/api/payments/initiate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            plan_name: plan.toLowerCase(),
            phone_number: phoneNumber,
            country: country,
            operator: operator
          })
        });

        const data = await res.json();

        if (res.ok) {
          setStep('processing');
          pollPaymentStatus(data.payment_id);
        } else {
          setError(data.detail || 'Payment initiation failed');
        }
      } else {
        // Crypto payment
        const res = await fetch(`${config.apiUrl}/api/payments/initiate-crypto`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            plan_name: plan.toLowerCase(),
            token_symbol: cryptoToken
          })
        });

        const data = await res.json();

        if (res.ok) {
          // Store payment details
          setDepositAddress(data.payment_details.payment_wallet);
          setDepositAmount(data.payment_details.amount_usd);
          setError(''); // Clear any previous errors
          setStep('processing');
          pollPaymentStatus(data.payment_id);
        } else {
          setError(data.detail || 'Payment initiation failed');
        }
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const pollPaymentStatus = async (paymentId: string) => {
    const maxAttempts = 30; // 5 minutes
    let attempts = 0;

    const interval = setInterval(async () => {
      attempts++;

      try {
        const token = localStorage.getItem('auth_token');
        const res = await fetch(`${config.apiUrl}/api/payments/status/${paymentId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await res.json();

        if (data.status === 'completed') {
          clearInterval(interval);
          setStep('success');
          setTimeout(() => {
            onSuccess();
            onClose();
          }, 2000);
        } else if (data.status === 'failed' || attempts >= maxAttempts) {
          clearInterval(interval);
          setError('Payment failed or timed out. Please try again.');
          setStep('details');
        }
      } catch {
        clearInterval(interval);
        setError('Failed to check payment status');
        setStep('details');
      }
    }, 10000);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl">
        {step === 'details' && (
          <>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Complete Payment</h2>
              <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-6 p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border-2 border-blue-200">
              <div className="text-sm text-gray-600 mb-1">Selected Plan</div>
              <div className="text-2xl font-bold text-blue-700 capitalize">{plan}</div>
              {paymentMethod === 'mobile' && pricing ? (
                <div className="text-3xl font-bold text-gray-900">
                  {parseInt(pricing[plan.toLowerCase()] || amount || '0').toLocaleString()} {pricing.currency}
                  <span className="text-lg text-gray-600">/month</span>
                </div>
              ) : (
                <div className="text-3xl font-bold text-gray-900">
                  ${amount || (plan === 'starter' ? '49' : plan === 'professional' ? '199' : '999')}
                  <span className="text-lg text-gray-600">/month</span>
                </div>
              )}
            </div>

            {/* Payment Method Selector */}
            <div className="mb-6">
              <label className="block text-sm font-semibold mb-3 text-gray-700">Payment Method</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setPaymentMethod('mobile')}
                  className={`p-4 rounded-xl border-2 transition ${
                    paymentMethod === 'mobile'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-2">📱</div>
                  <div className="font-semibold text-gray-900">Mobile Money</div>
                  <div className="text-xs text-gray-500">MTN, Airtel, M-Pesa</div>
                </button>
                <button
                  type="button"
                  onClick={() => setPaymentMethod('crypto')}
                  className={`p-4 rounded-xl border-2 transition ${
                    paymentMethod === 'crypto'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-2">🪙</div>
                  <div className="font-semibold text-gray-900">Crypto</div>
                  <div className="text-xs text-gray-500">USDT, USDC</div>
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {paymentMethod === 'mobile' ? (
                <>
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Country</label>
                    <select
                      value={country}
                      onChange={(e) => {
                        setCountry(e.target.value);
                        setOperator(operators[e.target.value][0]);
                      }}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition text-gray-900 font-medium"
                    >
                      {countries.map((c) => (
                        <option key={c.code} value={c.code}>{c.flag} {c.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Mobile Money Operator</label>
                    <select
                      value={operator}
                      onChange={(e) => setOperator(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition text-gray-900 font-medium"
                    >
                      {operators[country].map((op) => (
                        <option key={op} value={op}>{op}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Phone Number</label>
                    <input
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="+250788123456"
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition text-gray-900 font-medium placeholder-gray-400"
                    />
                    <p className="text-xs text-gray-500 mt-1">Include country code (e.g., +250 for Rwanda)</p>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Cryptocurrency</label>
                    <select
                      value={cryptoToken}
                      onChange={(e) => setCryptoToken(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition text-gray-900 font-medium"
                    >
                      <option value="USDT">USDT (Tether)</option>
                      <option value="USDC">USDC (USD Coin)</option>
                    </select>
                  </div>

                  <div className="p-4 bg-blue-50 border-2 border-blue-200 rounded-xl">
                    <div className="flex items-start gap-2">
                      <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div className="text-sm text-blue-800">
                        <p className="font-semibold mb-1">How it works</p>
                        <p>1. Click "Pay Now" to generate your deposit address</p>
                        <p>2. Send {cryptoToken} from your wallet to the address</p>
                        <p>3. Wait for blockchain confirmation</p>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-yellow-50 border-2 border-yellow-200 rounded-xl">
                    <div className="flex items-start gap-2">
                      <svg className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <div className="text-sm text-yellow-800">
                        <p className="font-semibold mb-1">⚠️ Polygon Network Only</p>
                        <p>Send on <strong>Polygon (MATIC)</strong> network, NOT Ethereum!</p>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {error && (
                <div className="p-4 bg-red-50 border-2 border-red-200 rounded-xl">
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  onClick={onClose}
                  className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-xl font-semibold text-gray-700 hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handlePayment}
                  disabled={loading || (paymentMethod === 'mobile' && !phoneNumber)}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:from-blue-700 hover:to-blue-800 transition shadow-lg"
                >
                  {loading ? 'Processing...' : 'Pay Now'}
                </button>
              </div>
            </div>
          </>
        )}

        {step === 'processing' && (
          <div className="text-center py-12">
            {paymentMethod === 'mobile' ? (
              <>
                <div className="text-7xl mb-6">📱</div>
                <h3 className="text-2xl font-bold mb-3 text-gray-900">Complete on Your Phone</h3>
                <p className="text-gray-600 mb-6 text-lg">
                  Check your phone for the payment prompt from <strong>{operator}</strong>
                </p>
                <div className="flex justify-center mb-4">
                  <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full"></div>
                </div>
                <p className="text-sm text-gray-500">Waiting for payment confirmation...</p>
              </>
            ) : (
              <>
                <div className="text-7xl mb-6">🪙</div>
                <h3 className="text-2xl font-bold mb-3 text-gray-900">Send Crypto Payment</h3>
                <p className="text-gray-600 mb-2 text-lg">
                  Send <strong>${depositAmount} {cryptoToken}</strong> to:
                </p>

                {depositAddress ? (
                  <>
                    <div className="relative mb-4">
                      <div className="p-4 bg-gray-100 rounded-xl break-all font-mono text-sm text-gray-900 border-2 border-gray-300">
                        {depositAddress}
                      </div>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(depositAddress);
                          alert('Address copied!');
                        }}
                        className="absolute top-2 right-2 p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
                        title="Copy address"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                    </div>

                    <div className="mb-6 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-xl text-left">
                      <p className="text-sm text-yellow-800 mb-2">
                        <strong>⚠️ Important:</strong>
                      </p>
                      <ul className="text-sm text-yellow-800 space-y-1">
                        <li>• Send on <strong>Polygon network</strong> (NOT Ethereum!)</li>
                        <li>• Amount: <strong>${depositAmount} {cryptoToken}</strong></li>
                        <li>• Confirmation takes 1-2 minutes</li>
                      </ul>
                    </div>

                    <div className="flex justify-center mb-4">
                      <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full"></div>
                    </div>
                    <p className="text-sm text-gray-500">Waiting for blockchain confirmation...</p>
                  </>
                ) : (
                  <div className="p-8">
                    <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
                    <p className="text-sm text-gray-500 mt-4">Generating deposit address...</p>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {step === 'success' && (
          <div className="text-center py-12">
            <div className="text-7xl mb-6">✅</div>
            <h3 className="text-2xl font-bold mb-3 text-green-600">Payment Successful!</h3>
            <p className="text-gray-600 text-lg">Your subscription is now active</p>
          </div>
        )}
      </div>
    </div>
  );
}
