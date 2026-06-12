'use client';

import { useState } from 'react';

export default function ReportsPage() {
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [reportType, setReportType] = useState<'security' | 'compliance' | 'executive'>('security');
  const [dateRange, setDateRange] = useState('30days');

  const reports = [
    {
      id: 1,
      name: 'Monthly Security Report - May 2026',
      type: 'Security Report',
      date: 'Jun 1, 2026',
      size: '2.4 MB',
      status: 'Ready',
      downloadUrl: '#',
    },
    {
      id: 2,
      name: 'Compliance Report Q2 2026',
      type: 'Compliance Report',
      date: 'May 28, 2026',
      size: '1.8 MB',
      status: 'Ready',
      downloadUrl: '#',
    },
    {
      id: 3,
      name: 'Executive Summary - April 2026',
      type: 'Executive Summary',
      date: 'May 1, 2026',
      size: '890 KB',
      status: 'Ready',
      downloadUrl: '#',
    },
    {
      id: 4,
      name: 'Asset Scan Report - Week 22',
      type: 'Security Report',
      date: 'May 27, 2026',
      size: '3.1 MB',
      status: 'Ready',
      downloadUrl: '#',
    },
  ];

  const reportStats = {
    totalReports: 24,
    thisMonth: 4,
    avgScore: 87,
    criticalIssues: 3,
  };

  const handleGenerateReport = () => {
    // TODO: Connect to backend API
    alert('Report generation will be implemented with backend API!');
    setShowGenerateModal(false);
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
              Security Reports
            </h1>
            <p className="text-gray-600">Generate and download comprehensive security reports</p>
          </div>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
            style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Generate Report
          </button>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-2xl font-bold mb-1" style={{ color: '#0047AB' }}>{reportStats.totalReports}</div>
            <div className="text-gray-600 text-sm">Total Reports</div>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-2xl font-bold text-green-600 mb-1">{reportStats.thisMonth}</div>
            <div className="text-gray-600 text-sm">This Month</div>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-2xl font-bold mb-1" style={{ color: '#DAA520' }}>{reportStats.avgScore}</div>
            <div className="text-gray-600 text-sm">Avg. Security Score</div>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-2xl font-bold text-red-600 mb-1">{reportStats.criticalIssues}</div>
            <div className="text-gray-600 text-sm">Critical Issues</div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Reports List */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-bold mb-4" style={{ color: '#0047AB' }}>Recent Reports</h2>

            {reports.map((report) => (
              <div key={report.id} className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-14 h-14 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-900 mb-1">{report.name}</h3>
                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                        <span>{report.type}</span>
                        <span>•</span>
                        <span>{report.date}</span>
                        <span>•</span>
                        <span>{report.size}</span>
                      </div>
                      <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-xs font-semibold">
                        {report.status}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <a
                      href={report.downloadUrl}
                      className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg font-semibold text-sm hover:bg-blue-100 transition-all flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download
                    </a>
                    <button className="px-4 py-2 bg-gray-50 text-gray-700 rounded-lg font-semibold text-sm hover:bg-gray-100 transition-all">
                      Share
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Report Types Info */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4" style={{ color: '#0047AB' }}>Report Types</h3>

              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <svg className="w-5 h-5 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    <h4 className="font-bold text-blue-900">Security Report</h4>
                  </div>
                  <p className="text-sm text-blue-800">
                    Detailed security findings, vulnerabilities, and recommendations for all assets
                  </p>
                </div>

                <div className="p-4 bg-green-50 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <svg className="w-5 h-5 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h4 className="font-bold text-green-900">Compliance Report</h4>
                  </div>
                  <p className="text-sm text-green-800">
                    Regulatory compliance status (GDPR, ISO 27001, SOC 2)
                  </p>
                </div>

                <div className="p-4 bg-purple-50 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <svg className="w-5 h-5 text-purple-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <h4 className="font-bold text-purple-900">Executive Summary</h4>
                  </div>
                  <p className="text-sm text-purple-800">
                    High-level overview with key metrics for leadership
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl shadow-lg p-6 border-2 border-blue-200">
              <div className="flex items-start gap-3 mb-4">
                <svg className="w-6 h-6 text-blue-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="font-bold text-blue-900 mb-1">Scheduled Reports</h4>
                  <p className="text-sm text-blue-800 mb-3">
                    Set up automatic report generation weekly or monthly
                  </p>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold text-sm hover:bg-blue-700 transition-all">
                    Configure Schedule
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Generate Report Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold" style={{ color: '#0047AB' }}>Generate New Report</h2>
              <button
                onClick={() => setShowGenerateModal(false)}
                className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold mb-3" style={{ color: '#0047AB' }}>
                  Report Type
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => setReportType('security')}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      reportType === 'security'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <svg className="w-8 h-8 mx-auto mb-2" style={{ color: reportType === 'security' ? '#0047AB' : '#6B7280' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    <div className="text-sm font-semibold">Security</div>
                  </button>

                  <button
                    onClick={() => setReportType('compliance')}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      reportType === 'compliance'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <svg className="w-8 h-8 mx-auto mb-2" style={{ color: reportType === 'compliance' ? '#0047AB' : '#6B7280' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="text-sm font-semibold">Compliance</div>
                  </button>

                  <button
                    onClick={() => setReportType('executive')}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      reportType === 'executive'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <svg className="w-8 h-8 mx-auto mb-2" style={{ color: reportType === 'executive' ? '#0047AB' : '#6B7280' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <div className="text-sm font-semibold">Executive</div>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#0047AB' }}>
                  Date Range
                </label>
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all"
                >
                  <option value="7days">Last 7 days</option>
                  <option value="30days">Last 30 days</option>
                  <option value="90days">Last 90 days</option>
                  <option value="custom">Custom range</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#0047AB' }}>
                  Include Assets
                </label>
                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span className="text-sm">All assets</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input type="checkbox" className="rounded" />
                    <span className="text-sm">Critical assets only</span>
                  </label>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowGenerateModal(false)}
                  className="flex-1 px-6 py-3 border-2 rounded-xl font-semibold hover:bg-gray-50 transition-all"
                  style={{ borderColor: '#0047AB', color: '#0047AB' }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateReport}
                  className="flex-1 px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
                  style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                >
                  Generate Report
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
