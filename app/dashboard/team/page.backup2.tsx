'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

export default function TeamPage() {
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'admin' | 'analyst' | 'viewer'>('analyst');

  const teamMembers = [
    { id: 1, name: 'Admin User', email: 'admin@company.com', role: 'Admin', status: 'Active', joinedDate: 'Jan 15, 2026' },
    { id: 2, name: 'Security Analyst', email: 'analyst@company.com', role: 'Analyst', status: 'Active', joinedDate: 'Feb 20, 2026' },
    { id: 3, name: 'Team Viewer', email: 'viewer@company.com', role: 'Viewer', status: 'Active', joinedDate: 'Mar 5, 2026' },
  ];

  const handleInvite = () => {
    if (!inviteEmail) {
      alert('Please enter an email address');
      return;
    }
    alert(`Invite will be sent to: ${inviteEmail}\nRole: ${inviteRole}\n\nThis will connect to the backend user management API!`);
    setShowInviteModal(false);
    setInviteEmail('');
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'admin': return '#EF4444';
      case 'analyst': return BLUE;
      case 'viewer': return '#10B981';
      default: return '#6B7280';
    }
  };

  return (
    <DashboardLayout title="Team" subtitle="Manage team members and permissions">
      <div className="space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-6">
          <div className="cyber-card p-6">
            <div className="text-3xl font-bold text-white mb-1">{teamMembers.length}</div>
            <div className="text-sm text-cyber-muted">Total Members</div>
          </div>
          <div className="cyber-card p-6">
            <div className="text-3xl font-bold text-green-400">{teamMembers.filter(m => m.status === 'Active').length}</div>
            <div className="text-sm text-cyber-muted">Active Members</div>
          </div>
          <div className="cyber-card p-6">
            <div className="text-3xl font-bold" style={{ color: BLUE }}>0</div>
            <div className="text-sm text-cyber-muted">Pending Invites</div>
          </div>
        </div>

        {/* Invite Button */}
        <div>
          <button
            onClick={() => setShowInviteModal(true)}
            className="px-6 py-3 rounded-xl font-semibold text-white transition-opacity hover:opacity-90"
            style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
          >
            + Invite Team Member
          </button>
        </div>

        {/* Team Members Table */}
        <div className="cyber-card-raised p-6">
          <h2 className="text-xl font-bold text-white mb-6">Team Members</h2>

          <div className="space-y-3">
            {teamMembers.map((member) => (
              <div key={member.id} className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-all">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg" style={{ background: BLUE }}>
                    {member.name.charAt(0)}
                  </div>
                  <div>
                    <div className="font-semibold text-white">{member.name}</div>
                    <div className="text-sm text-cyber-muted">{member.email}</div>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <div
                      className="inline-block px-3 py-1 rounded-lg text-xs font-bold"
                      style={{
                        background: getRoleBadgeColor(member.role) + '20',
                        color: getRoleBadgeColor(member.role)
                      }}
                    >
                      {member.role}
                    </div>
                  </div>

                  <div className="text-center min-w-[100px]">
                    <div className="text-sm text-white">{member.status}</div>
                    <div className="text-xs text-cyber-muted">{member.joinedDate}</div>
                  </div>

                  <button className="px-4 py-2 text-sm text-cyber-muted hover:text-red-400 transition-colors">
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Role Descriptions */}
        <div className="cyber-card p-6">
          <h3 className="text-lg font-bold text-white mb-4">Role Permissions</h3>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full mt-2 bg-red-400"></div>
              <div>
                <div className="font-semibold text-white">Admin</div>
                <div className="text-sm text-cyber-muted">Full access to all features, can manage team and billing</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full mt-2" style={{ background: BLUE }}></div>
              <div>
                <div className="font-semibold text-white">Analyst</div>
                <div className="text-sm text-cyber-muted">Can add assets, run scans, and view reports</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full mt-2 bg-green-400"></div>
              <div>
                <div className="font-semibold text-white">Viewer</div>
                <div className="text-sm text-cyber-muted">Read-only access to scans and reports</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setShowInviteModal(false)}>
          <div className="cyber-card-raised max-w-md w-full p-8" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Invite Team Member</h2>
              <button
                onClick={() => setShowInviteModal(false)}
                className="text-cyber-muted hover:text-white text-3xl font-light"
              >
                ×
              </button>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-white mb-2">Email Address</label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="colleague@company.com"
                  className="w-full px-4 py-3 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-white mb-3">Role</label>
                <div className="space-y-2">
                  {(['admin', 'analyst', 'viewer'] as const).map((role) => (
                    <div
                      key={role}
                      onClick={() => setInviteRole(role)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        inviteRole === role
                          ? 'border-blue-500 bg-blue-500/10'
                          : 'border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <div className="font-semibold text-white capitalize">{role}</div>
                      <div className="text-sm text-cyber-muted">
                        {role === 'admin' && 'Full access to all features'}
                        {role === 'analyst' && 'Can add assets and run scans'}
                        {role === 'viewer' && 'Read-only access'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={handleInvite}
                className="w-full px-6 py-3 rounded-xl font-semibold text-white transition-opacity hover:opacity-90"
                style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
              >
                Send Invitation
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
