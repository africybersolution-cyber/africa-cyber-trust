'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { config } from '@/lib/config';
import DashboardLayout from '@/components/DashboardLayout';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  status: string;
  joined_date: string;
}

interface TeamStats {
  total_members: number;
  member_limit: number;
  can_add_members: boolean;
  access_level: string;
}

export default function TeamPage() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [teamStats, setTeamStats] = useState<TeamStats | null>(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'admin' | 'analyst' | 'viewer'>('analyst');
  const [inviting, setInviting] = useState(false);

  // Load team members and stats
  useEffect(() => {
    const loadData = async () => {
      if (!token) return;

      try {
        // Load members
        const membersRes = await fetch(`${config.apiUrl}/api/team/members`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (membersRes.ok) {
          setTeamMembers(await membersRes.json());
        }

        // Load stats
        const statsRes = await fetch(`${config.apiUrl}/api/team/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (statsRes.ok) {
          setTeamStats(await statsRes.json());
        }
      } catch (error) {
        console.error('Error loading team data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [token]);

  const handleInvite = async () => {
    if (!inviteEmail) {
      alert('Please enter an email address');
      return;
    }

    setInviting(true);

    try {
      const res = await fetch(`${config.apiUrl}/api/team/invite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: inviteEmail,
          role: inviteRole
        })
      });

      if (res.ok) {
        const data = await res.json();
        alert(`✅ ${data.message}\n\nAn invitation email will be sent to ${inviteEmail}`);
        setShowInviteModal(false);
        setInviteEmail('');
      } else {
        const error = await res.json();
        alert(`❌ ${error.detail || 'Failed to send invitation'}`);
      }
    } catch (error) {
      console.error('Error sending invite:', error);
      alert('❌ Error sending invitation. Please try again.');
    } finally {
      setInviting(false);
    }
  };

  const handleRemoveMember = async (memberId: string, memberEmail: string) => {
    if (!confirm(`Are you sure you want to remove ${memberEmail} from the team?`)) {
      return;
    }

    try {
      const res = await fetch(`${config.apiUrl}/api/team/members/${memberId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        alert('✅ Member removed successfully');
        // Reload members
        setTeamMembers(teamMembers.filter(m => m.id !== memberId));
      } else {
        const error = await res.json();
        alert(`❌ ${error.detail || 'Failed to remove member'}`);
      }
    } catch (error) {
      console.error('Error removing member:', error);
      alert('❌ Error removing member. Please try again.');
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'admin': return '#EF4444';
      case 'analyst': return BLUE;
      case 'viewer': return '#10B981';
      default: return '#6B7280';
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="Team" subtitle="Manage team members and permissions">
        <div className="text-center py-12">
          <div className="text-white text-xl">Loading team members...</div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Team" subtitle="Manage team members and permissions">
      <div className="space-y-6">
        {/* Team Limit Banner */}
        {teamStats && !teamStats.can_add_members && (
          <div className="bg-yellow-900/20 border-2 border-yellow-600/50 rounded-xl p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-bold text-yellow-400 mb-2">Team Member Limit Reached</h3>
                <p className="text-gray-300 mb-4">
                  You've reached your limit of {teamStats.member_limit} team member{teamStats.member_limit > 1 ? 's' : ''} on the{' '}
                  <span className="font-semibold capitalize">{teamStats.access_level}</span> plan.
                </p>
                <a
                  href="/dashboard/billing"
                  className="inline-block px-6 py-3 rounded-xl font-semibold text-white"
                  style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
                >
                  {teamStats.access_level === 'personal' ? 'Upgrade to Professional ($79/month)' : 'Upgrade to Enterprise'}
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-6">
          <div className="cyber-card p-6">
            <div className="text-3xl font-bold text-white mb-1">
              {teamMembers.length}
              {teamStats && <span className="text-lg text-gray-500"> / {teamStats.member_limit === 999 ? '∞' : teamStats.member_limit}</span>}
            </div>
            <div className="text-sm text-cyber-muted">Team Members Used</div>
          </div>
          <div className="cyber-card p-6">
            <div className="text-3xl font-bold text-green-400">
              {teamMembers.filter(m => m.status.toLowerCase() === 'active').length}
            </div>
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
            onClick={() => teamStats?.can_add_members ? setShowInviteModal(true) : null}
            disabled={!teamStats?.can_add_members}
            className={`px-6 py-3 rounded-xl font-semibold text-white transition-opacity ${
              teamStats?.can_add_members ? 'hover:opacity-90' : 'opacity-50 cursor-not-allowed'
            }`}
            style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
          >
            + Invite Team Member
          </button>
        </div>

        {/* Team Members Table */}
        <div className="cyber-card-raised p-6">
          <h2 className="text-xl font-bold text-white mb-6">Team Members</h2>

          {teamMembers.length === 0 ? (
            <div className="text-center py-12 text-cyber-muted">
              No team members yet. Invite your first member!
            </div>
          ) : (
            <div className="space-y-3">
              {teamMembers.map((member) => (
                <div key={member.id} className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-all">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg" style={{ background: BLUE }}>
                      {member.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-semibold text-white">{member.name}</div>
                      <div className="text-sm text-cyber-muted">{member.email}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <div
                        className="inline-block px-3 py-1 rounded-lg text-xs font-bold uppercase"
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
                      <div className="text-xs text-cyber-muted">{member.joined_date}</div>
                    </div>

                    <button
                      onClick={() => handleRemoveMember(member.id, member.email)}
                      className="px-4 py-2 text-sm text-cyber-muted hover:text-red-400 transition-colors"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
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
                disabled={inviting}
                className="w-full px-6 py-3 rounded-xl font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
              >
                {inviting ? 'Sending...' : 'Send Invitation'}
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
