'use client';

import { useState } from 'react';

export default function AlertsPage() {
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [smsEnabled, setSmsEnabled] = useState(true);
  const [whatsappEnabled, setWhatsappEnabled] = useState(false);
  const [slackEnabled, setSlackEnabled] = useState(false);

  const [alertSettings, setAlertSettings] = useState({
    criticalIssues: true,
    mediumIssues: true,
    lowIssues: false,
    scanComplete: true,
    newVulnerability: true,
    assetOffline: true,
    teamChanges: false,
  });

  const recentAlerts = [
    {
      id: 1,
      severity: 'high',
      title: 'Suspicious redirect detected on payment page',
      asset: 'api.techstartup.com',
      time: '2 hours ago',
      read: false,
    },
    {
      id: 2,
      severity: 'medium',
      title: 'Missing HSTS header detected',
      asset: 'techstartup.com',
      time: '1 day ago',
      read: true,
    },
    {
      id: 3,
      severity: 'low',
      title: 'SSL certificate expires in 45 days',
      asset: 'techstartup.com',
      time: '2 days ago',
      read: true,
    },
    {
      id: 4,
      severity: 'high',
      title: 'Malware detected in uploaded file',
      asset: 'TechStartup Mobile',
      time: '3 days ago',
      read: true,
    },
  ];

  const handleSave = () => {
    // TODO: Connect to backend API
    alert('Alert settings saved!');
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
              Alert Configuration
            </h1>
            <p className="text-gray-600">Manage how and when you receive security alerts</p>
          </div>
          <button
            onClick={handleSave}
            className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
            style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
          >
            Save Changes
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Notification Channels */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-xl font-bold mb-6" style={{ color: '#0047AB' }}>Notification Channels</h2>

              <div className="space-y-6">
                {/* Email */}
                <div className="flex items-start justify-between p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-1">Email Notifications</h3>
                      <p className="text-sm text-gray-600 mb-2">john@techstartup.com</p>
                      <p className="text-xs text-gray-500">Instant delivery • Always available</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={emailEnabled}
                      onChange={(e) => setEmailEnabled(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {/* SMS */}
                <div className="flex items-start justify-between p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}>
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-1">SMS Notifications</h3>
                      <p className="text-sm text-gray-600 mb-2">+254 712 345 678</p>
                      <p className="text-xs text-gray-500">Critical alerts only • High-priority</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={smsEnabled}
                      onChange={(e) => setSmsEnabled(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {/* WhatsApp */}
                <div className="flex items-start justify-between p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-green-500">
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-1">WhatsApp Notifications</h3>
                      <p className="text-sm text-gray-600 mb-2">+254 712 345 678</p>
                      <p className="text-xs text-gray-500">Not connected • Business Plan feature</p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={whatsappEnabled}
                      onChange={(e) => setWhatsappEnabled(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {/* Slack */}
                <div className="flex items-start justify-between p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-purple-500">
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-1">Slack Integration</h3>
                      <p className="text-sm text-gray-600 mb-2">Not connected</p>
                      <p className="text-xs text-gray-500">Send alerts to Slack channels</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-purple-50 text-purple-700 rounded-lg font-semibold text-sm hover:bg-purple-100 transition-all">
                    Connect
                  </button>
                </div>
              </div>
            </div>

            {/* Alert Types */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-xl font-bold mb-6" style={{ color: '#0047AB' }}>Alert Types</h2>

              <div className="space-y-4">
                {Object.entries({
                  'Critical Issues': 'criticalIssues',
                  'Medium Priority Issues': 'mediumIssues',
                  'Low Priority Issues': 'lowIssues',
                  'Scan Complete': 'scanComplete',
                  'New Vulnerability Detected': 'newVulnerability',
                  'Asset Offline': 'assetOffline',
                  'Team Changes': 'teamChanges',
                }).map(([label, key]) => (
                  <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                    <div>
                      <h3 className="font-semibold text-gray-900">{label}</h3>
                      <p className="text-sm text-gray-500">
                        {key === 'criticalIssues' && 'High-severity security threats'}
                        {key === 'mediumIssues' && 'Medium-severity vulnerabilities'}
                        {key === 'lowIssues' && 'Low-severity informational alerts'}
                        {key === 'scanComplete' && 'Notify when scheduled scans finish'}
                        {key === 'newVulnerability' && 'New CVEs affecting your assets'}
                        {key === 'assetOffline' && 'Asset becomes unavailable'}
                        {key === 'teamChanges' && 'Member joins or leaves team'}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={alertSettings[key as keyof typeof alertSettings]}
                        onChange={(e) => setAlertSettings({ ...alertSettings, [key]: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Alerts */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4" style={{ color: '#0047AB' }}>Recent Alerts</h3>

              <div className="space-y-3">
                {recentAlerts.map((alert) => (
                  <div key={alert.id} className={`p-4 rounded-xl ${alert.read ? 'bg-gray-50' : 'bg-blue-50 border-2 border-blue-200'}`}>
                    <div className="flex items-start gap-3">
                      <div className={`w-3 h-3 rounded-full mt-1 ${
                        alert.severity === 'high' ? 'bg-red-500' :
                        alert.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`} />
                      <div className="flex-1">
                        <h4 className="font-semibold text-sm text-gray-900 mb-1">{alert.title}</h4>
                        <p className="text-xs text-gray-500">{alert.asset}</p>
                        <p className="text-xs text-gray-400 mt-1">{alert.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button className="w-full mt-4 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg font-semibold text-sm hover:bg-blue-100 transition-all">
                View All Alerts
              </button>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl shadow-lg p-6 border-2 border-green-200">
              <div className="flex items-start gap-3 mb-4">
                <svg className="w-6 h-6 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="font-bold text-green-900 mb-1">Alerts Active</h4>
                  <p className="text-sm text-green-800">
                    You're receiving security alerts via Email and SMS
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
