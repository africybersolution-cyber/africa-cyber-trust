'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { config } from '@/lib/config';
import DashboardLayout from '@/components/DashboardLayout';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

interface AIRiskAnalysis {
  overall_risk_score: number;
  risk_level: string;
  executive_summary: string;
  top_3_priorities: any[];
  quick_wins: any[];
  remediation_phases: number;
}

interface ScanData {
  id: string;
  asset_id: string;
  asset_name: string;
  asset_value: string;
  status: string;
  score: number;
  started_at: string;
  completed_at: string | null;
  findings_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  scan_data?: {
    ai_risk_analysis?: AIRiskAnalysis;
  };
}

interface Finding {
  id: string;
  title: string;
  severity: string;
  description: string;
  recommendation: string;
}

export default function ScansPage() {
  const { token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scans, setScans] = useState<ScanData[]>([]);
  const [selectedScan, setSelectedScan] = useState<ScanData | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loadingFindings, setLoadingFindings] = useState(false);

  useEffect(() => {
    // Wait for the auth context to finish hydrating from localStorage before
    // making any auth decision. Without this guard, `token` is null on the very
    // first render (the context loads it in its own effect), which caused an
    // immediate, spurious redirect to /login on first navigation here.
    if (authLoading) return;

    if (!token) {
      router.replace('/login');
      return;
    }

    let cancelled = false;

    const fetchAllScans = async () => {
      setLoading(true);
      setError(null);
      try {
        const assetsRes = await fetch(`${config.apiUrl}/api/assets`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (assetsRes.status === 401) {
          // Token expired/invalid — send the user to re-authenticate.
          router.replace('/login');
          return;
        }

        if (!assetsRes.ok) throw new Error('Failed to fetch assets');

        const assets = await assetsRes.json();
        const allScans: ScanData[] = [];

        for (const asset of assets) {
          try {
            const scansRes = await fetch(
              `${config.apiUrl}/api/scans/assets/${asset.id}/scans`,
              { headers: { Authorization: `Bearer ${token}` } }
            );

            if (scansRes.ok) {
              const assetScans = await scansRes.json();
              const scansWithAssetInfo = assetScans.map((scan: any) => ({
                ...scan,
                asset_name: asset.name,
                asset_value: asset.value
              }));
              allScans.push(...scansWithAssetInfo);
            }
          } catch (err) {
            console.error(`Error fetching scans for ${asset.name}:`, err);
          }
        }

        // Hide failed scans. Keep the most recent scan per asset (even if it
        // failed) so a brand-new failure is still visible, but drop older
        // failed/cancelled scans that would otherwise clutter the list.
        // Mirrors the filtering used on the Assets page report view.
        const latestPerAsset = new Map<string, string>();
        for (const scan of allScans) {
          const key = scan.asset_id;
          const prev = latestPerAsset.get(key);
          if (!prev || new Date(scan.started_at).getTime() > new Date(prev).getTime()) {
            latestPerAsset.set(key, scan.started_at);
          }
        }

        const isFailed = (s: string) => {
          const v = (s || '').toLowerCase();
          return v === 'failed' || v === 'error' || v === 'cancelled' || v === 'canceled';
        };

        const visibleScans = allScans.filter((scan) => {
          if (!isFailed(scan.status)) return true;
          // Only keep a failed scan if it is the latest scan for its asset.
          return latestPerAsset.get(scan.asset_id) === scan.started_at;
        });

        visibleScans.sort((a, b) =>
          new Date(b.started_at).getTime() - new Date(a.started_at).getTime()
        );

        if (!cancelled) setScans(visibleScans);
      } catch (error) {
        console.error('Error fetching scans:', error);
        if (!cancelled) setError('Could not load scans. Please try again.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchAllScans();

    return () => {
      cancelled = true;
    };
  }, [token, authLoading, router]);

  const loadFindings = async (scan: ScanData) => {
    setSelectedScan(scan);
    setLoadingFindings(true);

    try {
      const res = await fetch(
        `${config.apiUrl}/api/scans/assets/${scan.asset_id}/findings`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (res.ok) {
        const data = await res.json();
        setFindings(data);
      }
    } catch (error) {
      console.error('Error fetching findings:', error);
    } finally {
      setLoadingFindings(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10B981';
    if (score >= 60) return GOLD;
    if (score >= 40) return '#F97316';
    return '#EF4444';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return '#DC2626';
      case 'high': return '#F97316';
      case 'medium': return '#EAB308';
      case 'low': return '#3B82F6';
      default: return '#6B7280';
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toUpperCase()) {
      case 'CRITICAL': return '#DC2626';
      case 'HIGH': return '#F97316';
      case 'MEDIUM': return '#EAB308';
      case 'LOW': return '#10B981';
      default: return '#6B7280';
    }
  };

  const getStatusColor = (status: string) => {
    switch ((status || '').toLowerCase()) {
      case 'completed': return { bg: 'bg-green-500/15', text: 'text-green-400' };
      case 'running': return { bg: 'bg-blue-500/15', text: 'text-blue-400' };
      case 'failed':
      case 'error':
      case 'cancelled':
      case 'canceled': return { bg: 'bg-red-500/15', text: 'text-red-400' };
      default: return { bg: 'bg-yellow-500/15', text: 'text-yellow-400' };
    }
  };

  if (authLoading || loading) {
    return (
      <DashboardLayout title="Scans & Findings" subtitle="View security scan results">
        <div className="text-center py-20">
          <div className="w-16 h-16 border-4 border-t-blue-500 border-[#1B2C4F] rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-cyber-muted text-lg">Loading scans...</div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout title="Scans & Findings" subtitle="View security scan results">
        <div className="cyber-card-raised p-12 text-center max-w-xl mx-auto">
          <div className="text-5xl mb-4">⚠️</div>
          <h3 className="text-xl font-bold text-white mb-2">Couldn&apos;t load scans</h3>
          <p className="text-cyber-muted mb-6">{error}</p>
          <button
            onClick={() => router.refresh()}
            className="inline-block px-6 py-3 rounded-xl font-semibold text-white transition-opacity hover:opacity-90"
            style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
          >
            Retry
          </button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Scans & Findings" subtitle="View security scan results and vulnerability findings">
      {scans.length === 0 ? (
        <div className="cyber-card-raised p-12 text-center">
          <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4" style={{ background: `${BLUE}20` }}>
            <svg className="w-10 h-10" style={{ color: BLUE }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No Scans Yet</h3>
          <p className="text-cyber-muted mb-6">Add assets and run scans to see results here</p>
          <a
            href="/dashboard/assets"
            className="inline-block px-6 py-3 rounded-xl font-semibold text-white transition-opacity hover:opacity-90"
            style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
          >
            Go to Assets
          </a>
        </div>
      ) : (
        <div className="space-y-6">
          {scans.map((scan) => (
            <div
              key={scan.id}
              className="cyber-card-raised p-6 hover:cyber-glow-blue transition-all cursor-pointer"
              onClick={() => loadFindings(scan)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-1">{scan.asset_name}</h3>
                  <p className="text-sm text-cyber-muted">{scan.asset_value}</p>
                </div>
                <div className="text-right">
                  <div
                    className="text-3xl font-bold mb-1"
                    style={{ color: getScoreColor(scan.score) }}
                  >
                    {scan.score != null ? `${scan.score}/100` : '—'}
                  </div>
                  <div className="flex items-center justify-end gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold capitalize ${getStatusColor(scan.status).bg} ${getStatusColor(scan.status).text}`}>
                      {scan.status}
                    </span>
                    <span className="text-xs text-cyber-muted">{formatDate(scan.started_at)}</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-red-500/10 rounded-lg p-3 border border-red-500/30">
                  <div className="text-2xl font-bold text-red-400">{scan.critical_count}</div>
                  <div className="text-xs text-cyber-muted">Critical</div>
                </div>
                <div className="bg-orange-500/10 rounded-lg p-3 border border-orange-500/30">
                  <div className="text-2xl font-bold text-orange-400">{scan.high_count}</div>
                  <div className="text-xs text-cyber-muted">High</div>
                </div>
                <div className="bg-yellow-500/10 rounded-lg p-3 border border-yellow-500/30">
                  <div className="text-2xl font-bold text-yellow-400">{scan.medium_count}</div>
                  <div className="text-xs text-cyber-muted">Medium</div>
                </div>
                <div className="bg-blue-500/10 rounded-lg p-3 border border-blue-500/30">
                  <div className="text-2xl font-bold text-blue-400">{scan.low_count}</div>
                  <div className="text-xs text-cyber-muted">Low</div>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <div className="text-cyber-muted">
                  Total Findings: <span className="text-white font-semibold">{scan.findings_count}</span>
                </div>
                <div style={{ color: BLUE }} className="font-semibold hover:opacity-80">
                  View Details →
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Findings Modal */}
      {selectedScan && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setSelectedScan(null)}>
          <div className="cyber-card-raised max-w-4xl w-full max-h-[90vh] overflow-auto p-8" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">{selectedScan.asset_name}</h2>
                <p className="text-cyber-muted">{selectedScan.asset_value}</p>
              </div>
              <button
                onClick={() => setSelectedScan(null)}
                className="text-cyber-muted hover:text-white text-3xl font-light"
              >
                ×
              </button>
            </div>

            {loadingFindings ? (
              <div className="text-center py-12 text-cyber-muted">Loading findings...</div>
            ) : findings.length === 0 ? (
              <div className="text-center py-12 text-cyber-muted">No findings for this scan</div>
            ) : (
              <div className="space-y-6">
                {/* AI RISK SCORING - KILLER FEATURE */}
                {selectedScan.scan_data?.ai_risk_analysis && (
                  <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-6 border-2" style={{ borderColor: getRiskLevelColor(selectedScan.scan_data.ai_risk_analysis.risk_level) + '80' }}>
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-sm font-semibold text-cyber-muted mb-1">🤖 AI RISK ANALYSIS</h3>
                        <div className="flex items-baseline gap-3">
                          <span className="text-4xl font-bold" style={{ color: getRiskLevelColor(selectedScan.scan_data.ai_risk_analysis.risk_level) }}>
                            {selectedScan.scan_data.ai_risk_analysis.overall_risk_score}/100
                          </span>
                          <span
                            className="px-3 py-1 rounded-lg text-sm font-bold"
                            style={{
                              background: getRiskLevelColor(selectedScan.scan_data.ai_risk_analysis.risk_level) + '20',
                              color: getRiskLevelColor(selectedScan.scan_data.ai_risk_analysis.risk_level)
                            }}
                          >
                            {selectedScan.scan_data.ai_risk_analysis.risk_level} RISK
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-white">{selectedScan.scan_data.ai_risk_analysis.remediation_phases}</div>
                        <div className="text-xs text-cyber-muted">Remediation Phases</div>
                      </div>
                    </div>

                    {/* Executive Summary */}
                    <div className="bg-slate-800/50 rounded-lg p-4 mb-4">
                      <div className="text-xs font-semibold text-blue-400 mb-2">📊 EXECUTIVE SUMMARY</div>
                      <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">
                        {selectedScan.scan_data.ai_risk_analysis.executive_summary}
                      </p>
                    </div>

                    {/* Top 3 Priorities */}
                    {selectedScan.scan_data.ai_risk_analysis.top_3_priorities && selectedScan.scan_data.ai_risk_analysis.top_3_priorities.length > 0 && (
                      <div className="mb-4">
                        <div className="text-xs font-semibold text-red-400 mb-2">🎯 TOP 3 PRIORITIES</div>
                        <div className="space-y-2">
                          {selectedScan.scan_data.ai_risk_analysis.top_3_priorities.map((item: any, idx: number) => (
                            <div key={idx} className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 flex items-start gap-3">
                              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-red-500 text-white text-xs font-bold flex items-center justify-center">
                                {idx + 1}
                              </span>
                              <div className="flex-1">
                                <div className="text-sm font-semibold text-white">{item.title}</div>
                                <div className="text-xs text-red-400 mt-1">{item.priority} • Risk Score: {item.risk_score?.toFixed(1)}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Quick Wins */}
                    {selectedScan.scan_data.ai_risk_analysis.quick_wins && selectedScan.scan_data.ai_risk_analysis.quick_wins.length > 0 && (
                      <div>
                        <div className="text-xs font-semibold text-green-400 mb-2">⚡ QUICK WINS (Easy Fixes, High Impact)</div>
                        <div className="space-y-2">
                          {selectedScan.scan_data.ai_risk_analysis.quick_wins.map((item: any, idx: number) => (
                            <div key={idx} className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                              <div className="text-sm font-semibold text-white mb-1">{item.title}</div>
                              <div className="text-xs text-green-400">{item.estimated_time} • {item.impact}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* All Findings */}
                <div>
                  <h3 className="text-lg font-bold text-white mb-3">All Findings ({findings.length})</h3>
                  <div className="space-y-4">
                    {findings.map((finding) => (
                  <div
                    key={finding.id}
                    className="bg-slate-900/50 rounded-xl p-6 border"
                    style={{ borderColor: getSeverityColor(finding.severity) + '40' }}
                  >
                    <div className="flex items-start gap-4">
                      <div
                        className="px-3 py-1 rounded-lg text-xs font-bold uppercase flex-shrink-0"
                        style={{
                          background: getSeverityColor(finding.severity) + '20',
                          color: getSeverityColor(finding.severity)
                        }}
                      >
                        {finding.severity}
                      </div>
                      <div className="flex-1">
                        <h4 className="text-lg font-bold text-white mb-2">{finding.title}</h4>
                        <p className="text-cyber-muted text-sm mb-3">{finding.description}</p>
                        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                          <div className="text-xs font-semibold text-green-400 mb-1">✓ RECOMMENDATION</div>
                          <p className="text-sm text-gray-300">{finding.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                  </div>
                </div>

                {/* TWO-BUTTON CHOICE: Fix Guide or Contact for Quote */}
                <div className="mt-8 bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-8 border-2 border-blue-500/30">
                  <h3 className="text-xl font-bold text-white text-center mb-2">
                    How Would You Like to Fix These Issues?
                  </h3>
                  <p className="text-cyber-muted text-center text-sm mb-6">
                    Choose the option that works best for you
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Option 1: Fix with Guide */}
                    <div className="bg-green-500/10 border-2 border-green-500/30 rounded-xl p-6 hover:border-green-500/50 transition-all cursor-pointer">
                      <div className="text-center">
                        <div className="text-5xl mb-4">📖</div>
                        <h4 className="text-lg font-bold text-white mb-2">
                          Fix with Our Guide
                        </h4>
                        <p className="text-cyber-muted text-sm mb-4">
                          Get detailed step-by-step instructions
                        </p>
                        <ul className="text-left space-y-2 mb-4 text-sm">
                          <li className="flex items-center gap-2 text-green-400">
                            <span>✓</span>
                            <span>Specific to YOUR scan results</span>
                          </li>
                          <li className="flex items-center gap-2 text-green-400">
                            <span>✓</span>
                            <span>Code examples (copy-paste ready)</span>
                          </li>
                          <li className="flex items-center gap-2 text-green-400">
                            <span>✓</span>
                            <span>Fix at your own pace</span>
                          </li>
                        </ul>
                        <div className="text-2xl font-bold text-green-400 mb-4">
                          FREE
                        </div>
                        <div className="text-xs text-cyber-muted mb-4">
                          Recommendations shown above ↑
                        </div>
                      </div>
                    </div>

                    {/* Option 2: Professional Service */}
                    <div className="bg-blue-500/10 border-2 border-blue-500/30 rounded-xl p-6 hover:border-blue-500/50 transition-all cursor-pointer"
                         onClick={() => window.location.href = `mailto:africybersolution@gmail.com?subject=Service Request - ${selectedScan.asset_name}&body=I need help fixing ${findings.length} vulnerabilities in my ${selectedScan.asset_name}. Security Score: ${selectedScan.score}/100`}>
                      <div className="text-center">
                        <div className="text-5xl mb-4">🛠️</div>
                        <h4 className="text-lg font-bold text-white mb-2">
                          We Fix It For You
                        </h4>
                        <p className="text-cyber-muted text-sm mb-4">
                          Our security experts handle everything
                        </p>
                        <ul className="text-left space-y-2 mb-4 text-sm">
                          <li className="flex items-center gap-2" style={{ color: BLUE }}>
                            <span>✓</span>
                            <span>We do all the work</span>
                          </li>
                          <li className="flex items-center gap-2" style={{ color: BLUE }}>
                            <span>✓</span>
                            <span>Fixed in 2-4 weeks</span>
                          </li>
                          <li className="flex items-center gap-2" style={{ color: BLUE }}>
                            <span>✓</span>
                            <span>Compliance certificate included</span>
                          </li>
                        </ul>
                        <div className="text-lg font-semibold mb-4" style={{ color: BLUE }}>
                          Custom Quote
                        </div>
                        <button
                          className="w-full py-3 px-6 rounded-lg font-semibold text-white transition-opacity hover:opacity-90"
                          style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
                        >
                          Contact for Quote
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 text-center text-xs text-cyber-muted">
                    💡 Try fixing yourself first. If you get stuck, we're here to help!
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
