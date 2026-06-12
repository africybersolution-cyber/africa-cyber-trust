'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'billing' | 'team'>('profile');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      router.push('/login');
    } else {
      setLoading(false);
    }
  }, [user, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
      {/* Top Navigation */}
      <nav className="bg-slate-900/90 border-b backdrop-blur-sm sticky top-0 z-50" style={{ borderColor: 'rgba(0, 71, 171, 0.3)' }}>
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <a href="/dashboard" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div className="hidden md:block">
                <div className="text-sm font-bold">
                  <span style={{ color: '#0047AB' }}>AFRICA CYBER </span>
                  <span style={{ color: '#DAA520' }}>TRUST</span>
                </div>
              </div>
            </a>

            <div className="flex items-center gap-4">
              <a href="/dashboard" className="text-gray-400 hover:text-white">
                ← Back to Dashboard
              </a>
              <button onClick={() => logout()} className="px-4 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-slate-800">
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account preferences and security</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl overflow-hidden" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
              <button
                onClick={() => setActiveTab('profile')}
                className={`w-full px-6 py-4 text-left font-medium transition-all ${
                  activeTab === 'profile' ? 'text-white' : 'text-gray-400 hover:text-white'
                }`}
                style={activeTab === 'profile' ? { background: 'rgba(0, 71, 171, 0.3)' } : {}}
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Profile
                </div>
              </button>

              <button
                onClick={() => setActiveTab('security')}
                className={`w-full px-6 py-4 text-left font-medium transition-all ${
                  activeTab === 'security' ? 'text-white' : 'text-gray-400 hover:text-white'
                }`}
                style={activeTab === 'security' ? { background: 'rgba(0, 71, 171, 0.3)' } : {}}
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  Security
                </div>
              </button>

              <button
                onClick={() => setActiveTab('billing')}
                className={`w-full px-6 py-4 text-left font-medium transition-all ${
                  activeTab === 'billing' ? 'text-white' : 'text-gray-400 hover:text-white'
                }`}
                style={activeTab === 'billing' ? { background: 'rgba(0, 71, 171, 0.3)' } : {}}
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                  Billing
                </div>
              </button>

              <button
                onClick={() => setActiveTab('team')}
                className={`w-full px-6 py-4 text-left font-medium transition-all ${
                  activeTab === 'team' ? 'text-white' : 'text-gray-400 hover:text-white'
                }`}
                style={activeTab === 'team' ? { background: 'rgba(0, 71, 171, 0.3)' } : {}}
              >
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  Team
                </div>
              </button>
            </div>
          </div>

          {/* Content Area */}
          <div className="lg:col-span-3">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                  <h2 className="text-xl font-bold text-white mb-6">Profile Information</h2>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
                      <input
                        type="text"
                        defaultValue={user?.name || ''}
                        className="w-full px-4 py-3 bg-slate-900/50 border rounded-lg text-white"
                        style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                      <input
                        type="email"
                        defaultValue={user?.email || ''}
                        className="w-full px-4 py-3 bg-slate-900/50 border rounded-lg text-white"
                        style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Company</label>
                      <input
                        type="text"
                        placeholder="Your Company Ltd"
                        className="w-full px-4 py-3 bg-slate-900/50 border rounded-lg text-white"
                        style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                      />
                    </div>

                    <button className="px-6 py-3 rounded-lg font-semibold text-white" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                      Save Changes
                    </button>
                  </div>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                  <h2 className="text-xl font-bold text-white mb-4">Danger Zone</h2>
                  <p className="text-gray-400 text-sm mb-4">Permanently delete your account and all data</p>
                  <button className="px-6 py-3 rounded-lg font-semibold bg-red-600 text-white hover:bg-red-700">
                    Delete Account
                  </button>
                </div>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                  <h2 className="text-xl font-bold text-white mb-6">Change Password</h2>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Current Password</label>
                      <input
                        type="password"
                        className="w-full px-4 py-3 bg-slate-900/50 border rounded-lg text-white"
                        style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">New Password</label>
                      <input
                        type="password"
                        className="w-full px-4 py-3 bg-slate-900/50 border rounded-lg text-white"
                        style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Confirm New Password</label>
                      <input
                        type="password"
                        className="w-full px-4 py-3 bg-slate-900/50 border rounded-lg text-white"
                        style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                      />
                    </div>

                    <button className="px-6 py-3 rounded-lg font-semibold text-white" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                      Update Password
                    </button>
                  </div>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-bold text-white mb-1">Two-Factor Authentication</h2>
                      <p className="text-gray-400 text-sm">Add an extra layer of security</p>
                    </div>
                    <div className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400">
                      Not Enabled
                    </div>
                  </div>
                  <button className="px-6 py-3 rounded-lg font-semibold bg-slate-700 text-white hover:bg-slate-600">
                    Enable 2FA
                  </button>
                </div>
              </div>
            )}

            {/* Billing Tab */}
            {activeTab === 'billing' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-xl font-bold text-white mb-1">Current Plan</h2>
                      <p className="text-gray-400 text-sm">You are on the Professional plan</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold" style={{ color: '#DAA520' }}>$199</div>
                      <div className="text-sm text-gray-400">per month</div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <div className="p-4 rounded-lg bg-slate-900/50">
                      <div className="text-sm text-gray-400 mb-1">Next billing date</div>
                      <div className="font-medium text-white">July 11, 2026</div>
                    </div>
                    <div className="p-4 rounded-lg bg-slate-900/50">
                      <div className="text-sm text-gray-400 mb-1">Payment method</div>
                      <div className="font-medium text-white">•••• 4242</div>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => router.push('/pricing')}
                      className="px-6 py-3 rounded-lg font-semibold text-white"
                      style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}
                    >
                      Upgrade Plan
                    </button>
                    <button className="px-6 py-3 rounded-lg font-semibold bg-slate-700 text-white hover:bg-slate-600">
                      Cancel Subscription
                    </button>
                  </div>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                  <h2 className="text-xl font-bold text-white mb-4">Billing History</h2>
                  <div className="space-y-3">
                    {[
                      { date: 'Jun 11, 2026', amount: '$199.00', status: 'Paid' },
                      { date: 'May 11, 2026', amount: '$199.00', status: 'Paid' },
                      { date: 'Apr 11, 2026', amount: '$199.00', status: 'Paid' },
                    ].map((invoice, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 rounded-lg bg-slate-900/50">
                        <div>
                          <div className="font-medium text-white">{invoice.date}</div>
                          <div className="text-sm text-gray-400">{invoice.amount}</div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                            {invoice.status}
                          </span>
                          <button className="text-sm font-medium hover:underline" style={{ color: '#DAA520' }}>
                            Download
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Team Tab */}
            {activeTab === 'team' && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-xl font-bold text-white mb-1">Team Members</h2>
                      <p className="text-sm text-gray-400">Manage your team and their access levels</p>
                    </div>
                    <button className="px-4 py-2 rounded-lg font-semibold text-white" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                      + Invite Member
                    </button>
                  </div>

                  <div className="space-y-3">
                    {[
                      { name: user?.name || 'You', email: user?.email || '', role: 'Owner', status: 'Active', permissions: 'Full Access' },
                      { name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active', permissions: 'All except billing' },
                      { name: 'Jane Smith', email: 'jane@example.com', role: 'Member', status: 'Pending', permissions: 'View only' },
                    ].map((member, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 rounded-lg bg-slate-900/50 hover:bg-slate-900/70 transition-all">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                            {member.name[0]}
                          </div>
                          <div>
                            <div className="font-medium text-white">{member.name}</div>
                            <div className="text-sm text-gray-400">{member.email}</div>
                            <div className="text-xs text-gray-500 mt-1">{member.permissions}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <select
                            value={member.role}
                            className="px-3 py-1 rounded-lg text-sm font-medium bg-slate-700 text-white border-0"
                            style={{ background: 'rgba(30, 41, 59, 0.8)' }}
                          >
                            <option value="Owner">Owner</option>
                            <option value="Admin">Admin</option>
                            <option value="Member">Member</option>
                            <option value="Viewer">Viewer</option>
                          </select>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            member.status === 'Active' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                          }`}>
                            {member.status}
                          </span>
                          {member.role !== 'Owner' && (
                            <button className="p-2 rounded-lg text-red-400 hover:text-red-300 hover:bg-slate-700">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-6 p-6 rounded-lg border-2 border-dashed" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                    <div className="text-center text-gray-400 mb-4">
                      <p className="mb-1 font-medium text-white">Invite team members to collaborate</p>
                      <p className="text-sm">Your Professional plan includes up to 5 team members</p>
                    </div>
                    <div className="flex gap-3 max-w-md mx-auto">
                      <input
                        type="email"
                        placeholder="email@example.com"
                        className="flex-1 px-4 py-2 bg-slate-900/50 border rounded-lg text-white text-sm"
                        style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}
                      />
                      <button className="px-6 py-2 rounded-lg font-semibold text-white" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100())' }}>
                        Send Invite
                      </button>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6" style={{ borderColor: 'rgba(71, 85, 105, 0.5)' }}>
                  <h2 className="text-xl font-bold text-white mb-4">Role Permissions</h2>
                  <div className="space-y-4">
                    {[
                      { role: 'Owner', color: '#DAA520', permissions: ['Full system access', 'Manage billing', 'Delete account', 'Manage all members'] },
                      { role: 'Admin', color: '#0047AB', permissions: ['Manage assets & scans', 'View reports', 'Invite members', 'View billing'] },
                      { role: 'Member', color: '#10b981', permissions: ['Run scans', 'View own assets', 'View reports', 'Limited access'] },
                      { role: 'Viewer', color: '#6b7280', permissions: ['View reports only', 'No asset management', 'No scan permissions', 'Read-only'] },
                    ].map((roleInfo, idx) => (
                      <div key={idx} className="p-4 rounded-lg bg-slate-900/50">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-xs" style={{ background: roleInfo.color }}>
                            {roleInfo.role[0]}
                          </div>
                          <h3 className="font-bold text-white">{roleInfo.role}</h3>
                        </div>
                        <div className="grid md:grid-cols-2 gap-2">
                          {roleInfo.permissions.map((perm, pidx) => (
                            <div key={pidx} className="flex items-center gap-2 text-sm text-gray-300">
                              <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              {perm}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
