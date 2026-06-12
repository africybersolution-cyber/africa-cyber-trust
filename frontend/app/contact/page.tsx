'use client';

import { useState } from 'react';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    phone: '',
    subject: 'General Inquiry',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      setSubmitted(true);
    }, 1500);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

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
              <a href="/pricing" className="text-gray-300 hover:text-blue-400 transition font-medium">Pricing</a>
              <a href="/business" className="text-gray-300 hover:text-blue-400 transition font-medium">For Business</a>
              <a href="/contact" className="text-blue-400 font-semibold">Contact</a>
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
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
            </svg>
            <span className="text-sm font-bold text-blue-300 tracking-wide">WE'RE HERE TO HELP</span>
          </div>

          <h1 className="text-6xl font-extrabold mb-6 leading-tight tracking-tight">
            <span style={{ color: '#0047AB', textShadow: '0 0 40px rgba(0, 71, 171, 0.3)' }}>
              Get in
            </span>
            <br />
            <span style={{ color: '#DAA520', textShadow: '0 0 40px rgba(218, 165, 32, 0.3)' }}>
              Touch
            </span>
          </h1>

          <p className="text-xl text-gray-300">
            Have questions about our security platform? Our team is ready to help you protect your digital assets.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {/* Contact Form */}
          <div className="lg:col-span-2">
            <div className="bg-slate-800/60 backdrop-blur-xl rounded-3xl p-10 border border-blue-900/30 shadow-2xl">
              {!submitted ? (
                <>
                  <h2 className="text-3xl font-bold text-white mb-8">Send us a message</h2>
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-bold mb-2 text-gray-300">Full Name *</label>
                        <input
                          type="text"
                          name="name"
                          value={formData.name}
                          onChange={handleChange}
                          required
                          className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none text-white placeholder-gray-500 transition-all"
                          placeholder="John Doe"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-bold mb-2 text-gray-300">Email Address *</label>
                        <input
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          required
                          className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none text-white placeholder-gray-500 transition-all"
                          placeholder="john@company.com"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-bold mb-2 text-gray-300">Company</label>
                        <input
                          type="text"
                          name="company"
                          value={formData.company}
                          onChange={handleChange}
                          className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none text-white placeholder-gray-500 transition-all"
                          placeholder="Your Company"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-bold mb-2 text-gray-300">Phone Number</label>
                        <input
                          type="tel"
                          name="phone"
                          value={formData.phone}
                          onChange={handleChange}
                          className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none text-white placeholder-gray-500 transition-all"
                          placeholder="+250 XXX XXX XXX"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-bold mb-2 text-gray-300">Subject *</label>
                      <select
                        name="subject"
                        value={formData.subject}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none text-white transition-all"
                      >
                        <option value="General Inquiry">General Inquiry</option>
                        <option value="Sales">Sales</option>
                        <option value="Technical Support">Technical Support</option>
                        <option value="Partnership">Partnership</option>
                        <option value="Media & Press">Media & Press</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-bold mb-2 text-gray-300">Message *</label>
                      <textarea
                        name="message"
                        value={formData.message}
                        onChange={handleChange}
                        required
                        rows={6}
                        className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border-2 border-blue-900/30 focus:border-blue-500 focus:outline-none text-white placeholder-gray-500 transition-all resize-none"
                        placeholder="Tell us how we can help you..."
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full py-4 rounded-xl font-bold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-lg"
                      style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                    >
                      {loading ? (
                        <span className="flex items-center justify-center gap-2">
                          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Sending...
                        </span>
                      ) : (
                        'Send Message'
                      )}
                    </button>
                  </form>
                </>
              ) : (
                <div className="text-center py-12">
                  <div className="w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-3xl font-bold text-white mb-4">Message Sent!</h3>
                  <p className="text-gray-300 mb-8">
                    Thank you for contacting us. Our team will get back to you within 24 hours.
                  </p>
                  <button
                    onClick={() => {
                      setSubmitted(false);
                      setFormData({
                        name: '',
                        email: '',
                        company: '',
                        phone: '',
                        subject: 'General Inquiry',
                        message: ''
                      });
                    }}
                    className="px-8 py-3 rounded-xl font-bold border-2 hover:bg-blue-950/50 transition-all"
                    style={{ borderColor: '#0047AB', color: '#0047AB' }}
                  >
                    Send Another Message
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Contact Info */}
          <div className="space-y-6">
            {/* Email */}
            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border border-blue-900/30">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Email Us</h3>
              <p className="text-gray-400 text-sm mb-3">For general inquiries and support</p>
              <a href="mailto:support@africacybertrust.com" className="text-blue-400 hover:text-blue-300 font-medium">
                support@africacybertrust.com
              </a>
            </div>

            {/* Phone */}
            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border border-blue-900/30">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Call Us</h3>
              <p className="text-gray-400 text-sm mb-3">Mon-Fri, 9am-6pm EAT</p>
              <a href="tel:+250788000000" className="text-blue-400 hover:text-blue-300 font-medium">
                +250 788 000 000
              </a>
            </div>

            {/* Office */}
            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border border-blue-900/30">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Visit Us</h3>
              <p className="text-gray-400 text-sm mb-3">Headquarters</p>
              <p className="text-white">
                Kigali, Rwanda<br />
                KN 4 Ave, Nyarugenge<br />
                Kigali Heights Building
              </p>
            </div>

            {/* Social */}
            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border border-blue-900/30">
              <h3 className="text-xl font-bold text-white mb-4">Follow Us</h3>
              <div className="flex gap-3">
                <a href="#" className="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-600 hover:bg-blue-700 transition-colors">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                </a>
                <a href="#" className="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-500 hover:bg-blue-600 transition-colors">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                  </svg>
                </a>
                <a href="#" className="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-700 hover:bg-blue-800 transition-colors">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
              </div>
            </div>
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
