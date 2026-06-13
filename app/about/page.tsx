'use client';

export default function AboutPage() {
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
              <a href="/about" className="text-blue-400 font-semibold">About</a>
              <a href="/pricing" className="text-gray-300 hover:text-blue-400 transition font-medium">Pricing</a>
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
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-bold text-blue-300 tracking-wide">OUR STORY</span>
          </div>

          <h1 className="text-6xl font-extrabold mb-6 leading-tight tracking-tight">
            <span style={{ color: '#0047AB', textShadow: '0 0 40px rgba(0, 71, 171, 0.3)' }}>
              Protecting
            </span>
            <br />
            <span style={{ color: '#DAA520', textShadow: '0 0 40px rgba(218, 165, 32, 0.3)' }}>
              Africa's Digital Future
            </span>
          </h1>

          <p className="text-xl text-gray-300 leading-relaxed">
            We're building the most trusted cybersecurity infrastructure in Africa, helping businesses and individuals stay safe in an increasingly digital world.
          </p>
        </div>

        {/* Mission Statement */}
        <div className="max-w-6xl mx-auto mb-20">
          <div className="bg-slate-800/60 backdrop-blur-xl rounded-3xl p-12 border border-blue-900/30 shadow-2xl">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-4xl font-bold mb-6" style={{ color: '#0047AB' }}>Our Mission</h2>
                <p className="text-gray-300 text-lg leading-relaxed mb-6">
                  To democratize cybersecurity across Africa by providing accessible, AI-powered tools that protect businesses and individuals from digital threats, scams, and fraud.
                </p>
                <p className="text-gray-400 leading-relaxed">
                  We believe every African business deserves enterprise-grade security, regardless of size or budget. Our platform combines cutting-edge AI with local expertise to deliver world-class protection tailored for the African market.
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-2xl p-6 text-center">
                  <div className="text-5xl font-extrabold mb-2" style={{ color: '#0047AB' }}>10K+</div>
                  <div className="text-gray-400 text-sm">Assets Protected</div>
                </div>
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-2xl p-6 text-center">
                  <div className="text-5xl font-extrabold mb-2" style={{ color: '#DAA520' }}>24/7</div>
                  <div className="text-gray-400 text-sm">Monitoring</div>
                </div>
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-2xl p-6 text-center">
                  <div className="text-5xl font-extrabold mb-2" style={{ color: '#0047AB' }}>50+</div>
                  <div className="text-gray-400 text-sm">Countries Served</div>
                </div>
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-2xl p-6 text-center">
                  <div className="text-5xl font-extrabold mb-2" style={{ color: '#DAA520' }}>99.9%</div>
                  <div className="text-gray-400 text-sm">Uptime</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Core Values */}
        <div className="max-w-6xl mx-auto mb-20">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">Our Core Values</h2>
            <p className="text-gray-400 text-lg">The principles that guide everything we do</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Security First</h3>
              <p className="text-gray-400">
                We never compromise on security. Every decision, feature, and line of code is built with protection in mind.
              </p>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Africa-Focused</h3>
              <p className="text-gray-400">
                Built by Africans, for Africa. We understand the unique challenges and opportunities of the African digital landscape.
              </p>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Innovation</h3>
              <p className="text-gray-400">
                We leverage cutting-edge AI and technology to stay ahead of evolving threats and deliver the best protection.
              </p>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #1E90FF 0%, #0047AB 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Accessibility</h3>
              <p className="text-gray-400">
                Enterprise security shouldn't be a luxury. We make powerful tools accessible to businesses of all sizes.
              </p>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #FFD700 0%, #DAA520 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Trust</h3>
              <p className="text-gray-400">
                Transparency and integrity in everything we do. Your trust is our most valuable asset.
              </p>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Excellence</h3>
              <p className="text-gray-400">
                We strive for excellence in every aspect, from product quality to customer service and beyond.
              </p>
            </div>
          </div>
        </div>

        {/* Why Africa Needs This */}
        <div className="max-w-6xl mx-auto mb-20">
          <div className="bg-gradient-to-br from-blue-900/20 to-yellow-900/20 backdrop-blur-sm rounded-3xl p-12 border border-blue-500/30 shadow-2xl">
            <h2 className="text-4xl font-bold mb-6 text-center text-white">Why Africa Needs Cyber Trust Infrastructure</h2>
            <div className="grid md:grid-cols-2 gap-8 text-gray-300">
              <div>
                <h3 className="text-xl font-bold mb-3" style={{ color: '#0047AB' }}>The Challenge</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <svg className="w-5 h-5 flex-shrink-0 mt-1 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span>Cyber attacks on African businesses increased by 300% in recent years</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-5 h-5 flex-shrink-0 mt-1 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span>Digital scams and fraud cost African economies billions annually</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-5 h-5 flex-shrink-0 mt-1 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span>Most SMEs lack access to affordable cybersecurity tools</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-5 h-5 flex-shrink-0 mt-1 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span>Traditional security solutions are too expensive for local businesses</span>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-bold mb-3" style={{ color: '#DAA520' }}>Our Solution</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <svg className="w-5 h-5 flex-shrink-0 mt-1 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>AI-powered threat detection and prevention in real-time</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-5 h-5 flex-shrink-0 mt-1 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Affordable pricing designed for African businesses</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-5 h-5 flex-shrink-0 mt-1 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Free tools for individuals to verify websites and detect scams</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <svg className="w-5 h-5 flex-shrink-0 mt-1 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Local support team that understands African context</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-6 text-white">Join Us in Building a Safer Africa</h2>
          <p className="text-xl text-gray-300 mb-8">
            Whether you're an individual looking to verify a website or a business seeking enterprise protection, we're here to help.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
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
              Contact Us
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
