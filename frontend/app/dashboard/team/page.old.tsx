'use client';

import { useState } from 'react';

export default function TeamPage() {
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteData, setInviteData] = useState({
    email: '',
    role: 'member',
    message: '',
  });

  const teamMembers = [
    {
      id: 1,
      name: 'John Doe',
      email: 'john@techstartup.com',
      role: 'Owner',
      avatar: 'JD',
      status: 'Active',
      joinedDate: 'Jan 15, 2026',
      lastActive: '2 hours ago',
    },
    {
      id: 2,
      name: 'Sarah Smith',
      email: 'sarah@techstartup.com',
      role: 'Admin',
      avatar: 'SS',
      status: 'Active',
      joinedDate: 'Feb 3, 2026',
      lastActive: '1 day ago',
    },
    {
      id: 3,
      name: 'Mike Johnson',
      email: 'mike@techstartup.com',
      role: 'Member',
      avatar: 'MJ',
      status: 'Active',
      joinedDate: 'Mar 10, 2026',
      lastActive: '3 hours ago',
    },
    {
      id: 4,
      name: 'Emily Chen',
      email: 'emily@techstartup.com',
      role: 'Member',
      avatar: 'EC',
      status: 'Invited',
      joinedDate: 'Pending',
      lastActive: '-',
    },
  ];

  const roles = [
    {
      name: 'Owner',
      description: 'Full access to all features, billing, and team management',
      permissions: ['Full access', 'Manage billing', 'Delete company'],
    },
    {
      name: 'Admin',
      description: 'Manage assets, scans, and team members (except owner)',
      permissions: ['Manage assets', 'View reports', 'Invite members', 'Configure alerts'],
    },
    {
      name: 'Member',
      description: 'View assets and reports, run scans',
      permissions: ['View assets', 'Run scans', 'View reports'],
    },
    {
      name: 'Viewer',
      description: 'Read-only access to reports and dashboards',
      permissions: ['View reports', 'View dashboard'],
    },
  ];

  const handleInvite = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Connect to backend API
    alert(`Invitation sent to ${inviteData.email}!`);
    setShowInviteModal(false);
    setInviteData({ email: '', role: 'member', message: '' });
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
              Team Management
            </h1>
            <p className="text-gray-600">Manage your team members and their permissions</p>
          </div>
          <button
            onClick={() => setShowInviteModal(true)}
            className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
            style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Invite Member
          </button>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-2xl font-bold mb-1" style={{ color: '#0047AB' }}>4</div>
            <div className="text-gray-600 text-sm">Total Members</div>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-2xl font-bold text-green-600 mb-1">3</div>
            <div className="text-gray-600 text-sm">Active</div>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-2xl font-bold text-yellow-600 mb-1">1</div>
            <div className="text-gray-600 text-sm">Pending Invites</div>
          </div>
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="text-2xl font-bold mb-1" style={{ color: '#DAA520' }}>10</div>
            <div className="text-gray-600 text-sm">Seats Available</div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Team Members List */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-bold mb-4" style={{ color: '#0047AB' }}>Team Members</h2>

            {teamMembers.map((member) => (
              <div key={member.id} className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div
                      className="w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-lg"
                      style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                    >
                      {member.avatar}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 mb-1">{member.name}</h3>
                      <div className="text-sm text-gray-500 mb-2">{member.email}</div>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div>
                          <span className="font-semibold">Joined:</span> {member.joinedDate}
                        </div>
                        <div>
                          <span className="font-semibold">Last Active:</span> {member.lastActive}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div
                        className="px-3 py-1 rounded-full text-xs font-semibold mb-2"
                        style={{
                          background: member.role === 'Owner' ? '#0047AB' : member.role === 'Admin' ? '#DAA520' : '#1E90FF',
                          color: 'white'
                        }}
                      >
                        {member.role}
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          member.status === 'Active'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {member.status}
                      </span>
                    </div>

                    {member.role !== 'Owner' && (
                      <button className="p-2 hover:bg-gray-100 rounded-lg transition-all">
                        <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Roles & Permissions */}
          <div>
            <h2 className="text-xl font-bold mb-4" style={{ color: '#0047AB' }}>Roles & Permissions</h2>
            <div className="space-y-4">
              {roles.map((role, index) => (
                <div key={index} className="bg-white rounded-2xl shadow-lg p-6">
                  <h3 className="font-bold text-lg mb-2" style={{ color: '#0047AB' }}>{role.name}</h3>
                  <p className="text-sm text-gray-600 mb-4">{role.description}</p>
                  <div className="space-y-2">
                    {role.permissions.map((permission, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm">
                        <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="text-gray-700">{permission}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold" style={{ color: '#0047AB' }}>Invite Team Member</h2>
              <button
                onClick={() => setShowInviteModal(false)}
                className="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleInvite} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#0047AB' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={inviteData.email}
                  onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all"
                  placeholder="colleague@company.com"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#0047AB' }}>
                  Role
                </label>
                <select
                  value={inviteData.role}
                  onChange={(e) => setInviteData({ ...inviteData, role: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all"
                >
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#0047AB' }}>
                  Personal Message (Optional)
                </label>
                <textarea
                  rows={3}
                  value={inviteData.message}
                  onChange={(e) => setInviteData({ ...inviteData, message: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all"
                  placeholder="Add a personal note..."
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="flex-1 px-6 py-3 border-2 rounded-xl font-semibold hover:bg-gray-50 transition-all"
                  style={{ borderColor: '#0047AB', color: '#0047AB' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
                  style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                >
                  Send Invite
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
