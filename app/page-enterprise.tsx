'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  return (
    <main className="min-h-screen">
      {/* Navigation */}
      <nav className="border-b border-gray-200 bg-white sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-lg" style={{ color: '#0047AB' }}>
                  AFRICA <span style={{ color: '#DAA520' }}>CYBER TRUST</span>
                </div>
                <div className="text-xs text-gray-500">INFRASTRUCTURE</div>
              </div>
            </div>
            <div className="flex gap-6 items-center">
              <a href="/login" className="text-gray-600 hover:text-blue-700 font-medium">Sign In</a>
              <a
                href="/signup"
                className="px-6 py-2 rounded-lg font-semibold text-white shadow-lg hover:shadow-xl transition-all"
                style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
              >
                Get Started
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section - Enterprise Focus */}
      <section className="relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 50%, #87CEEB 100%)' }}>
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-96 h-96 rounded-full bg-white blur-3xl"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 rounded-full bg-yellow-300 blur-3xl"></div>
        </div>

        <div className="container mx-auto px-6 py-24 relative">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm text-white mb-8">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
              <span className="font-semibold">Enterprise Solutions</span>
            </div>

            <h1 className="text-6xl font-bold text-white mb-6 leading-tight">
              Protect Your Business
            </h1>

            <p className="text-2xl text-white/90 mb-12 leading-relaxed">
              Get verified vulnerability scanning, continuous monitoring, and
              <br />AI-assisted security guidance
            </p>

            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <button
                onClick={() => router.push('/signup')}
                className="px-10 py-5 rounded-xl font-bold text-lg shadow-2xl hover:shadow-3xl transition-all bg-white hover:scale-105"
                style={{ color: '#0047AB' }}
              >
                Start Free Trial
              </button>
              <button
                onClick={() => router.push('/business')}
                className="px-10 py-5 rounded-xl font-bold text-lg border-2 border-white text-white hover:bg-white/10 transition-all"
              >
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4" style={{ color: '#0047AB' }}>
              Complete Security Platform
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to protect your digital assets
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-gradient-to-br from-blue-50 to-white rounded-3xl shadow-lg p-8 hover:shadow-xl transition-all">
              <div className="w-16 h-16 rounded-2xl mb-6 flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4" style={{ color: '#0047AB' }}>
                Continuous Monitoring
              </h3>
              <p className="text-gray-600 leading-relaxed">
                24/7 automated scanning of your websites, APIs, and mobile apps. Get instant alerts when security issues are detected.
              </p>
            </div>

            <div className="bg-gradient-to-br from-yellow-50 to-white rounded-3xl shadow-lg p-8 hover:shadow-xl transition-all">
              <div className="w-16 h-16 rounded-2xl mb-6 flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4" style={{ color: '#DAA520' }}>
                AI-Powered Analysis
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Advanced AI detects threats, analyzes vulnerabilities, and provides actionable security recommendations.
              </p>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-white rounded-3xl shadow-lg p-8 hover:shadow-xl transition-all">
              <div className="w-16 h-16 rounded-2xl mb-6 flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #1E90FF 0%, #0047AB 100%)' }}>
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4" style={{ color: '#0047AB' }}>
                Team Collaboration
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Add team members, assign roles, and collaborate on security issues. Perfect for distributed teams.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 max-w-6xl mx-auto text-center">
            <div>
              <div className="text-5xl font-bold text-white mb-2">500+</div>
              <div className="text-blue-100">African Businesses</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-white mb-2">10K+</div>
              <div className="text-blue-100">Assets Protected</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-white mb-2">99.9%</div>
              <div className="text-blue-100">Uptime</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-white mb-2">24/7</div>
              <div className="text-blue-100">Monitoring</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-5xl font-bold mb-6" style={{ color: '#0047AB' }}>
              Ready to Secure Your Business?
            </h2>
            <p className="text-xl text-gray-600 mb-12">
              Join hundreds of African businesses protecting their digital assets with ACTI
            </p>
            <button
              onClick={() => router.push('/signup')}
              className="px-12 py-5 rounded-xl font-bold text-lg text-white shadow-2xl hover:shadow-3xl transition-all hover:scale-105"
              style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
            >
              Get Started - Free Trial
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="font-bold text-xl mb-4">
                AFRICA <span style={{ color: '#DAA520' }}>CYBER TRUST</span>
              </div>
              <p className="text-gray-400 text-sm">
                Building trusted digital infrastructure for Africa through AI-powered cybersecurity.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/business" className="hover:text-white">Features</a></li>
                <li><a href="/business" className="hover:text-white">Pricing</a></li>
                <li><a href="/dashboard" className="hover:text-white">Dashboard</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/business" className="hover:text-white">About</a></li>
                <li><a href="/business" className="hover:text-white">Contact</a></li>
                <li><a href="/business" className="hover:text-white">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/business" className="hover:text-white">Privacy</a></li>
                <li><a href="/business" className="hover:text-white">Terms</a></li>
                <li><a href="/business" className="hover:text-white">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
            © 2026 Africa Cyber Trust Infrastructure. All rights reserved.
          </div>
        </div>
      </footer>
    </main>
  );
}
