'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { getIndustry, riskTierLabel, industryAdjustedScore, IndustryConfig } from '@/lib/industries';
import { config } from '@/lib/config';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

interface DashboardStats {
  assetsCount: number;
  scansToday: number;
  issuesFound: number;
  criticalAlerts: number;
}

const NAV = [
  { label: 'Overview', href: '/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { label: 'Assets', href: '/dashboard/assets', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
  { label: 'Scans & Findings', href: '/scans', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  { label: 'Reports', href: '/dashboard/reports', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { label: 'Alerts', href: '/dashboard/alerts', icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
  { label: 'Team', href: '/dashboard/team', icon: 'M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-9a4 4 0 11-8 0 4 4 0 018 0zm6 3a3 3 0 11-6 0 3 3 0 016 0z' },
  { label: 'Billing', href: '/dashboard/billing', icon: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z' },
];

function riskLabel(score: number) {
  if (score >= 80) return { label: 'Low Risk', color: '#10B981' };
  if (score >= 60) return { label: 'Medium Risk', color: GOLD };
  if (score >= 40) return { label: 'High Risk', color: '#F97316' };
  return { label: 'Critical Risk', color: '#EF4444' };
}

export default function DashboardPage() {
  const { user, company, token, logout } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>({
    assetsCount: 0,
    scansToday: 0,
    issuesFound: 0,
    criticalAlerts: 0,
  });
  const [securityScore, setSecurityScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [assets, setAssets] = useState<any[]>([]);
  const [showMultiScanModal, setShowMultiScanModal] = useState(false);
  const [scanningAssets, setScanningAssets] = useState<Map<string, {name: string, progress: number, status: string, phase: string}>>(new Map());

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        // Use token from auth context
        if (!token) {
          setLoading(false);
          return;
        }

        const assetsRes = await fetch(`${config.apiUrl}/api/assets`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (assetsRes.ok) {
          const assetsData = await assetsRes.json();
          const list = Array.isArray(assetsData) ? assetsData : [];
          setAssets(list);

          const assetCount = list.length;
          const totalIssues = list.reduce((sum: number, a: any) => sum + (a.findings_count || 0), 0);

          const today = new Date().toDateString();
          const scansToday = list.filter((a: any) => {
            const ts = a.last_scan_at || a.last_scanned_at;
            if (!ts) return false;
            return new Date(ts).toDateString() === today;
          }).length;

          // Average security score across scored assets
          const scored = list.filter((a: any) => a.security_score !== null && a.security_score !== undefined);
          const avg = scored.length
            ? Math.round(scored.reduce((s: number, a: any) => s + a.security_score, 0) / scored.length)
            : null;
          setSecurityScore(avg);

          // Critical alerts = assets scoring below 40
          const critical = list.filter((a: any) => (a.security_score ?? 100) < 40).length;

          setStats({
            assetsCount: assetCount,
            scansToday,
            issuesFound: totalIssues,
            criticalAlerts: critical,
          });

          // 🔥 AUTO-TRIGGER SCARY SCANNING ANIMATION on first load
          if (list.length > 0 && !sessionStorage.getItem('dashboard_scanned')) {
            sessionStorage.setItem('dashboard_scanned', 'true');
            // Trigger scan with the loaded assets list
            setTimeout(() => {
              triggerAutoScan(list);
            }, 1000);
          }
        }
      } catch (error: any) {
        console.error('Error fetching dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    // Run when token is available
    if (token) {
      fetchDashboardStats();
    }
  }, [token]); // Re-run when token changes

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const triggerAutoScan = async (assetsList: any[]) => {
    if (assetsList.length === 0) {
      return;
    }

    setShowMultiScanModal(true);
    const newScanningAssets = new Map();

    // Initialize all assets
    assetsList.forEach(asset => {
      newScanningAssets.set(asset.id, {
        name: asset.name,
        progress: 0,
        status: 'pending',
        phase: 'Queued...'
      });
    });
    setScanningAssets(new Map(newScanningAssets));

    // Scan each asset
    for (const asset of assetsList) {
      try {
        // Update to starting
        newScanningAssets.set(asset.id, {
          ...newScanningAssets.get(asset.id)!,
          status: 'scanning',
          phase: 'Initializing deep security scan...'
        });
        setScanningAssets(new Map(newScanningAssets));

        // Simulate scanning phases
        const phases = [
          'Initializing deep security scan...',
          'Analyzing SSL/TLS encryption...',
          'Checking security headers...',
          'Scanning for vulnerabilities...',
          'Detecting technology stack...',
          'Testing DNS security...',
          'Probing for exposed services...',
          'Analyzing threat vectors...',
          'Generating risk assessment...',
          'Finalizing report...'
        ];

        let phaseIndex = 0;
        const phaseInterval = setInterval(() => {
          if (phaseIndex < phases.length) {
            newScanningAssets.set(asset.id, {
              ...newScanningAssets.get(asset.id)!,
              phase: phases[phaseIndex],
              progress: Math.min(95, (phaseIndex + 1) * 10)
            });
            setScanningAssets(new Map(newScanningAssets));
            phaseIndex++;
          }
        }, 1000);

        const res = await fetch(`${config.apiUrl}/api/scans/assets/${asset.id}/scan`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });

        clearInterval(phaseInterval);

        if (res.ok) {
          const data = await res.json();
          newScanningAssets.set(asset.id, {
            ...newScanningAssets.get(asset.id)!,
            status: 'complete',
            phase: `✅ Complete! Score: ${data.score || 'N/A'}/100`,
            progress: 100
          });
        } else {
          const errorData = await res.json().catch(() => ({ detail: 'Unknown error' }));
          newScanningAssets.set(asset.id, {
            ...newScanningAssets.get(asset.id)!,
            status: 'failed',
            phase: `❌ Failed: ${errorData.detail || 'Error'}`,
            progress: 100
          });
        }
      } catch (err: any) {
        newScanningAssets.set(asset.id, {
          ...newScanningAssets.get(asset.id)!,
          status: 'failed',
          phase: `❌ Network error: ${err.message || 'Connection failed'}`,
          progress: 100
        });
      }
      setScanningAssets(new Map(newScanningAssets));
    }

    // Refresh dashboard after all scans complete
    setTimeout(() => {
      if (token) {
        window.location.reload();
      }
    }, 3000);
  };

  const handleScanAllAssets = async () => {
    if (assets.length === 0) {
      alert('No assets to scan');
      return;
    }

    triggerAutoScan(assets);
  };

  const score = securityScore ?? 0;
  const risk = riskLabel(score);
  const circumference = 2 * Math.PI * 52;
  const dashOffset = circumference - (score / 100) * circumference;

  const industry = getIndustry(company?.industry);
  const tier = riskTierLabel(industry.riskTier);
  const adjustedScore = securityScore === null ? null : industryAdjustedScore(industry, score);

  return (
    <main className="min-h-screen cyber-bg">
      {/* Top Navigation */}
      <nav className="border-b border-cyber bg-[#050B1A]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <a href="/dashboard" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-sm text-white">{company ? company.name : user?.name}</div>
                <div className="text-xs text-cyber-muted capitalize">{company ? `${company.plan} Plan` : user?.role}</div>
              </div>
            </a>

            <div className="flex items-center gap-4">
              <button onClick={handleLogout} className="px-4 py-2 text-sm font-semibold text-cyber-muted hover:text-red-400 transition-colors">
                Logout
              </button>
              <div className="w-10 h-10 rounded-full flex items-center justify-center text-white" style={{ background: BLUE }}>
                <span className="text-sm font-bold">{user?.name?.charAt(0).toUpperCase()}</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-[230px_1fr] gap-8">
          {/* Sidebar Nav */}
          <aside className="hidden lg:block">
            <div className="cyber-card p-3 sticky top-24">
              <nav className="space-y-1">
                {NAV.map((item) => (
                  <a
                    key={item.label}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      item.label === 'Overview' ? 'text-white bg-white/5' : 'text-cyber-muted hover:text-white hover:bg-white/5'
                    }`}
                    style={item.label === 'Overview' ? { borderLeft: `3px solid ${GOLD}` } : { borderLeft: '3px solid transparent' }}
                  >
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                    </svg>
                    {item.label}
                  </a>
                ))}
              </nav>
            </div>
          </aside>

          {/* Main */}
          <div>
            <div className="mb-8">
              <div className="flex flex-wrap items-center gap-3 mb-1">
                <h1 className="text-3xl font-bold text-white">Security Overview</h1>
                {company && (
                  <span
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold text-white"
                    style={{ background: BLUE }}
                    title={tier.label}
                  >
                    <span>{industry.icon}</span>
                    {industry.label}
                  </span>
                )}
              </div>
              <p className="text-cyber-muted">{company ? `Monitoring ${company.name}` : `Welcome back, ${user?.name}`}</p>
            </div>

            {/* Hero: Security Score + Stats */}
            <div className="grid lg:grid-cols-3 gap-6 mb-8">
              {/* Score gauge */}
              <div className="cyber-card-raised p-6 flex flex-col items-center justify-center cyber-glow-blue">
                <div className="relative w-36 h-36">
                  <svg className="w-36 h-36 -rotate-90" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="52" fill="none" stroke="#1B2C4F" strokeWidth="10" />
                    <circle
                      cx="60" cy="60" r="52" fill="none"
                      stroke={risk.color} strokeWidth="10" strokeLinecap="round"
                      strokeDasharray={circumference}
                      strokeDashoffset={loading ? circumference : dashOffset}
                      style={{ transition: 'stroke-dashoffset 1s ease' }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl font-bold text-white">{loading ? '—' : securityScore ?? '—'}</span>
                    <span className="text-xs text-cyber-muted">/ 100</span>
                  </div>
                </div>
                <div className="mt-4 text-center">
                  <div className="text-sm text-cyber-muted">Security Score</div>
                  <div className="font-bold mt-1" style={{ color: risk.color }}>
                    {securityScore === null ? 'No scans yet' : risk.label}
                  </div>
                </div>
              </div>

              {/* Stat tiles */}
              <div className="lg:col-span-2 grid grid-cols-2 gap-6">
                <StatCard label="Assets Monitored" value={loading ? '...' : stats.assetsCount} color={BLUE} icon="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2" />
                <StatCard label="Scans Today" value={loading ? '...' : stats.scansToday} color="#10B981" icon="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                <StatCard label="Open Findings" value={loading ? '...' : stats.issuesFound} color={GOLD} icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                <StatCard label="Critical Alerts" value={loading ? '...' : stats.criticalAlerts} color="#EF4444" icon="M13 10V3L4 14h7v7l9-11h-7z" />
              </div>
            </div>


            {/* Risk trend (illustrative) */}
            <div className="cyber-card-raised p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-white">Risk Trend (30 days)</h2>
                <span className="text-xs text-cyber-muted">Average security score across assets</span>
              </div>
              <RiskTrend baseScore={securityScore ?? 0} hasData={securityScore !== null} />
            </div>

            {/* Industry-specific compliance & focus */}
            {company && (
              <IndustryCompliance
                industry={industry}
                tier={tier}
                securityScore={securityScore}
                adjustedScore={adjustedScore}
              />
            )}

            {/* Industry best practices */}
            {company && <IndustryBestPractices industry={industry} />}

            {/* Monitored Assets */}
            <div className="cyber-card-raised p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-white">Monitored Assets</h2>
                <a href="/dashboard/assets" className="text-sm font-semibold hover:underline" style={{ color: GOLD }}>
                  Manage assets →
                </a>
              </div>

              {assets.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-cyber-muted text-lg mb-2">No assets monitored yet</p>
                  <p className="text-cyber-muted text-sm mb-6">Add and verify a domain, API or app to begin deep scanning.</p>
                  <a href="/dashboard/assets" className="inline-block px-6 py-3 rounded-xl font-semibold text-white shadow-lg" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}>
                    Add Your First Asset
                  </a>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {assets.slice(0, 6).map((asset: any) => {
                    const verified = String(asset.verification_status).toUpperCase() === 'VERIFIED';
                    const failed = String(asset.verification_status).toUpperCase() === 'FAILED';
                    const sc = asset.security_score;
                    const scColor = sc == null ? '#8FA3C4' : sc >= 80 ? '#10B981' : sc >= 60 ? GOLD : sc >= 40 ? '#F97316' : '#EF4444';
                    return (
                      <div
                        key={asset.id}
                        className="cyber-card p-4 hover:cyber-glow-blue transition-all cursor-pointer"
                        onClick={() => router.push('/dashboard/assets')}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1 min-w-0">
                            <h3 className="font-bold text-white truncate">{asset.name}</h3>
                            <p className="text-xs text-cyber-muted truncate">{asset.value}</p>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-[10px] font-bold flex items-center gap-1 ${
                            verified ? 'bg-green-500/15 text-green-400' : failed ? 'bg-red-500/15 text-red-400' : 'bg-yellow-500/15 text-yellow-400'
                          }`}>
                            {verified && (
                              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                            )}
                            {verified ? 'VERIFIED' : failed ? 'FAILED' : 'PENDING'}
                          </span>
                        </div>
                        <div className="flex items-center justify-between pt-3 border-t border-cyber">
                          <div className="flex items-center gap-4">
                            <div>
                              <div className="text-[10px] text-cyber-muted uppercase">Score</div>
                              <div className="text-lg font-bold" style={{ color: scColor }}>{sc ?? '—'}</div>
                            </div>
                            <div>
                              <div className="text-[10px] text-cyber-muted uppercase">Findings</div>
                              <div className="text-lg font-bold" style={{ color: GOLD }}>{asset.findings_count || 0}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Account info */}
            <div className="cyber-card-raised p-6">
              <h2 className="text-lg font-bold text-white mb-6">Account Information</h2>
              <div className="grid md:grid-cols-2 gap-6 text-sm">
                <div>
                  <h3 className="font-semibold text-cyber-muted mb-3 uppercase text-xs tracking-wider">User Details</h3>
                  <div className="space-y-3">
                    <Field label="Name" value={user?.name} />
                    <Field label="Email" value={user?.email} />
                    <Field label="Role" value={user?.role?.replace('_', ' ')} />
                  </div>
                </div>
                {company && (
                  <div>
                    <h3 className="font-semibold text-cyber-muted mb-3 uppercase text-xs tracking-wider">Company Details</h3>
                    <div className="space-y-3">
                      <Field label="Company Name" value={company.name} />
                      <Field label="Country" value={company.country} />
                      <Field label="Industry" value={`${industry.icon} ${industry.label}`} />
                      <Field label="Plan" value={company.plan} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* 🔥 MULTI-ASSET SCANNING MODAL */}
      {showMultiScanModal && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div className="relative max-w-4xl w-full max-h-[90vh] overflow-hidden">
            {/* Animated glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 via-orange-500/20 to-yellow-500/20 rounded-3xl blur-2xl animate-pulse" />

            {/* Main modal */}
            <div className="relative cyber-card-raised p-8 max-h-[90vh] overflow-y-auto">
              {/* Background matrix effect */}
              <div className="absolute inset-0 opacity-10">
                <div className="absolute inset-0 bg-gradient-to-b from-red-500/20 to-transparent animate-pulse" />
              </div>

              <div className="relative z-10">
                {/* Header */}
                <div className="text-center mb-8">
                  <div className="relative inline-block">
                    <div className="w-24 h-24 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                      <svg className="w-16 h-16 text-red-500 animate-spin-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    {/* Scanning rings */}
                    <div className="absolute inset-0 border-4 border-red-500/30 rounded-full animate-ping" />
                    <div className="absolute inset-0 border-2 border-yellow-500/40 rounded-full animate-pulse" style={{ animationDelay: '0.5s' }} />
                  </div>

                  <h3 className="text-3xl font-bold text-white mb-2 animate-pulse">
                    🔴 DEEP SECURITY SCAN IN PROGRESS
                  </h3>
                  <p className="text-lg text-red-400 font-semibold">Scanning {scanningAssets.size} Assets Simultaneously</p>
                </div>

                {/* Asset scan progress list */}
                <div className="space-y-4 mb-6">
                  {Array.from(scanningAssets.entries()).map(([assetId, asset]) => (
                    <div key={assetId} className="bg-black/40 rounded-xl p-4 border border-red-500/20">
                      <div className="flex items-start gap-3 mb-3">
                        {/* Status icon */}
                        <div className="flex-shrink-0 mt-1">
                          {asset.status === 'pending' && (
                            <div className="w-6 h-6 bg-gray-500/20 rounded-full flex items-center justify-center">
                              <span className="text-sm">⏳</span>
                            </div>
                          )}
                          {asset.status === 'scanning' && (
                            <svg className="animate-spin h-6 w-6 text-red-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                          )}
                          {asset.status === 'complete' && <span className="text-2xl">✅</span>}
                          {asset.status === 'failed' && <span className="text-2xl">❌</span>}
                        </div>

                        {/* Asset info */}
                        <div className="flex-1">
                          <div className="text-white font-semibold mb-1">{asset.name}</div>
                          <div className="text-sm text-cyber-muted font-mono animate-pulse">
                            {asset.phase}
                          </div>
                        </div>

                        {/* Progress percentage */}
                        <div className="text-right">
                          <div className="text-white font-bold text-lg">{asset.progress}%</div>
                        </div>
                      </div>

                      {/* Progress bar */}
                      <div className="relative h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className={`absolute inset-y-0 left-0 transition-all duration-500 ease-out ${
                            asset.status === 'complete' ? 'bg-gradient-to-r from-green-600 via-green-500 to-emerald-500' :
                            asset.status === 'failed' ? 'bg-gradient-to-r from-red-600 via-red-500 to-orange-500' :
                            'bg-gradient-to-r from-red-600 via-orange-500 to-yellow-500'
                          }`}
                          style={{ width: `${asset.progress}%` }}
                        >
                          <div className="absolute inset-0 bg-white/20 animate-pulse" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Summary stats */}
                <div className="grid grid-cols-3 gap-3 mb-6">
                  <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 text-center">
                    <div className="text-blue-500 font-bold text-xl">{Array.from(scanningAssets.values()).filter(a => a.status === 'scanning').length}</div>
                    <div className="text-xs text-blue-400 mt-1">Scanning</div>
                  </div>
                  <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 text-center">
                    <div className="text-green-500 font-bold text-xl">{Array.from(scanningAssets.values()).filter(a => a.status === 'complete').length}</div>
                    <div className="text-xs text-green-400 mt-1">Complete</div>
                  </div>
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-center">
                    <div className="text-red-500 font-bold text-xl">{Array.from(scanningAssets.values()).filter(a => a.status === 'failed').length}</div>
                    <div className="text-xs text-red-400 mt-1">Failed</div>
                  </div>
                </div>

                {/* Close button (only show when all scans are done) */}
                {Array.from(scanningAssets.values()).every(a => a.status === 'complete' || a.status === 'failed') && (
                  <div className="text-center">
                    <button
                      onClick={() => setShowMultiScanModal(false)}
                      className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-semibold transition-all"
                    >
                      Close & View Results
                    </button>
                  </div>
                )}

                {/* Footer note */}
                <div className="text-center mt-4">
                  <p className="text-xs text-cyber-muted">
                    🔒 Deep security analysis in progress...
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

function StatCard({ label, value, color, icon }: { label: string; value: any; color: string; icon: string }) {
  return (
    <div className="cyber-card p-5">
      <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-4" style={{ background: `${color}22` }}>
        <svg className="w-5 h-5" style={{ color }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
        </svg>
      </div>
      <div className="text-3xl font-bold text-white">{value}</div>
      <div className="text-sm text-cyber-muted mt-1">{label}</div>
    </div>
  );
}

function IndustryCompliance({
  industry,
  tier,
  securityScore,
  adjustedScore,
}: {
  industry: IndustryConfig;
  tier: { label: string; color: string };
  securityScore: number | null;
  adjustedScore: number | null;
}) {
  // A focus area is considered "needs attention" when the industry-adjusted
  // score is low; we colour the indicators accordingly.
  const status = (i: number): { color: string; label: string } => {
    if (adjustedScore === null) return { color: '#8FA3C4', label: 'No data' };
    // Stagger thresholds so areas light up progressively as score improves.
    const threshold = 50 + i * 8;
    if (adjustedScore >= threshold + 15) return { color: '#10B981', label: 'Compliant' };
    if (adjustedScore >= threshold) return { color: GOLD, label: 'Review' };
    return { color: '#EF4444', label: 'Needs attention' };
  };

  return (
    <div className="cyber-card-raised p-6 mb-8 cyber-glow-blue">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{industry.icon}</span>
          <div>
            <h2 className="text-lg font-bold text-white">{industry.label} · Compliance Focus</h2>
            <span className="text-xs font-semibold" style={{ color: tier.color }}>{tier.label}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-[10px] uppercase tracking-wider text-cyber-muted">Industry-Adjusted Score</div>
          <div className="text-2xl font-bold" style={{ color: tier.color }}>
            {adjustedScore === null ? '—' : adjustedScore}
            <span className="text-sm text-cyber-muted">/100</span>
          </div>
        </div>
      </div>

      {/* Compliance badges */}
      <div className="flex flex-wrap gap-2 mb-6">
        {industry.compliance.map((c) => (
          <span
            key={c.label}
            title={c.full}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border"
            style={{ borderColor: GOLD, color: GOLD }}
          >
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
            {c.label}
          </span>
        ))}
        {securityScore === null && (
          <span className="text-xs text-cyber-muted self-center">Run a scan to assess compliance posture.</span>
        )}
      </div>

      {/* Focus areas */}
      <div className="grid sm:grid-cols-2 gap-4">
        {industry.focusAreas.map((f, i) => {
          const s = status(i);
          return (
            <div key={f.label} className="cyber-card p-4 flex items-start gap-3">
              <span className="mt-1 w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: s.color }} />
              <div className="min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="font-semibold text-white text-sm truncate">{f.label}</h3>
                  <span className="text-[10px] font-bold flex-shrink-0" style={{ color: s.color }}>{s.label}</span>
                </div>
                <p className="text-xs text-cyber-muted mt-0.5">{f.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function IndustryBestPractices({ industry }: { industry: IndustryConfig }) {
  return (
    <div className="cyber-card-raised p-6 mb-8 border-l-4" style={{ borderColor: GOLD }}>
      <div className="flex items-center gap-2 mb-4">
        <svg className="w-5 h-5" style={{ color: GOLD }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <h2 className="text-lg font-bold text-white">Industry Best Practices</h2>
        <span className="text-xs text-cyber-muted">· {industry.label}</span>
      </div>
      <ul className="space-y-3">
        {industry.recommendations.map((r) => (
          <li key={r} className="flex items-start gap-3 text-sm text-cyber-muted">
            <span className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold" style={{ background: `${GOLD}22`, color: GOLD }}>✓</span>
            <span>{r}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Field({ label, value }: { label: string; value?: string }) {
  return (
    <div>
      <div className="text-cyber-muted text-xs">{label}</div>
      <div className="font-semibold text-white capitalize">{value || '—'}</div>
    </div>
  );
}

function RiskTrend({ baseScore, hasData }: { baseScore: number; hasData: boolean }) {
  // Illustrative trend converging to the current average score.
  const points = 12;
  const data = Array.from({ length: points }, (_, i) => {
    if (!hasData) return 0;
    const t = i / (points - 1);
    const start = Math.max(0, baseScore - 18);
    const wobble = Math.sin(i * 1.3) * 4;
    return Math.max(0, Math.min(100, Math.round(start + (baseScore - start) * t + wobble)));
  });

  const w = 720;
  const h = 140;
  const stepX = w / (points - 1);
  const toY = (v: number) => h - (v / 100) * h;
  const linePath = data.map((v, i) => `${i === 0 ? 'M' : 'L'} ${i * stepX} ${toY(v)}`).join(' ');
  const areaPath = `${linePath} L ${w} ${h} L 0 ${h} Z`;

  if (!hasData) {
    return <div className="h-[140px] flex items-center justify-center text-cyber-muted text-sm">Run a scan to start building your risk trend.</div>;
  }

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-[140px]" preserveAspectRatio="none">
      <defs>
        <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1E90FF" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#1E90FF" stopOpacity="0" />
        </linearGradient>
      </defs>
      {[0, 0.5, 1].map((g) => (
        <line key={g} x1="0" x2={w} y1={h * g} y2={h * g} stroke="#1B2C4F" strokeWidth="1" />
      ))}
      <path d={areaPath} fill="url(#trendFill)" />
      <path d={linePath} fill="none" stroke="#1E90FF" strokeWidth="2.5" />
      {data.map((v, i) => (
        <circle key={i} cx={i * stepX} cy={toY(v)} r="3" fill={GOLD} />
      ))}
    </svg>
  );
}
