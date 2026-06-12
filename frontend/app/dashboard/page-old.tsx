'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

interface DashboardStats {
  assetsCount: number;
  scansToday: number;
  issuesFound: number;
  teamMembers: number;
}

export default function DashboardPage() {
  const { user, company, logout } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>({
    assetsCount: 0,
    scansToday: 0,
    issuesFound: 0,
    teamMembers: 1
  });
  const [loading, setLoading] = useState(true);
  const [assets, setAssets] = useState<any[]>([]);

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;

        // Fetch assets
        const assetsRes = await fetch('/api/assets/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (assetsRes.ok) {
          const assetsData = await assetsRes.json();
          console.log('📊 Assets loaded:', assetsData);

          // Store assets for display
          setAssets(Array.isArray(assetsData) ? assetsData : []);

          // Calculate stats from assets
          const assetCount = Array.isArray(assetsData) ? assetsData.length : 0;
          const totalIssues = assetsData.reduce((sum: number, a: any) => sum + (a.findings_count || 0), 0);

          // Count scans today (assets that have last_scan_at today)
          const today = new Date().toDateString();
          const scansToday = assetsData.filter((a: any) => {
            if (!a.last_scan_at) return false;
            const scanDate = new Date(a.last_scan_at).toDateString();
            return scanDate === today;
          }).length;

          setStats({
            assetsCount: assetCount,
            scansToday: scansToday,
            issuesFound: totalIssues,
            teamMembers: 1
          });
        } else {
          console.error('❌ Failed to fetch assets:', assetsRes.status, await assetsRes.text());
        }

        setLoading(false);
      } catch (error) {
        console.error('❌ Error fetching dashboard stats:', error);
        setLoading(false);
      }
    };

    if (user) {
      fetchDashboardStats();
    }
  }, [user]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Top Navigation */}
      <nav className="border-b border-gray-200 bg-white sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-sm" style={{ color: '#0047AB' }}>
                  {company ? company.name : user?.name}
                </div>
                <div className="text-xs text-gray-500">
                  {company ? `${company.plan} Plan` : user?.role}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-red-600 transition-colors"
              >
                Logout
              </button>
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center" style={{ color: '#0047AB' }}>
                <span className="text-sm font-bold">
                  {user?.name.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Welcome Section */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold mb-2" style={{ color: '#0047AB' }}>
                Welcome back, {user?.name}!
              </h1>
              <p className="text-gray-600 text-lg">
                {company ? `Managing ${company.name}` : 'Personal Account'}
              </p>
            </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              </div>
            </div>
            <div className="text-3xl font-bold" style={{ color: '#0047AB' }}>
              {loading ? '...' : stats.assetsCount}
            </div>
            <div className="text-sm text-gray-600 mt-1">Assets Monitored</div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="text-3xl font-bold text-green-600">
              {loading ? '...' : stats.scansToday}
            </div>
            <div className="text-sm text-gray-600 mt-1">Scans Today</div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <div className="text-3xl font-bold text-amber-600">
              {loading ? '...' : stats.issuesFound}
            </div>
            <div className="text-sm text-gray-600 mt-1">Issues Found</div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
            </div>
            <div className="text-3xl font-bold text-indigo-600">
              {loading ? '...' : stats.teamMembers}
            </div>
            <div className="text-sm text-gray-600 mt-1">Team Members</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold mb-6" style={{ color: '#0047AB' }}>Quick Actions</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <a
              href="/dashboard/assets"
              className="flex items-center gap-4 p-6 rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all group"
            >
              <div className="w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-gray-900">Add Asset</div>
                <div className="text-sm text-gray-600">Monitor a new domain or app</div>
              </div>
            </a>

            <a
              href="/dashboard/assets"
              className="flex items-center gap-4 p-6 rounded-xl border-2 border-gray-200 hover:border-green-500 hover:shadow-lg transition-all group"
            >
              <div className="w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-gray-900">Run Check</div>
                <div className="text-sm text-gray-600">Scan your assets now</div>
              </div>
            </a>

            <a
              href="/dashboard/reports"
              className="flex items-center gap-4 p-6 rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all group"
            >
              <div className="w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{ background: 'linear-gradient(135deg, #DAA520 0%, #FFD700 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-gray-900">View Reports</div>
                <div className="text-sm text-gray-600">Security & compliance</div>
              </div>
            </a>

            <a
              href="/services/company-verification"
              className="flex items-center gap-4 p-6 rounded-xl border-2 border-gray-200 hover:border-green-500 hover:shadow-lg transition-all group"
            >
              <div className="w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{ background: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-gray-900">Company Verification</div>
                <div className="text-sm text-gray-600">Due diligence reports</div>
              </div>
            </a>
          </div>
        </div>

        {/* Your Assets Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold" style={{ color: '#0047AB' }}>Your Assets</h2>
              <a
                href="/dashboard/assets"
                className="text-sm font-semibold hover:underline"
                style={{ color: '#0047AB' }}
              >
                View All →
              </a>
            </div>

            {assets.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📦</div>
                <p className="text-gray-600 text-lg mb-2">No assets added yet</p>
                <p className="text-gray-500 text-sm mb-6">
                  Click "+ Add Asset" or "📱 Add Mobile App" above to get started
                </p>
                <div className="flex gap-3 justify-center">
                  <a
                    href="/dashboard/assets"
                    className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
                    style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                  >
                    Add Your First Asset
                  </a>
                </div>
              </div>
            ) : (
              <>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {assets.slice(0, 6).map((asset: any) => (
                <div
                  key={asset.id}
                  className="border-2 border-gray-200 rounded-xl p-4 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
                  onClick={() => router.push('/dashboard/assets')}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {(asset.type?.toLowerCase() === 'mobile_app' || asset.type?.toUpperCase() === 'MOBILE_APP') ? (
                          <span className="text-xl">📱</span>
                        ) : (
                          <span className="text-xl">🌐</span>
                        )}
                        <h3 className="font-bold text-gray-900 truncate">{asset.name}</h3>
                      </div>
                      <p className="text-xs text-gray-500 truncate">{asset.value}</p>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      asset.verification_status === 'VERIFIED'
                        ? 'bg-green-100 text-green-700'
                        : asset.verification_status === 'FAILED'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {asset.verification_status?.toLowerCase() || 'pending'}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div className="flex items-center gap-3">
                      <div>
                        <div className="text-xs text-gray-500">Score</div>
                        <div className={`text-lg font-bold ${
                          (asset.security_score || 0) >= 80 ? 'text-green-600' :
                          (asset.security_score || 0) >= 60 ? 'text-yellow-600' :
                          (asset.security_score || 0) >= 40 ? 'text-orange-600' : 'text-red-600'
                        }`}>
                          {asset.security_score !== null && asset.security_score !== undefined ? asset.security_score : '—'}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Issues</div>
                        <div className="text-lg font-bold text-amber-600">
                          {asset.findings_count || 0}
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-400">
                      {asset.last_scanned_at ? (
                        <span>Scanned {new Date(asset.last_scanned_at).toLocaleDateString()}</span>
                      ) : (
                        <span>Not scanned yet</span>
                      )}
                    </div>
                  </div>
                </div>
                  ))}
                </div>

                {assets.length > 6 && (
                  <div className="text-center mt-6">
                    <a
                      href="/dashboard/assets"
                      className="inline-block px-6 py-3 rounded-xl font-semibold text-white shadow-lg hover:opacity-90 transition-opacity"
                      style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                    >
                      View All {assets.length} Assets →
                    </a>
                  </div>
                )}
              </>
            )}
          </div>

            {/* Account Info */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-6" style={{ color: '#0047AB' }}>Account Information</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-700 mb-4">User Details</h3>
              <div className="space-y-3">
                <div>
                  <div className="text-sm text-gray-600">Name</div>
                  <div className="font-semibold">{user?.name}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Email</div>
                  <div className="font-semibold">{user?.email}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Role</div>
                  <div className="font-semibold capitalize">{user?.role.replace('_', ' ')}</div>
                </div>
              </div>
            </div>

            {company && (
              <div>
                <h3 className="font-semibold text-gray-700 mb-4">Company Details</h3>
                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-600">Company Name</div>
                    <div className="font-semibold">{company.name}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Country</div>
                    <div className="font-semibold">{company.country}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Plan</div>
                    <div className="font-semibold capitalize">{company.plan}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-6">
              {/* Quick Links */}
              <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-gray-100">
                <h3 className="font-bold text-gray-900 mb-4">Services</h3>
                <div className="space-y-2">
                  <a href="/services/company-verification" className="block px-4 py-2 rounded-lg hover:bg-blue-50 transition text-sm font-medium text-gray-700 hover:text-blue-700">
                    🏢 Company Verification
                  </a>
                  <a href="/business" className="block px-4 py-2 rounded-lg hover:bg-blue-50 transition text-sm font-medium text-gray-700 hover:text-blue-700">
                    💼 All Services
                  </a>
                  <a href="/pricing" className="block px-4 py-2 rounded-lg hover:bg-blue-50 transition text-sm font-medium text-gray-700 hover:text-blue-700">
                    💰 Pricing Plans
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
