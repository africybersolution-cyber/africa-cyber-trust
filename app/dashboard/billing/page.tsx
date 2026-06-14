'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { config } from '@/lib/config';
import DashboardLayout from '@/components/DashboardLayout';
import PaymentModal from '../../components/PaymentModal';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

interface SubscriptionInfo {
  plan: string;
  status: string;
  trial_active: boolean;
  days_remaining: number;
  expires_at: string | null;
}

export default function BillingPage() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [currentPlan, setCurrentPlan] = useState('professional');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<{name: string, price: string} | null>(null);

  // Load subscription data
  useEffect(() => {
    const loadSubscription = async () => {
      if (!token) return;

      try {
        const res = await fetch(`${config.apiUrl}/api/payments/subscription`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (res.ok) {
          const data = await res.json();
          setSubscription(data);
          setCurrentPlan(data.plan || 'starter');
        }
      } catch (error) {
        console.error('Error loading subscription:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSubscription();
  }, [token]);

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      price: '$19',
      period: '/month',
      features: [
        'Dashboard access',
        'Vulnerability scanning',
        'Up to 5 assets',
        'Email notifications',
        'Scan history',
        'Email support',
        'Pay with Mobile Money or Crypto'
      ],
      recommended: false
    },
    {
      id: 'professional',
      name: 'Professional',
      price: '$69',
      period: '/month',
      features: [
        'Everything in Starter',
        'Unlimited assets',
        'Advanced vulnerability scanning',
        'AI risk scoring & prioritization',
        'Up to 10 team members',
        'Priority support',
        'Advanced reports & compliance'
      ],
      recommended: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: '$199',
      period: '/month',
      features: [
        'Everything in Professional',
        'Unlimited team members',
        '24/7 dedicated security analyst',
        'Custom integrations & API access',
        'SSO integration',
        'Custom SLA',
        'Dedicated account manager',
        'White-label options'
      ],
      recommended: false
    }
  ];

  const invoices = [
    { id: 1, date: 'Jun 1, 2026', amount: '$69.00', status: 'Paid', plan: 'Professional' },
    { id: 2, date: 'May 1, 2026', amount: '$69.00', status: 'Paid', plan: 'Professional' },
    { id: 3, date: 'Apr 1, 2026', amount: '$69.00', status: 'Paid', plan: 'Professional' },
  ];

  const handleChangePlan = (planId: string) => {
    const plan = plans.find(p => p.id === planId);
    if (!plan) return;

    // Open payment modal for all plans (Starter, Professional, Enterprise)
    setSelectedPlan({
      name: plan.name,
      price: plan.price.replace('$', '')
    });
    setShowPaymentModal(true);
  };

  const handlePaymentSuccess = () => {
    // Reload subscription data
    if (token) {
      fetch(`${config.apiUrl}/api/payments/subscription`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(data => {
        setSubscription(data);
        setCurrentPlan(data.plan || 'starter');
      });
    }
  };

  return (
    <DashboardLayout title="Billing" subtitle="Manage your subscription and payment methods">
      <div className="space-y-8">
        {/* Trial Banner */}
        {subscription?.trial_active && (
          <div className="bg-blue-900/30 border-2 border-blue-500/50 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-blue-400 mb-2">
                  Free Trial Active - {subscription.days_remaining} Days Remaining
                </h3>
                <p className="text-gray-300">
                  You're trying out the <span className="font-semibold capitalize">{subscription.plan}</span> plan.
                  Upgrade before your trial ends to keep all features.
                </p>
              </div>
              <a
                href="#available-plans"
                className="px-6 py-3 rounded-xl font-semibold text-white whitespace-nowrap"
                style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
              >
                Upgrade Now
              </a>
            </div>
          </div>
        )}

        {/* Current Plan */}
        <div className="cyber-card-raised p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">Current Plan</h2>
              <p className="text-cyber-muted text-sm">
                You're currently on the{' '}
                <span className="capitalize">{subscription?.plan || 'Starter'}</span> plan
                {subscription?.trial_active && ' (Trial)'}
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-white">
                {subscription?.plan === 'starter' ? '$19' : subscription?.plan === 'professional' ? '$69' : '$199'}
              </div>
              <div className="text-sm text-cyber-muted">
                per month
              </div>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-2xl font-bold text-white">5</div>
              <div className="text-xs text-cyber-muted">Team Members</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-2xl font-bold text-green-400">∞</div>
              <div className="text-xs text-cyber-muted">Scans</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-2xl font-bold" style={{ color: BLUE }}>✓</div>
              <div className="text-xs text-cyber-muted">Dashboard Access</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-2xl font-bold" style={{ color: GOLD }}>✓</div>
              <div className="text-xs text-cyber-muted">Priority Support</div>
            </div>
          </div>
        </div>

        {/* Available Plans */}
        <div>
          <h2 className="text-xl font-bold text-white mb-6">Available Plans</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`cyber-card p-6 relative ${
                  plan.id === currentPlan ? 'ring-2' : ''
                }`}
                style={plan.id === currentPlan ? { borderColor: BLUE } : {}}
              >
                {plan.recommended && (
                  <div
                    className="absolute top-0 right-0 px-3 py-1 rounded-bl-lg rounded-tr-xl text-xs font-bold"
                    style={{ background: GOLD, color: '#000' }}
                  >
                    RECOMMENDED
                  </div>
                )}

                <div className="mb-6">
                  <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                    <span className="text-cyber-muted">{plan.period}</span>
                  </div>
                </div>

                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <svg className="w-5 h-5 flex-shrink-0 text-green-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-cyber-muted">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleChangePlan(plan.id)}
                  disabled={plan.id === currentPlan}
                  className={`w-full px-6 py-3 rounded-xl font-semibold transition-all ${
                    plan.id === currentPlan
                      ? 'bg-slate-700 text-cyber-muted cursor-not-allowed'
                      : 'text-white hover:opacity-90'
                  }`}
                  style={plan.id !== currentPlan ? { background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` } : {}}
                >
                  {plan.id === currentPlan ? 'Current Plan' : plan.id === 'enterprise' ? 'Contact Sales' : 'Upgrade'}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Payment Method */}
        <div className="cyber-card-raised p-6">
          <h2 className="text-xl font-bold text-white mb-6">Payment Method</h2>
          <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
            <div className="flex items-center gap-4">
              <div className="w-12 h-8 rounded bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <div>
                <div className="font-semibold text-white">Visa ending in 4242</div>
                <div className="text-sm text-cyber-muted">Expires 12/2028</div>
              </div>
            </div>
            <button className="px-4 py-2 text-sm font-semibold text-cyber-muted hover:text-white transition-colors">
              Update
            </button>
          </div>
        </div>

        {/* Billing History */}
        <div className="cyber-card-raised p-6">
          <h2 className="text-xl font-bold text-white mb-6">Billing History</h2>
          <div className="space-y-3">
            {invoices.map((invoice) => (
              <div key={invoice.id} className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-all">
                <div>
                  <div className="font-semibold text-white">{invoice.plan} Plan</div>
                  <div className="text-sm text-cyber-muted">{invoice.date}</div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-white font-semibold">{invoice.amount}</div>
                  <div className="px-3 py-1 rounded-lg bg-green-500/20 text-green-400 text-xs font-bold">
                    {invoice.status}
                  </div>
                  <button className="text-sm font-semibold hover:opacity-80" style={{ color: BLUE }}>
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Info */}
        <div className="cyber-card p-6">
          <div className="flex items-start gap-4">
            <svg className="w-6 h-6 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-semibold text-white mb-2">Billing Information</h4>
              <p className="text-sm text-cyber-muted leading-relaxed">
                All plans include automatic monthly billing. You can upgrade or downgrade at any time.
                Changes take effect immediately, and we'll prorate the difference. Cancel anytime with
                no penalties.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && selectedPlan && (
        <PaymentModal
          plan={selectedPlan.name}
          amount={selectedPlan.price}
          onClose={() => setShowPaymentModal(false)}
          onSuccess={handlePaymentSuccess}
        />
      )}
    </DashboardLayout>
  );
}
