'use client';

import { useState, useEffect } from 'react';
import PaymentModal from './PaymentModal';

export default function CreditsWidget() {
  const [credits, setCredits] = useState<number>(0);
  const [plan, setPlan] = useState<string>('free');
  const [loading, setLoading] = useState(true);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<{ name: string; amount: string } | null>(null);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/payments/subscription', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        const data = await res.json();
        setCredits(data.credits_remaining || 0);
        setPlan(data.plan || 'free');
      }
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = (planName: string, amount: string) => {
    setSelectedPlan({ name: planName, amount });
    setShowPaymentModal(true);
  };

  const handlePaymentSuccess = () => {
    fetchSubscription();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-gray-100">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  const isLowCredits = credits < 10;
  const isFree = plan === 'free';

  return (
    <>
      <div className={`bg-gradient-to-br ${isLowCredits ? 'from-red-50 to-red-100 border-red-200' : 'from-blue-50 to-blue-100 border-blue-200'} rounded-xl shadow-lg p-6 border-2`}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="text-sm font-semibold text-gray-600 mb-1">Your Credits</div>
            <div className={`text-4xl font-bold ${isLowCredits ? 'text-red-600' : 'text-blue-700'}`}>
              {credits}
            </div>
            <div className="text-sm text-gray-600 mt-1 capitalize">
              {plan} Plan
            </div>
          </div>
          <div className={`w-16 h-16 rounded-full ${isLowCredits ? 'bg-red-200' : 'bg-blue-200'} flex items-center justify-center`}>
            <svg className={`w-8 h-8 ${isLowCredits ? 'text-red-600' : 'text-blue-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        {isLowCredits && (
          <div className="mb-4 p-3 bg-red-100 border-2 border-red-200 rounded-lg">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-sm text-red-700 font-medium">
                Low credits! Upgrade to continue using services.
              </p>
            </div>
          </div>
        )}

        <div className="text-xs text-gray-600 mb-4">
          <div className="flex justify-between mb-1">
            <span>Service costs:</span>
          </div>
          <div className="space-y-1">
            <div className="flex justify-between">
              <span>• Website scan</span>
              <span className="font-semibold">1 credit</span>
            </div>
            <div className="flex justify-between">
              <span>• Company report</span>
              <span className="font-semibold">5 credits</span>
            </div>
            <div className="flex justify-between">
              <span>• Mobile app scan</span>
              <span className="font-semibold">2 credits</span>
            </div>
          </div>
        </div>

        {isFree ? (
          <div className="space-y-2">
            <button
              onClick={() => handleUpgrade('Personal', '5')}
              className="w-full px-4 py-3 border-2 border-blue-600 text-blue-700 rounded-lg font-semibold hover:bg-blue-50 transition"
            >
              Upgrade to Personal - $5/mo
            </button>
            <button
              onClick={() => handleUpgrade('Professional', '49')}
              className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition shadow-md"
            >
              Upgrade to Pro - $49/mo
            </button>
          </div>
        ) : (
          <button
            onClick={() => window.location.href = '/pricing'}
            className="w-full px-4 py-3 border-2 border-blue-600 text-blue-700 rounded-lg font-semibold hover:bg-blue-50 transition"
          >
            View All Plans
          </button>
        )}
      </div>

      {showPaymentModal && selectedPlan && (
        <PaymentModal
          plan={selectedPlan.name}
          amount={selectedPlan.amount}
          onClose={() => setShowPaymentModal(false)}
          onSuccess={handlePaymentSuccess}
        />
      )}
    </>
  );
}
