'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { APIClient } from '@/lib/api-client';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>('');
  const [error, setError] = useState<string>('');

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleCheckWebsite = async () => {
    if (!inputValue.trim()) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await APIClient.checkURL(inputValue);
      sessionStorage.setItem('lastCheck', JSON.stringify(result));
      router.push(`/check/${result.id}`);
    } catch (err: any) {
      setError(err.message || 'Check failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setSelectedFile(file);
    setLoading(true);
    setError('');

    try {
      let result;

      if (file.type.startsWith('image/')) {
        // Upload photo for AI detection
        result = await APIClient.uploadPhoto(file);
      } else if (file.type.startsWith('video/')) {
        // Upload video for AI detection
        result = await APIClient.uploadVideo(file);
      } else {
        throw new Error('Invalid file type. Please upload an image or video.');
      }

      sessionStorage.setItem('lastCheck', JSON.stringify(result));
      router.push(`/check/${result.id}`);
    } catch (err: any) {
      setError(err.message || 'File verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckPhoto = async () => {
    // Trigger file input for photo
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        handleFileUpload(file);
      }
    };
    input.click();
  };

  const handleCheckVideo = async () => {
    // Trigger file input for video
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'video/*';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        handleFileUpload(file);
      }
    };
    input.click();
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
      {/* Navigation Bar */}
      <nav className="border-b border-blue-900/50 bg-slate-900/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
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
            </div>
            <div className="hidden md:flex gap-6 items-center">
              <a href="/" className="text-gray-300 hover:text-blue-400 transition font-medium">Home</a>
              <a href="/about" className="text-gray-300 hover:text-blue-400 transition font-medium">About</a>
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
      <div className="relative overflow-hidden">
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 2px 2px, rgba(100, 181, 246, 0.4) 1px, transparent 0)`,
            backgroundSize: '40px 40px'
          }}></div>
        </div>

        <div className="container mx-auto px-4 py-24 relative">
          <div className="text-center mb-20 max-w-5xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full mb-8 border border-blue-400/30 shadow-lg shadow-blue-500/20" style={{ background: 'linear-gradient(135deg, rgba(0, 71, 171, 0.2) 0%, rgba(218, 165, 32, 0.2) 100%)' }}>
              <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
              <span className="text-sm font-bold text-blue-300 tracking-wide">AI-POWERED SECURITY FOR AFRICA</span>
            </div>

            {/* Main headline */}
            <h1 className="text-7xl font-extrabold mb-6 leading-tight tracking-tight">
              <span className="block mb-2" style={{ color: '#0047AB', textShadow: '0 0 40px rgba(0, 71, 171, 0.3)' }}>
                AFRICA CYBER
              </span>
              <span className="block" style={{ color: '#DAA520', textShadow: '0 0 40px rgba(218, 165, 32, 0.3)' }}>
                TRUST
              </span>
            </h1>

            <p className="text-2xl text-gray-300 mb-4 font-light">Scam Detection & Authenticity Verification</p>
            <p className="text-gray-400 text-lg max-w-3xl mx-auto">
              Protect yourself from online scams, phishing, deepfakes, and fraud. Check if websites are legitimate, detect AI-generated content, and stay safe across Africa.
            </p>

            {/* Trust indicators */}
            <div className="grid grid-cols-3 gap-6 max-w-2xl mx-auto mt-12">
              <div className="text-center">
                <div className="text-4xl font-bold mb-1" style={{ color: '#0047AB' }}>24/7</div>
                <div className="text-sm text-gray-400">Protection</div>
              </div>
              <div className="text-center border-x border-blue-900/50">
                <div className="text-4xl font-bold mb-1" style={{ color: '#DAA520' }}>AI-Powered</div>
                <div className="text-sm text-gray-400">Detection</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-1" style={{ color: '#0047AB' }}>Instant</div>
                <div className="text-sm text-gray-400">Results</div>
              </div>
            </div>

            {/* CTA buttons */}
            <div className="flex flex-wrap gap-4 justify-center mt-12">
              <a
                href="#check"
                className="px-10 py-4 rounded-xl font-bold text-white shadow-2xl shadow-blue-500/40 hover:shadow-blue-500/60 transition-all transform hover:scale-105 text-lg"
                style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
              >
                Start Free Check →
              </a>
              <a
                href="/business"
                className="px-10 py-4 rounded-xl font-bold border-2 hover:bg-blue-950/50 transition-all text-lg backdrop-blur-sm"
                style={{ borderColor: '#DAA520', color: '#DAA520' }}
              >
                Business Solutions
              </a>
            </div>
          </div>

          {/* Quick Check Section */}
          <div className="max-w-4xl mx-auto" id="check">
            <div className="bg-slate-800/60 backdrop-blur-xl rounded-3xl shadow-2xl p-10 md:p-14 border border-blue-900/30">
              {/* Header */}
              <div className="flex items-center gap-4 mb-8">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-4xl font-bold text-white mb-1">Scam Detector</h2>
                  <p className="text-gray-400">Is this website legitimate or a scam?</p>
                </div>
              </div>

              <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-4 mb-8">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <p className="text-sm text-gray-300">
                    <span className="font-semibold text-blue-400">Safe scam detection.</span> We check domain age, reputation, SSL trust, and red flags - without exposing security vulnerabilities. Protect yourself from fraud!
                  </p>
                </div>
              </div>

              <div className="space-y-6">
                {/* URL Input */}
                <div>
                  <label className="block text-sm font-bold mb-3 text-gray-300">Website URL or Company Name</label>
                  <div className="relative">
                    <input
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleCheckWebsite()}
                      placeholder="https://example.com or company name..."
                      className="w-full px-6 py-5 text-lg border-2 rounded-xl focus:outline-none transition-all shadow-lg bg-slate-900/50 text-white placeholder-gray-500"
                      style={{
                        borderColor: error ? '#DC2626' : 'rgba(0, 71, 171, 0.3)',
                        boxShadow: '0 0 30px rgba(0, 71, 171, 0.1)'
                      }}
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = '#0047AB';
                        e.currentTarget.style.boxShadow = '0 0 30px rgba(0, 71, 171, 0.3)';
                        setError('');
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = error ? '#DC2626' : 'rgba(0, 71, 171, 0.3)';
                        e.currentTarget.style.boxShadow = '0 0 30px rgba(0, 71, 171, 0.1)';
                      }}
                      disabled={loading}
                    />
                    <button
                      onClick={handleCheckWebsite}
                      disabled={loading}
                      className="absolute right-2 top-2 px-6 py-3 rounded-lg font-bold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50"
                      style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                    >
                      Check Now
                    </button>
                  </div>
                </div>

                {/* OR Divider */}
                <div className="flex items-center gap-4 my-6">
                  <div className="flex-1 border-t border-slate-700"></div>
                  <span className="text-gray-500 font-bold text-sm">OR UPLOAD FILE</span>
                  <div className="flex-1 border-t border-slate-700"></div>
                </div>

                {/* File Upload */}
                <div>
                  <label className="flex flex-col items-center justify-center w-full px-6 py-10 border-2 border-dashed rounded-2xl cursor-pointer hover:border-blue-500 transition-all bg-slate-900/30 hover:bg-slate-900/50 border-slate-700">
                    <svg className="w-14 h-14 mb-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="text-lg font-bold text-gray-300 mb-1">Drop file or click to upload</p>
                    <p className="text-sm text-gray-500">PNG, JPG, MP4, WebM (max 10MB photos, 100MB videos)</p>
                    <input
                      type="file"
                      accept="image/*,video/*"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          handleFileUpload(file);
                        }
                      }}
                      className="hidden"
                      disabled={loading}
                    />
                  </label>
                </div>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                    <p className="text-red-400 font-medium">{error}</p>
                  </div>
                )}

                {loading && (
                  <div className="flex items-center justify-center gap-3 py-6 bg-blue-500/10 rounded-xl">
                    <div className="w-6 h-6 border-3 border-t-blue-500 border-blue-900 rounded-full animate-spin"></div>
                    <span className="text-blue-300 font-semibold">Analyzing security...</span>
                  </div>
                )}

                {/* Quick action buttons */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
                  <button
                    onClick={handleCheckPhoto}
                    disabled={loading}
                    className="px-6 py-4 rounded-xl font-bold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                  >
                    <span className="flex items-center justify-center gap-2">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      Verify Photo
                    </span>
                  </button>
                  <button
                    onClick={handleCheckVideo}
                    disabled={loading}
                    className="px-6 py-4 rounded-xl font-bold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}
                  >
                    <span className="flex items-center justify-center gap-2">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Verify Video
                    </span>
                  </button>
                  <button
                    onClick={handleCheckWebsite}
                    disabled={loading}
                    className="px-6 py-4 rounded-xl font-bold text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{ background: 'linear-gradient(135deg, #1E90FF 0%, #0047AB 100%)' }}
                  >
                    <span className="flex items-center justify-center gap-2">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                      </svg>
                      Check Website
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mt-24">
            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">Scam Detection</h3>
              <p className="text-gray-400">Check domain age, verify legitimacy, detect phishing, typosquatting, and assess trust scores. Avoid scams before they happen!</p>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}>
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">AI Content Detection</h3>
              <p className="text-gray-400">Detect deepfakes, AI-generated photos and videos, face swaps, and manipulated media using advanced AI.</p>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-8 border border-blue-900/30 hover:border-blue-500/50 transition-all">
              <div className="w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-white">Company Verification</h3>
              <p className="text-gray-400">Verify business legitimacy, check registration, validate payment platforms, and avoid fintech scams.</p>
            </div>
          </div>

          {/* Bottom CTA */}
          <div className="text-center mt-24 mb-12">
            <h2 className="text-4xl font-bold mb-6" style={{ color: '#0047AB' }}>Ready for Enterprise Security?</h2>
            <p className="text-xl text-gray-400 mb-8">Get continuous monitoring, alerts, and comprehensive reports for your business.</p>
            <a
              href="/business"
              className="inline-block px-12 py-5 rounded-xl font-bold text-white shadow-2xl shadow-gold-500/30 hover:shadow-gold-500/50 transition-all text-lg"
              style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}
            >
              Explore Business Solutions →
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <div className="font-bold" style={{ color: '#0047AB' }}>AFRICA <span style={{ color: '#DAA520' }}>CYBER TRUST</span></div>
                </div>
              </div>
              <p className="text-sm text-gray-500">Digital security and authenticity verification for Africa.</p>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/pricing" className="hover:text-blue-400 transition">Pricing</a></li>
                <li><a href="/business" className="hover:text-blue-400 transition">For Business</a></li>
                <li><a href="/about" className="hover:text-blue-400 transition">About Us</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/terms" className="hover:text-blue-400 transition">Terms of Service</a></li>
                <li><a href="/privacy" className="hover:text-blue-400 transition">Privacy Policy</a></li>
                <li><a href="/security" className="hover:text-blue-400 transition">Security</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="/contact" className="hover:text-blue-400 transition">Contact Us</a></li>
                <li><a href="/help" className="hover:text-blue-400 transition">Help Center</a></li>
                <li><a href="/status" className="hover:text-blue-400 transition">Status</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-8 pt-8 text-center text-sm text-gray-500">
            <p>© 2026 Africa Cyber Trust Infrastructure. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  );
}
