'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import CreditsWidget from '../../components/CreditsWidget';

export default function CompanyVerificationPage() {
  const router = useRouter();
  const [companyName, setCompanyName] = useState('');
  const [companyTin, setCompanyTin] = useState('');
  const [country, setCountry] = useState('RW');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [reports, setReports] = useState<any[]>([]);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/company/reports', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        const data = await res.json();
        setReports(data);
      }
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');

      const res = await fetch('/api/company/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          company_name: companyName,
          company_tin: companyTin,
          country: country,
          report_type: 'basic'
        })
      });

      const data = await res.json();

      if (res.ok) {
        alert(`Report generated! Risk Score: ${data.risk_score}/100\nCredits remaining: ${data.credits_remaining}`);
        setCompanyName('');
        setCompanyTin('');
        fetchReports();
      } else {
        if (res.status === 402) {
          setError('Insufficient credits. Please upgrade your plan.');
        } else {
          setError(data.detail || 'Failed to generate report');
        }
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const countries = [
    { code: 'RW', name: 'Rwanda', flag: '🇷🇼' },
    { code: 'KE', name: 'Kenya', flag: '🇰🇪' },
    { code: 'UG', name: 'Uganda', flag: '🇺🇬' },
    { code: 'TZ', name: 'Tanzania', flag: '🇹🇿' },
    { code: 'ZM', name: 'Zambia', flag: '🇿🇲' },
    { code: 'GH', name: 'Ghana', flag: '🇬🇭' },
    { code: 'ZA', name: 'South Africa', flag: '🇿🇦' },
    { code: 'NG', name: 'Nigeria', flag: '🇳🇬' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <nav className="border-b border-gray-200 bg-white/90 backdrop-blur-md sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => router.push('/dashboard')}>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-gradient-to-br from-blue-700 to-blue-900">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-lg text-blue-700">ACTI</div>
                <div className="text-xs text-gray-500">Company Verification</div>
              </div>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 font-semibold transition"
            >
              ← Back
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Left Column - Form */}
            <div className="lg:col-span-2 space-y-6">
              {/* Hero Card */}
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl p-8 text-white shadow-2xl">
                <div className="flex items-start justify-between">
                  <div>
                    <h1 className="text-3xl font-bold mb-2">Company Verification</h1>
                    <p className="text-blue-100 text-lg">
                      Get detailed due diligence reports on any African company
                    </p>
                  </div>
                  <div className="text-6xl">🏢</div>
                </div>
              </div>

              {/* Request Form */}
              <div className="bg-white rounded-2xl shadow-xl p-8 border-2 border-gray-100">
                <h2 className="text-2xl font-bold mb-6">Request Verification Report</h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">
                      Company Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="e.g., Ktravo Ltd"
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">
                      Tax ID Number (TIN)
                    </label>
                    <input
                      type="text"
                      value={companyTin}
                      onChange={(e) => setCompanyTin(e.target.value)}
                      placeholder="e.g., 123456789"
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition"
                    />
                    <p className="text-xs text-gray-500 mt-1">Optional - helps with accuracy</p>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">
                      Country *
                    </label>
                    <select
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition"
                    >
                      {countries.map((c) => (
                        <option key={c.code} value={c.code}>{c.flag} {c.name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
                    <h3 className="font-semibold text-blue-900 mb-2">Report Includes:</h3>
                    <ul className="space-y-1 text-sm text-blue-800">
                      <li>✓ Business registration validation</li>
                      <li>✓ Directors & shareholders info</li>
                      <li>✓ Financial health scoring</li>
                      <li>✓ Court cases & legal issues</li>
                      <li>✓ Tax compliance status</li>
                      <li>✓ Online reputation analysis</li>
                    </ul>
                  </div>

                  {error && (
                    <div className="p-4 bg-red-50 border-2 border-red-200 rounded-xl text-red-700">
                      {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-bold text-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 transition shadow-lg"
                  >
                    {loading ? 'Generating Report...' : 'Generate Report (5 Credits)'}
                  </button>
                </form>
              </div>

              {/* Previous Reports */}
              {reports.length > 0 && (
                <div className="bg-white rounded-2xl shadow-xl p-8 border-2 border-gray-100">
                  <h2 className="text-2xl font-bold mb-6">Your Reports</h2>
                  <div className="space-y-4">
                    {reports.map((report) => (
                      <div
                        key={report.id}
                        className="p-4 border-2 border-gray-200 rounded-xl hover:border-blue-300 transition cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-bold text-lg">{report.company_name}</h3>
                            <p className="text-sm text-gray-600">{report.country}</p>
                          </div>
                          {report.risk_score && (
                            <div className={`text-2xl font-bold ${report.risk_score > 70 ? 'text-green-600' : report.risk_score > 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                              {report.risk_score}/100
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Credits Widget */}
            <div className="lg:col-span-1">
              <div className="sticky top-24">
                <CreditsWidget />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
