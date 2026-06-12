'use client';

import { useState } from 'react';

export default function BillingPage() {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<'starter' | 'business' | 'enterprise'>('business');
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'mobile'>('card');
  const [mobileProvider, setMobileProvider] = useState('mpesa');

  const currentPlan = {
    name: 'Business',
    price: 99,
    billingCycle: 'monthly',
    renewalDate: 'July 8, 2026',
    status: 'Active',
  };

  const usage = {
    checks: { used: 1248, limit: 'Unlimited', percentage: 0 },
    photoVerifications: { used: 342, limit: 'Unlimited', percentage: 0 },
    videoVerifications: { used: 127, limit: 'Unlimited', percentage: 0 },
    apiCalls: { used: 45678, limit: 100000, percentage: 45 },
    teamMembers: { used: 4, limit: 10, percentage: 40 },
  };

  const invoices = [
    { id: 'INV-2026-06', date: 'Jun 8, 2026', amount: 99, status: 'Paid', downloadUrl: '#' },
    { id: 'INV-2026-05', date: 'May 8, 2026', amount: 99, status: 'Paid', downloadUrl: '#' },
    { id: 'INV-2026-04', date: 'Apr 8, 2026', amount: 99, status: 'Paid', downloadUrl: '#' },
    { id: 'INV-2026-03', date: 'Mar 8, 2026', amount: 99, status: 'Paid', downloadUrl: '#' },
  ];

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      price: 29,
      features: ['200 checks/month', '100 photo verifications', '50 video verifications', 'API access', 'Email support'],
    },
    {
      id: 'business',
      name: 'Business',
      price: 99,
      features: ['Unlimited checks', 'Unlimited verifications', 'Priority support', 'Team collaboration (10 users)', 'WhatsApp alerts'],
      recommended: true,
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 'Custom',
      features: ['Everything in Business', 'Dedicated account manager', 'Custom AI training', '24/7 phone support', 'On-premise deployment'],
    },
  ];

  const handleUpgrade = () => {
    // TODO: Connect to payment gateway
    alert('Payment processing will be implemented with Stripe/PayStack!');
    setShowUpgradeModal(false);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Navigation */}
      <nav className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-sm" style={{ color: '#0047AB' }}>TechStartup Ltd</div>
                <div className="text-xs text-gray-500">Business Plan</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <a href="/dashboard" className="text-sm text-gray-600 hover:text-blue-700">← Back to Dashboard</a>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ color: '#0047AB' }}>
              Billing & Subscription
            </h1>
            <p className="text-gray-600">Manage your subscription and payment methods</p>
          </div>
          <button
            onClick={() => setShowUpgradeModal(true)}
            className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
            style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}
          >
            Upgrade Plan
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Current Plan */}
          <div className="lg:col-span-2 space-y-6">
            {/* Plan Card */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="text-sm text-gray-500 mb-1">Current Plan</div>
                  <h2 className="text-3xl font-bold mb-2" style={{ color: '#0047AB' }}>{currentPlan.name}</h2>
                  <div className="text-4xl font-bold mb-1" style={{ color: '#DAA520' }}>
                    ${currentPlan.price}
                    <span className="text-lg text-gray-500 font-normal">/month</span>
                  </div>
                </div>
                <span className="px-4 py-2 rounded-full bg-green-100 text-green-700 font-semibold text-sm">
                  {currentPlan.status}
                </span>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-blue-50 rounded-xl">
                  <div className="text-sm text-gray-600 mb-1">Billing Cycle</div>
                  <div className="font-semibold text-gray-900">{currentPlan.billingCycle}</div>
                </div>
                <div className="p-4 bg-blue-50 rounded-xl">
                  <div className="text-sm text-gray-600 mb-1">Next Renewal</div>
                  <div className="font-semibold text-gray-900">{currentPlan.renewalDate}</div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowUpgradeModal(true)}
                  className="flex-1 px-6 py-3 rounded-xl font-semibold text-white shadow-md hover:shadow-lg transition-all"
                  style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                >
                  Change Plan
                </button>
                <button className="flex-1 px-6 py-3 rounded-xl font-semibold border-2 hover:bg-gray-50 transition-all" style={{ borderColor: '#DC2626', color: '#DC2626' }}>
                  Cancel Subscription
                </button>
              </div>
            </div>

            {/* Usage Stats */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="text-xl font-bold mb-6" style={{ color: '#0047AB' }}>Usage This Month</h3>

              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">Security Checks</span>
                    <span className="text-sm text-gray-500">{usage.checks.used.toLocaleString()} / {usage.checks.limit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-blue-600 to-blue-400 h-2 rounded-full" style={{ width: `${usage.checks.percentage || 100}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">Photo Verifications</span>
                    <span className="text-sm text-gray-500">{usage.photoVerifications.used.toLocaleString()} / {usage.photoVerifications.limit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-green-600 to-green-400 h-2 rounded-full" style={{ width: `${usage.photoVerifications.percentage || 100}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">Video Verifications</span>
                    <span className="text-sm text-gray-500">{usage.videoVerifications.used.toLocaleString()} / {usage.videoVerifications.limit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-purple-600 to-purple-400 h-2 rounded-full" style={{ width: `${usage.videoVerifications.percentage || 100}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">API Calls</span>
                    <span className="text-sm text-gray-500">{usage.apiCalls.used.toLocaleString()} / {usage.apiCalls.limit.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-yellow-600 to-yellow-400 h-2 rounded-full" style={{ width: `${usage.apiCalls.percentage}%` }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">Team Members</span>
                    <span className="text-sm text-gray-500">{usage.teamMembers.used} / {usage.teamMembers.limit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-indigo-600 to-indigo-400 h-2 rounded-full" style={{ width: `${usage.teamMembers.percentage}%` }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Invoices */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="text-xl font-bold mb-6" style={{ color: '#0047AB' }}>Recent Invoices</h3>

              <div className="space-y-3">
                {invoices.map((invoice) => (
                  <div key={invoice.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">{invoice.id}</div>
                        <div className="text-sm text-gray-500">{invoice.date}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="font-bold text-gray-900">${invoice.amount}</div>
                        <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-xs font-semibold">
                          {invoice.status}
                        </span>
                      </div>
                      <a href={invoice.downloadUrl} className="p-2 hover:bg-gray-200 rounded-lg transition-all">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Payment Method */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4" style={{ color: '#0047AB' }}>Payment Method</h3>

              <div className="p-4 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl text-white mb-4">
                <div className="text-sm mb-2">Visa ending in</div>
                <div className="text-2xl font-bold mb-4">•••• 4242</div>
                <div className="flex items-center justify-between text-sm">
                  <span>Expires 12/26</span>
                  <svg className="w-10 h-6" viewBox="0 0 48 32" fill="none">
                    <rect width="48" height="32" rx="4" fill="white" fillOpacity="0.2"/>
                    <text x="24" y="20" fill="white" fontSize="12" fontWeight="bold" textAnchor="middle">VISA</text>
                  </svg>
                </div>
              </div>

              <button className="w-full px-4 py-3 border-2 border-blue-200 rounded-xl font-semibold text-blue-700 hover:bg-blue-50 transition-all">
                Update Payment Method
              </button>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4" style={{ color: '#0047AB' }}>Quick Actions</h3>

              <div className="space-y-3">
                <button className="w-full px-4 py-3 bg-blue-50 text-blue-700 rounded-xl font-semibold text-sm hover:bg-blue-100 transition-all text-left">
                  Download All Invoices
                </button>
                <button className="w-full px-4 py-3 bg-blue-50 text-blue-700 rounded-xl font-semibold text-sm hover:bg-blue-100 transition-all text-left">
                  Update Billing Email
                </button>
                <button className="w-full px-4 py-3 bg-blue-50 text-blue-700 rounded-xl font-semibold text-sm hover:bg-blue-100 transition-all text-left">
                  Tax Information
                </button>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl shadow-lg p-6 border-2 border-green-200">
              <div className="flex items-start gap-3 mb-4">
                <svg className="w-6 h-6 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="font-bold text-green-900 mb-1">Mobile Money Supported</h4>
                  <p className="text-sm text-green-800">Pay with M-Pesa, MTN Mobile Money, or Airtel Money</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full p-8 my-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold" style={{ color: '#0047AB' }}>Choose Your Plan</h2>
              <button
                onClick={() => setShowUpgradeModal(false)}
                className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Plan Selection */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              {plans.map((plan: any) => (
                <div
                  key={plan.id}
                  onClick={() => setSelectedPlan(plan.id)}
                  className={`p-6 rounded-2xl border-2 cursor-pointer transition-all ${
                    selectedPlan === plan.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${plan.recommended ? 'ring-4 ring-blue-200' : ''}`}
                >
                  {plan.recommended && (
                    <div className="bg-gradient-to-r from-blue-600 to-blue-400 text-white text-xs font-bold px-3 py-1 rounded-full mb-3 inline-block">
                      RECOMMENDED
                    </div>
                  )}
                  <h3 className="text-xl font-bold mb-2" style={{ color: '#0047AB' }}>{plan.name}</h3>
                  <div className="text-3xl font-bold mb-4" style={{ color: '#DAA520' }}>
                    {typeof plan.price === 'number' ? `$${plan.price}` : plan.price}
                    {typeof plan.price === 'number' && <span className="text-sm text-gray-500">/mo</span>}
                  </div>
                  <ul className="space-y-2">
                    {plan.features.map((feature: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            {/* Payment Method Selection */}
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-4" style={{ color: '#0047AB' }}>Payment Method</h3>

              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <button
                  onClick={() => setPaymentMethod('card')}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    paymentMethod === 'card' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <svg className="w-8 h-8" style={{ color: paymentMethod === 'card' ? '#0047AB' : '#6B7280' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                    </svg>
                    <div className="text-left">
                      <div className="font-semibold">Credit/Debit Card</div>
                      <div className="text-sm text-gray-500">Visa, Mastercard, Amex</div>
                    </div>
                  </div>
                </button>

                <button
                  onClick={() => setPaymentMethod('mobile')}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    paymentMethod === 'mobile' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <svg className="w-8 h-8" style={{ color: paymentMethod === 'mobile' ? '#0047AB' : '#6B7280' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <div className="text-left">
                      <div className="font-semibold">Mobile Money</div>
                      <div className="text-sm text-gray-500">M-Pesa, MTN, Airtel</div>
                    </div>
                  </div>
                </button>
              </div>

              {paymentMethod === 'mobile' && (
                <div>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#0047AB' }}>
                    Select Provider
                  </label>
                  <select
                    value={mobileProvider}
                    onChange={(e) => setMobileProvider(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all"
                  >
                    <option value="mpesa">M-Pesa (Kenya, Tanzania, etc.)</option>
                    <option value="mtn">MTN Mobile Money</option>
                    <option value="airtel">Airtel Money</option>
                    <option value="orange">Orange Money</option>
                    <option value="vodacom">Vodacom M-Pesa</option>
                  </select>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => setShowUpgradeModal(false)}
                className="flex-1 px-6 py-4 border-2 rounded-xl font-semibold hover:bg-gray-50 transition-all"
                style={{ borderColor: '#0047AB', color: '#0047AB' }}
              >
                Cancel
              </button>
              <button
                onClick={handleUpgrade}
                className="flex-1 px-6 py-4 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
                style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
              >
                {paymentMethod === 'card' ? 'Continue to Payment' : 'Pay with Mobile Money'}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
