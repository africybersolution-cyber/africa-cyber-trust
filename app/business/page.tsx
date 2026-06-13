'use client';

import { useState } from 'react';
import { INDUSTRY_LIST, getIndustry } from '@/lib/industries';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

const MODULES = [
  {
    name: 'Website Background Checker',
    tier: 'public',
    desc: 'Passive trust scoring for any website — DNS, SSL, security headers, reputation and blacklist checks. No attacks, no permission needed.',
    icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  },
  {
    name: 'App Background Checker',
    tier: 'public',
    desc: 'Check a mobile app or store listing for known risk signals, permissions and publisher reputation before you trust it.',
    icon: 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z',
  },
  {
    name: 'Company Background Check',
    tier: 'public',
    desc: 'Assess a company\'s legitimacy from public footprint, domain age, online reputation and red-flag indicators.',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
  },
  {
    name: 'Verified Web Scanner',
    tier: 'verified',
    desc: 'Deep, authorized vulnerability scanning of your verified domains using Nuclei and OWASP ZAP. Active testing on assets you own.',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    name: 'API Security Scanner',
    tier: 'verified',
    desc: 'Authenticated testing of your REST/GraphQL endpoints for broken auth, injection, misconfiguration and OWASP API Top 10.',
    icon: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4',
  },
  {
    name: 'Mobile App Scanner',
    tier: 'verified',
    desc: 'Static and dynamic analysis of your APK/IPA builds — secrets, insecure storage, weak crypto and dangerous permissions.',
    icon: 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z',
  },
  {
    name: 'AI Security Assistant',
    tier: 'verified',
    desc: 'Plain-language explanations of every finding with prioritized, step-by-step remediation guidance tailored to your stack.',
    icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
  },
  {
    name: 'Company Dashboard',
    tier: 'verified',
    desc: 'One pane of glass — security score, monitored assets, findings, alerts, reports and team roles for your whole organization.',
    icon: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z',
  },
];

const PLANS = [
  {
    name: 'Public Check',
    price: 'Free',
    cadence: 'forever',
    highlight: false,
    cta: 'Run a Check',
    href: '/#check',
    features: [
      'Website, app & company background checks',
      'Trust score + risk level + red flags',
      'AI-written plain-language explanation',
      'Passive analysis only (no scanning)',
      'No registration required',
    ],
  },
  {
    name: 'Business',
    price: '$199',
    cadence: 'per month',
    highlight: true,
    cta: 'Start Free Trial',
    href: '#register',
    features: [
      'Everything in Public Check',
      'Verified deep vulnerability scanning',
      'Up to 25 monitored assets',
      'Scheduled scans + continuous monitoring',
      'Email / SMS / WhatsApp alerts',
      'Executive & technical PDF reports',
      'Team roles & collaboration',
    ],
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    cadence: 'contact us',
    highlight: false,
    cta: 'Talk to Sales',
    href: '/contact',
    features: [
      'Unlimited assets & scans',
      'API security + CI/CD integration',
      'Dedicated security analyst review',
      'Compliance reporting (ISO 27001, SOC 2)',
      'SSO + audit logs',
      'Priority support & SLAs',
    ],
  },
];

export default function BusinessPage() {
  const [step, setStep] = useState<'landing' | 'register' | 'verify'>('landing');
  const [formData, setFormData] = useState({
    companyName: '',
    domain: '',
    email: '',
    phone: '',
    country: '',
    size: '',
    industry: '',
  });

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setStep('verify');
  };

  if (step === 'landing') {
    return (
      <main className="min-h-screen cyber-bg">
        {/* Navigation */}
        <nav className="border-b border-cyber bg-[#050B1A]/80 backdrop-blur-md sticky top-0 z-50">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <a href="/" className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}>
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <div className="font-bold text-sm text-white">AFRICA <span style={{ color: GOLD }}>CYBER TRUST</span></div>
                  <div className="text-[10px] tracking-widest text-cyber-muted">INFRASTRUCTURE</div>
                </div>
              </a>
              <div className="hidden md:flex gap-6 items-center text-sm">
                <a href="/" className="text-cyber-muted hover:text-white transition">Home</a>
                <a href="#modules" className="text-cyber-muted hover:text-white transition">Modules</a>
                <a href="#pricing" className="text-cyber-muted hover:text-white transition">Pricing</a>
                <a href="/contact" className="text-cyber-muted hover:text-white transition">Contact</a>
                <a href="/auth/login" className="text-cyber-muted hover:text-white transition">Login</a>
                <button
                  onClick={() => setStep('register')}
                  className="px-4 py-2 rounded-lg font-semibold text-white shadow-md transition-all hover:opacity-90"
                  style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
                >
                  Start Free Trial
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero */}
        <section className="relative overflow-hidden py-24">
          <div className="container mx-auto px-4 relative">
            <div className="max-w-4xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-cyber bg-[#0A1428] text-sm mb-8" style={{ color: GOLD }}>
                <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: GOLD }}></span>
                Enterprise Cyber Trust Platform for Africa
              </div>

              <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
                Continuously secure the assets <span style={{ color: GOLD }}>you own</span>
              </h1>

              <p className="text-xl text-cyber-muted mb-10 leading-relaxed max-w-2xl mx-auto">
                Verify ownership, run authorized deep vulnerability scans, and monitor your
                domains, APIs and apps 24/7 — with AI-assisted remediation.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => setStep('register')}
                  className="px-8 py-4 rounded-xl font-bold text-white shadow-xl transition-all hover:scale-105 cyber-glow-blue"
                  style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
                >
                  Start Free Trial
                </button>
                <a
                  href="/#check"
                  className="px-8 py-4 rounded-xl font-bold border-2 transition-all hover:bg-white/5"
                  style={{ borderColor: GOLD, color: GOLD }}
                >
                  Try a Free Public Check
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Two-tier offering */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">Two ways to use the platform</h2>
              <p className="text-cyber-muted max-w-2xl mx-auto">
                Anyone can run passive safety checks. Businesses unlock authorized deep scanning after verifying ownership.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
              {/* Public tier */}
              <div className="cyber-card-raised p-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold mb-5 border" style={{ borderColor: GOLD, color: GOLD }}>
                  FOR EVERYONE · FREE
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">Public Background Checks</h3>
                <p className="text-cyber-muted mb-6">
                  Paste any URL, app or company name and get an instant trust assessment.
                </p>
                <ul className="space-y-3 text-sm text-cyber-muted">
                  {['Trust score (0–100) and risk level', 'DNS, SSL, headers & reputation checks', 'Red flags + AI explanation', 'Passive only — no attacks, no permission needed'].map((f) => (
                    <li key={f} className="flex items-start gap-3">
                      <svg className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: GOLD }} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                <a href="/#check" className="mt-7 inline-block px-6 py-3 rounded-xl font-semibold border-2 transition hover:bg-white/5" style={{ borderColor: GOLD, color: GOLD }}>
                  Run a free check
                </a>
              </div>

              {/* Verified tier */}
              <div className="cyber-card-raised p-8 cyber-glow-blue">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold mb-5 text-white" style={{ background: BLUE }}>
                  OWNERSHIP VERIFIED · SUBSCRIPTION
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">Verified Business Monitoring</h3>
                <p className="text-cyber-muted mb-6">
                  Prove you own the asset, then run authorized deep scans and monitor continuously.
                </p>
                <ul className="space-y-3 text-sm text-cyber-muted">
                  {['Domain / API / app / IP ownership verification', 'Deep scans: Nuclei, OWASP ZAP, SSL, headers', 'CVSS-scored findings with remediation', 'Dashboard, alerts, reports & team roles'].map((f) => (
                    <li key={f} className="flex items-start gap-3">
                      <svg className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: '#1E90FF' }} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                <button onClick={() => setStep('register')} className="mt-7 px-6 py-3 rounded-xl font-semibold text-white shadow-lg transition hover:opacity-90" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}>
                  Verify & start scanning
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Modules */}
        <section id="modules" className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">Security modules</h2>
              <p className="text-cyber-muted max-w-2xl mx-auto">
                A complete toolkit — passive checks for everyone, deep scanning for verified owners.
              </p>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
              {MODULES.map((m) => {
                const isVerified = m.tier === 'verified';
                const accent = isVerified ? BLUE : GOLD;
                return (
                  <div key={m.name} className="cyber-card p-6 hover:cyber-glow-blue transition-all">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ background: isVerified ? `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` : `linear-gradient(135deg, ${GOLD} 0%, #FFD700 100%)` }}>
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={m.icon} />
                      </svg>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-[10px] font-bold tracking-wider px-2 py-0.5 rounded-full border" style={{ borderColor: accent, color: accent }}>
                        {isVerified ? 'VERIFIED' : 'PUBLIC'}
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2">{m.name}</h3>
                    <p className="text-sm text-cyber-muted leading-relaxed">{m.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section id="pricing" className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">Plans &amp; pricing</h2>
              <p className="text-cyber-muted max-w-2xl mx-auto">Start free. Upgrade when you need authorized deep scanning and monitoring.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto items-stretch">
              {PLANS.map((p) => (
                <div
                  key={p.name}
                  className={`cyber-card-raised p-8 flex flex-col ${p.highlight ? 'cyber-glow-gold border-2' : ''}`}
                  style={p.highlight ? { borderColor: GOLD } : undefined}
                >
                  {p.highlight && (
                    <div className="self-start mb-4 px-3 py-1 rounded-full text-xs font-bold text-[#050B1A]" style={{ background: GOLD }}>
                      MOST POPULAR
                    </div>
                  )}
                  <h3 className="text-xl font-bold text-white mb-1">{p.name}</h3>
                  <div className="mb-6">
                    <span className="text-4xl font-bold" style={{ color: p.highlight ? GOLD : '#fff' }}>{p.price}</span>
                    <span className="text-cyber-muted text-sm ml-2">{p.cadence}</span>
                  </div>
                  <ul className="space-y-3 text-sm text-cyber-muted flex-1">
                    {p.features.map((f) => (
                      <li key={f} className="flex items-start gap-3">
                        <svg className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: p.highlight ? GOLD : '#1E90FF' }} fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                  {p.href.startsWith('#') ? (
                    <button
                      onClick={() => setStep('register')}
                      className="mt-8 w-full py-3 rounded-xl font-semibold transition hover:opacity-90"
                      style={p.highlight ? { background: `linear-gradient(135deg, ${GOLD} 0%, #FFD700 100%)`, color: '#050B1A' } : { background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)`, color: '#fff' }}
                    >
                      {p.cta}
                    </button>
                  ) : (
                    <a
                      href={p.href}
                      className="mt-8 w-full py-3 rounded-xl font-semibold text-center transition hover:opacity-90 border-2"
                      style={{ borderColor: p.highlight ? GOLD : BLUE, color: p.highlight ? GOLD : '#1E90FF' }}
                    >
                      {p.cta}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section id="register" className="py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto rounded-3xl p-12 text-center relative overflow-hidden cyber-glow-blue" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 50%, ${GOLD} 130%)` }}>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Ready to secure your business?</h2>
              <p className="text-lg text-blue-50 mb-8 max-w-2xl mx-auto">
                Verify ownership and start authorized deep scanning in minutes. 14-day free trial, no card required.
              </p>
              <button
                onClick={() => setStep('register')}
                className="px-10 py-4 bg-white rounded-xl font-bold text-lg shadow-xl transition-all hover:scale-105"
                style={{ color: BLUE }}
              >
                Register Your Business
              </button>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-cyber py-10">
          <div className="container mx-auto px-4 text-center text-cyber-muted text-sm">
            © 2026 Africa Cyber Trust Infrastructure. All rights reserved.
          </div>
        </footer>
      </main>
    );
  }

  if (step === 'register') {
    return (
      <main className="min-h-screen cyber-bg py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold mb-3 text-white">
                Register Your <span style={{ color: GOLD }}>Business</span>
              </h1>
              <p className="text-cyber-muted">
                Get started with a 14-day free trial. No credit card required.
              </p>
            </div>

            <div className="cyber-card-raised p-10">
              <form onSubmit={handleRegister} className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold mb-2 text-cyber-muted">Company Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.companyName}
                    onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
                    className="w-full px-4 py-3 bg-[#050B1A] border border-cyber rounded-xl text-white focus:outline-none focus:border-blue-500 transition-all"
                    placeholder="e.g., TechStartup Ltd"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-cyber-muted">Company Domain *</label>
                  <input
                    type="text"
                    required
                    value={formData.domain}
                    onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                    className="w-full px-4 py-3 bg-[#050B1A] border border-cyber rounded-xl text-white focus:outline-none focus:border-blue-500 transition-all"
                    placeholder="e.g., techstartup.com"
                  />
                  <p className="text-sm text-cyber-muted mt-2">We&apos;ll verify you own this domain before any deep scanning.</p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-cyber-muted">Business Email *</label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-4 py-3 bg-[#050B1A] border border-cyber rounded-xl text-white focus:outline-none focus:border-blue-500 transition-all"
                      placeholder="admin@techstartup.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-cyber-muted">Phone Number *</label>
                    <input
                      type="tel"
                      required
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="w-full px-4 py-3 bg-[#050B1A] border border-cyber rounded-xl text-white focus:outline-none focus:border-blue-500 transition-all"
                      placeholder="+254 712 345 678"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-cyber-muted">Country *</label>
                    <select
                      required
                      value={formData.country}
                      onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                      className="w-full px-4 py-3 bg-[#050B1A] border border-cyber rounded-xl text-white focus:outline-none focus:border-blue-500 transition-all"
                    >
                      <option value="">Select country</option>
                      <option value="DZ">Algeria</option>
                      <option value="AO">Angola</option>
                      <option value="BJ">Benin</option>
                      <option value="BW">Botswana</option>
                      <option value="BF">Burkina Faso</option>
                      <option value="BI">Burundi</option>
                      <option value="CV">Cabo Verde</option>
                      <option value="CM">Cameroon</option>
                      <option value="CF">Central African Republic</option>
                      <option value="TD">Chad</option>
                      <option value="KM">Comoros</option>
                      <option value="CG">Congo</option>
                      <option value="CD">Congo (DRC)</option>
                      <option value="CI">Côte d&apos;Ivoire</option>
                      <option value="DJ">Djibouti</option>
                      <option value="EG">Egypt</option>
                      <option value="GQ">Equatorial Guinea</option>
                      <option value="ER">Eritrea</option>
                      <option value="SZ">Eswatini</option>
                      <option value="ET">Ethiopia</option>
                      <option value="GA">Gabon</option>
                      <option value="GM">Gambia</option>
                      <option value="GH">Ghana</option>
                      <option value="GN">Guinea</option>
                      <option value="GW">Guinea-Bissau</option>
                      <option value="KE">Kenya</option>
                      <option value="LS">Lesotho</option>
                      <option value="LR">Liberia</option>
                      <option value="LY">Libya</option>
                      <option value="MG">Madagascar</option>
                      <option value="MW">Malawi</option>
                      <option value="ML">Mali</option>
                      <option value="MR">Mauritania</option>
                      <option value="MU">Mauritius</option>
                      <option value="MA">Morocco</option>
                      <option value="MZ">Mozambique</option>
                      <option value="NA">Namibia</option>
                      <option value="NE">Niger</option>
                      <option value="NG">Nigeria</option>
                      <option value="RW">Rwanda</option>
                      <option value="ST">São Tomé and Príncipe</option>
                      <option value="SN">Senegal</option>
                      <option value="SC">Seychelles</option>
                      <option value="SL">Sierra Leone</option>
                      <option value="SO">Somalia</option>
                      <option value="ZA">South Africa</option>
                      <option value="SS">South Sudan</option>
                      <option value="SD">Sudan</option>
                      <option value="TZ">Tanzania</option>
                      <option value="TG">Togo</option>
                      <option value="TN">Tunisia</option>
                      <option value="UG">Uganda</option>
                      <option value="ZM">Zambia</option>
                      <option value="ZW">Zimbabwe</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-cyber-muted">Company Size *</label>
                    <select
                      required
                      value={formData.size}
                      onChange={(e) => setFormData({ ...formData, size: e.target.value })}
                      className="w-full px-4 py-3 bg-[#050B1A] border border-cyber rounded-xl text-white focus:outline-none focus:border-blue-500 transition-all"
                    >
                      <option value="">Select size</option>
                      <option value="1-10">1-10 employees</option>
                      <option value="11-50">11-50 employees</option>
                      <option value="51-200">51-200 employees</option>
                      <option value="201-500">201-500 employees</option>
                      <option value="500+">500+ employees</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-cyber-muted">Industry *</label>
                  <select
                    required
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    className="w-full px-4 py-3 bg-[#050B1A] border border-cyber rounded-xl text-white focus:outline-none focus:border-blue-500 transition-all"
                  >
                    <option value="">Select industry</option>
                    {INDUSTRY_LIST.map((ind) => (
                      <option key={ind.id} value={ind.id}>
                        {ind.icon} {ind.label}
                      </option>
                    ))}
                  </select>
                  {formData.industry && (
                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <span className="text-xs text-cyber-muted">We&apos;ll tailor compliance & scanning to:</span>
                      {getIndustry(formData.industry).compliance.map((c) => (
                        <span
                          key={c.label}
                          title={c.full}
                          className="px-2 py-0.5 rounded-full text-[10px] font-bold border"
                          style={{ borderColor: GOLD, color: GOLD }}
                        >
                          {c.label}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => setStep('landing')}
                    className="flex-1 py-4 rounded-xl font-semibold border-2 transition-all hover:bg-white/5"
                    style={{ borderColor: GOLD, color: GOLD }}
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:opacity-90"
                    style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
                  >
                    Continue to Verification
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </main>
    );
  }

  // Verification step
  return (
    <main className="min-h-screen cyber-bg py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <div className="w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center cyber-glow-blue" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}>
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold mb-4 text-white">Verify Domain Ownership</h1>
            <p className="text-cyber-muted max-w-2xl mx-auto">
              Deep scanning is only unlocked after you prove ownership of <strong className="text-white">{formData.domain || 'your domain'}</strong>.
            </p>
          </div>

          <div className="cyber-card-raised p-10">
            <h2 className="text-2xl font-bold mb-6 text-white">Preview: Verification Methods Available</h2>
            <p className="text-cyber-muted mb-6 text-sm">
              ℹ️ These are preview examples. You'll choose your method on the next page.
            </p>

            <div className="space-y-4 opacity-60 pointer-events-none">
              <div className="border border-cyber rounded-2xl p-6 transition-all" style={{ borderColor: BLUE }}>
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}>
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2 text-white">DNS TXT Record <span className="text-xs" style={{ color: GOLD }}>(Recommended)</span></h3>
                    <p className="text-cyber-muted mb-4">Add a TXT record to your domain&apos;s DNS settings</p>
                    <div className="bg-[#050B1A] border border-cyber rounded-lg p-4 font-mono text-sm text-cyber-muted">
                      <div className="mb-2"><strong className="text-white">Name:</strong> _acti-verify</div>
                      <div><strong className="text-white">Value:</strong> acti-{Math.random().toString(36).substring(7)}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border border-cyber rounded-2xl p-6 transition-all">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${GOLD} 0%, #FFD700 100%)` }}>
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2 text-white">HTML File Upload</h3>
                    <p className="text-cyber-muted mb-4">Upload a verification file to your website root</p>
                    <div className="bg-[#050B1A] border border-cyber rounded-lg p-4 font-mono text-sm text-cyber-muted">
                      <div className="mb-2"><strong className="text-white">File:</strong> acti-verify.html</div>
                      <div><strong className="text-white">URL:</strong> https://{formData.domain || 'your-domain.com'}/acti-verify.html</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border border-cyber rounded-2xl p-6 transition-all">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #1E90FF 0%, #0047AB 100%)' }}>
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2 text-white">Email Verification</h3>
                    <p className="text-cyber-muted">We&apos;ll send a verification link to admin@{formData.domain || 'your-domain.com'}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 flex gap-4">
              <button
                onClick={() => setStep('register')}
                className="flex-1 py-4 rounded-xl font-semibold border-2 transition-all hover:bg-white/5"
                style={{ borderColor: GOLD, color: GOLD }}
              >
                Back
              </button>
              <a
                href={`/business/register?company=${encodeURIComponent(formData.companyName)}&domain=${encodeURIComponent(formData.domain)}&email=${encodeURIComponent(formData.email)}&phone=${encodeURIComponent(formData.phone)}&country=${encodeURIComponent(formData.country)}&size=${encodeURIComponent(formData.size)}&industry=${encodeURIComponent(formData.industry)}`}
                className="flex-1 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:opacity-90 text-center"
                style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
              >
                Continue to Registration
              </a>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
