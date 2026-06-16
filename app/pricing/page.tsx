'use client';

import { useState } from 'react';

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  const plans = [
    {
      name: 'Starter',
      price: 15,
      annualPrice: 150,
      description: 'For small businesses and startups',
      features: [
        'Up to 5 assets',
        'Weekly security scans',
        'Vulnerability scanning',
        'Email alerts',
        'Scan history dashboard',
        'PDF reports',
        'Email support',
        'Pay with Mobile Money or Crypto'
      ],
      cta: 'Start 14-Day Trial',
      ctaLink: '/signup?plan=starter',
      popular: false,
      color: 'blue'
    },
    {
      name: 'Professional',
      price: 79,
      annualPrice: 790,
      description: 'For businesses and professionals',
      features: [
        'Everything in Personal',
        'Full business dashboard',
        'Deep vulnerability scanning',
        'SSL/TLS monitoring',
        'API security testing',
        'Continuous monitoring',
        'Email + SMS alerts',
        'PDF security reports',
        'Priority support',
        '5 team members'
      ],
      cta: 'Start 14-Day Trial',
      ctaLink: '/signup?plan=professional',
      popular: true,
      color: 'blue'
    },
    {
      name: 'Enterprise',
      price: 299,
      annualPrice: 2990,
      description: 'For large organizations',
      features: [
        'Everything in Professional',
        'Custom security policies',
        'Industry-specific compliance',
        'Network infrastructure scanning',
        'Dedicated security analyst',
        'WhatsApp + Slack alerts',
        'Custom integrations',
        'SLA guarantees',
        'On-premise deployment option',
        'Unlimited team members',
        '24/7 phone support'
      ],
      cta: 'Contact Sales',
      ctaLink: '/contact?plan=enterprise',
      popular: false,
      color: 'gold'
    }
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
      {/* Navigation Bar */}
      <nav className="border-b border-blue-900/50 bg-slate-900/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <a href="/" className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-xl tracking-tight">
                  <span style={{ color: '#0047AB' }}>AFRICA </span>
                  <span style={{ color: '#DAA520' }}>CYBER TRUST</span>
                </div>
                <div className="text-xs text-gray-400 tracking-widest">INFRASTRUCTURE</div>
              </div>
            </a>
            <div className="hidden md:flex gap-6 items-center">
              <a href="/" className="text-gray-300 hover:text-blue-400 transition font-medium">Home</a>
              <a href="/about" className="text-gray-300 hover:text-blue-400 transition font-medium">About</a>
              <a href="/pricing" className="text-blue-400 font-semibold">Pricing</a>
              <a href="/business" className="text-gray-300 hover:text-blue-400 transition font-medium">For Business</a>
              <a href="/contact" className="text-gray-300 hover:text-blue-400 transition font-medium">Contact</a>
              <a href="/login" className="text-gray-300 hover:text-blue-400 transition font-medium">Login</a>
              <a
                href="/signup"
                className="px-6 py-2.5 rounded-xl font-semibold text-white shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-all"
                style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
              >
                Get Started
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="text-center mb-16 max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full mb-8 border border-blue-400/30 shadow-lg shadow-blue-500/20" style={{ background: 'linear-gradient(135deg, rgba(0, 71, 171, 0.2) 0%, rgba(218, 165, 32, 0.2) 100%)' }}>
            <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-bold text-blue-300 tracking-wide">TRANSPARENT PRICING</span>
          </div>

          <h1 className="text-6xl font-extrabold mb-6 leading-tight tracking-tight">
            <span style={{ color: '#0047AB', textShadow: '0 0 40px rgba(0, 71, 171, 0.3)' }}>
              Choose Your
            </span>
            <br />
            <span style={{ color: '#DAA520', textShadow: '0 0 40px rgba(218, 165, 32, 0.3)' }}>
              Security Plan
            </span>
          </h1>

          <p className="text-xl text-gray-300 mb-8">
            Comprehensive security monitoring for African businesses. Start with a 14-day free trial, plans from $15/month.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center gap-4 bg-slate-800/60 backdrop-blur-sm p-2 rounded-xl border border-blue-900/30">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-lg font-semibold transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`px-6 py-2 rounded-lg font-semibold transition-all ${
                billingCycle === 'annual'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Annual
              <span className="ml-2 text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">
                Save 17%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative bg-slate-800/40 backdrop-blur-sm rounded-3xl p-8 border transition-all hover:scale-105 ${
                plan.popular
                  ? 'border-blue-500 shadow-2xl shadow-blue-500/20 ring-2 ring-blue-500/50'
                  : 'border-blue-900/30 hover:border-blue-500/50'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="px-6 py-2 rounded-full font-bold text-sm text-white shadow-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                    ⭐ MOST POPULAR
                  </div>
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-3xl font-bold mb-3 text-white">{plan.name}</h3>
                <p className="text-gray-400 text-sm">{plan.description}</p>
              </div>

              <div className="text-center mb-8">
                {plan.price === null ? (
                  <div className="text-4xl font-extrabold text-white mb-2">Custom Pricing</div>
                ) : (
                  <>
                    <div className="text-6xl font-extrabold mb-2" style={{ color: plan.color === 'blue' ? '#0047AB' : '#DAA520' }}>
                      ${billingCycle === 'monthly' ? plan.price : Math.floor((plan.annualPrice || 0) / 12)}
                    </div>
                    <div className="text-gray-400">
                      per month{billingCycle === 'annual' && ', billed annually'}
                    </div>
                    {billingCycle === 'annual' && plan.annualPrice && (
                      <div className="text-sm text-green-400 mt-2">
                        Save ${((plan.price || 0) * 12) - plan.annualPrice} per year
                      </div>
                    )}
                  </>
                )}
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <svg className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: plan.color === 'blue' ? '#0047AB' : plan.color === 'gold' ? '#DAA520' : '#10B981' }} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-300 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <a
                href={plan.ctaLink}
                className={`block w-full py-4 rounded-xl font-bold text-center transition-all shadow-lg hover:shadow-xl ${
                  plan.popular
                    ? 'text-white'
                    : plan.color === 'gold'
                    ? 'text-white'
                    : 'text-white bg-slate-700 hover:bg-slate-600'
                }`}
                style={
                  plan.popular
                    ? { background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }
                    : plan.color === 'gold'
                    ? { background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }
                    : {}
                }
              >
                {plan.cta}
              </a>
            </div>
          ))}
        </div>

        {/* Add-ons Section */}
        <div className="max-w-7xl mx-auto mt-20">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">Add-Ons & Extras</h2>
            <p className="text-gray-400">Enhance your plan with additional features</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border border-blue-900/30">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">Additional Team Members</h3>
                  <p className="text-gray-400 text-sm mb-4">Add more users to your team account</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold" style={{ color: '#0047AB' }}>$20</span>
                    <span className="text-gray-400">per user/month</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border border-blue-900/30">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}>
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">Compliance Reports</h3>
                  <p className="text-gray-400 text-sm mb-4">PCI-DSS, HIPAA, SOC 2 compliance reports</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold" style={{ color: '#DAA520' }}>$79</span>
                    <span className="text-gray-400">per report</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="max-w-4xl mx-auto mt-24">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">Frequently Asked Questions</h2>
            <p className="text-gray-400">Have questions? We have answers.</p>
          </div>

          <div className="space-y-4">
            {[
              {
                q: 'Can I switch plans anytime?',
                a: 'Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately, and we prorate any billing adjustments.'
              },
              {
                q: 'What payment methods do you accept?',
                a: 'We accept mobile money (MTN, Airtel, M-Pesa, Orange, etc. in 20 African countries) and cryptocurrency (USDT/USDC on Polygon). Pay in your local currency!'
              },
              {
                q: 'Is there a free trial?',
                a: 'Yes! Personal plan comes with a 7-day free trial, and Professional has a 14-day free trial. No payment required to start your trial.'
              },
              {
                q: 'Can I use this without a subscription?',
                a: 'Yes! You can use the home page for 1 free scan per day without creating an account. For business monitoring with unlimited assets, upgrade to Professional ($79/month).'
              }
            ].map((faq, i) => (
              <div key={i} className="bg-slate-800/40 backdrop-blur-sm rounded-xl p-6 border border-blue-900/30">
                <h3 className="text-lg font-bold text-white mb-2">{faq.q}</h3>
                <p className="text-gray-400">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center mt-20">
          <h2 className="text-4xl font-bold mb-6 text-white">Ready to Get Started?</h2>
          <p className="text-xl text-gray-400 mb-8">Join thousands of businesses protecting their digital assets with Africa Cyber Trust.</p>
          <div className="flex gap-4 justify-center">
            <a
              href="/signup"
              className="px-12 py-5 rounded-xl font-bold text-white shadow-2xl shadow-blue-500/40 hover:shadow-blue-500/60 transition-all text-lg"
              style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
            >
              Start Free Trial
            </a>
            <a
              href="/contact"
              className="px-12 py-5 rounded-xl font-bold border-2 hover:bg-blue-950/50 transition-all text-lg backdrop-blur-sm"
              style={{ borderColor: '#DAA520', color: '#DAA520' }}
            >
              Contact Sales
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/50 backdrop-blur-xl mt-20">
        <div className="container mx-auto px-4 py-12">
          <div className="text-center text-sm text-gray-500">
            <p>© 2026 Africa Cyber Trust Infrastructure. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
