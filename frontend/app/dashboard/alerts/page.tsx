'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { config } from '@/lib/config';
import DashboardLayout from '@/components/DashboardLayout';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

export default function AlertsPage() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [emailEnabled, setEmailEnabled] = useState(true);

  const [alertSettings, setAlertSettings] = useState({
    criticalIssues: true,
    highIssues: true,
    mediumIssues: true,
    lowIssues: false,
    scanComplete: true,
    newVulnerability: true,
    assetOffline: true,
  });

  // Load settings from API
  useEffect(() => {
    const loadSettings = async () => {
      if (!token) return;

      try {
        const res = await fetch(`${config.apiUrl}/api/alerts/settings`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (res.ok) {
          const data = await res.json();
          const settings = data.settings;

          setEmailEnabled(settings.email_enabled);

          setAlertSettings({
            criticalIssues: settings.critical_issues,
            highIssues: settings.high_issues,
            mediumIssues: settings.medium_issues,
            lowIssues: settings.low_issues,
            scanComplete: settings.scan_complete,
            newVulnerability: settings.new_vulnerability,
            assetOffline: settings.asset_offline
          });
        }
      } catch (error) {
        console.error('Error loading alert settings:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, [token]);

  const handleSave = async () => {
    if (!token) return;

    setSaving(true);

    try {
      const res = await fetch(`${config.apiUrl}/api/alerts/settings`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email_enabled: emailEnabled,
          sms_enabled: false,  // Coming soon
          whatsapp_enabled: false,  // Coming soon
          slack_enabled: false,  // Coming soon
          critical_issues: alertSettings.criticalIssues,
          high_issues: alertSettings.highIssues,
          medium_issues: alertSettings.mediumIssues,
          low_issues: alertSettings.lowIssues,
          scan_complete: alertSettings.scanComplete,
          new_vulnerability: alertSettings.newVulnerability,
          asset_offline: alertSettings.assetOffline
        })
      });

      if (res.ok) {
        alert('✅ Alert settings saved successfully!');
      } else {
        alert('❌ Failed to save settings. Please try again.');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('❌ Error saving settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const Toggle = ({ enabled, onChange }: { enabled: boolean; onChange: (v: boolean) => void }) => (
    <label className="relative inline-flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={enabled}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only peer"
      />
      <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
    </label>
  );

  return (
    <DashboardLayout title="Alerts" subtitle="Configure security alert notifications">
      <div className="space-y-8">
        {/* Notification Channels */}
        <div className="cyber-card-raised p-6">
          <h2 className="text-xl font-bold text-white mb-4">Notification Channels</h2>
          <p className="text-cyber-muted text-sm mb-6">Choose how you want to receive security alerts</p>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `${BLUE}20` }}>
                  <svg className="w-5 h-5" style={{ color: BLUE }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-white">Email Notifications</div>
                  <div className="text-sm text-cyber-muted">Receive alerts via email</div>
                </div>
              </div>
              <Toggle enabled={emailEnabled} onChange={setEmailEnabled} />
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg opacity-60">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-gray-700">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-white flex items-center gap-2">
                    SMS Notifications
                    <span className="text-xs px-2 py-1 bg-yellow-600/20 text-yellow-400 rounded-full border border-yellow-600/30">Coming Soon</span>
                  </div>
                  <div className="text-sm text-cyber-muted">Receive alerts via text message</div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg opacity-60">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-gray-700">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-white flex items-center gap-2">
                    WhatsApp
                    <span className="text-xs px-2 py-1 bg-yellow-600/20 text-yellow-400 rounded-full border border-yellow-600/30">Coming Soon</span>
                  </div>
                  <div className="text-sm text-cyber-muted">Receive alerts via WhatsApp</div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg opacity-60">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-gray-700">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-white flex items-center gap-2">
                    Slack Integration
                    <span className="text-xs px-2 py-1 bg-yellow-600/20 text-yellow-400 rounded-full border border-yellow-600/30">Coming Soon</span>
                  </div>
                  <div className="text-sm text-cyber-muted">Send alerts to Slack channel</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Alert Types */}
        <div className="cyber-card-raised p-6">
          <h2 className="text-xl font-bold text-white mb-4">Alert Types</h2>
          <p className="text-cyber-muted text-sm mb-6">Choose which events trigger notifications</p>

          <div className="space-y-3">
            {Object.entries(alertSettings).map(([key, value]) => (
              <label key={key} className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg cursor-pointer hover:bg-slate-800/50 transition-all">
                <span className="text-white capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => setAlertSettings({ ...alertSettings, [key]: e.target.checked })}
                  className="w-4 h-4 rounded border-gray-600 bg-gray-700 focus:ring-blue-600 focus:ring-2"
                />
              </label>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-8 py-3 rounded-xl font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
          >
            {saving ? 'Saving...' : 'Save Alert Settings'}
          </button>
        </div>

        {/* Info */}
        <div className="cyber-card p-6">
          <div className="flex items-start gap-4">
            <svg className="w-6 h-6 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-semibold text-white mb-2">About Alerts</h4>
              <p className="text-sm text-cyber-muted leading-relaxed">
                Configure how you want to be notified about security events. Critical issues will always
                trigger immediate notifications. You can customize notification channels and alert types
                based on your preferences.
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
