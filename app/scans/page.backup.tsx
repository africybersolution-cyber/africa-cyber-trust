'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { config } from '@/lib/config';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

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
}

interface Finding {
  id: string;
  title: string;
  severity: string;
  description: string;
  recommendation: string;
}

export default function ScansPage() {
  const { user, token, logout } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [scans, setScans] = useState<ScanData[]>([]);
  const [selectedScan, setSelectedScan] = useState<ScanData | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loadingFindings, setLoadingFindings] = useState(false);

  // Fetch all scans
  useEffect(() => {
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchAllScans = async () => {
      try {
        // First, fetch all assets
        const assetsRes = await fetch(`${config.apiUrl}/api/assets/`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!assetsRes.ok) {
          throw new Error('Failed to fetch assets');
        }

        const assets = await assetsRes.json();
        console.log('📊 Assets:', assets);

        // For each asset, fetch its scans
        const allScans: ScanData[] = [];

        for (const asset of assets) {
          try {
            const scansRes = await fetch(
              `${config.apiUrl}/api/scans/assets/${asset.id}/scans`,
              { headers: { Authorization: `Bearer ${token}` } }
            );

            if (scansRes.ok) {
              const assetScans = await scansRes.json();
              // Add asset info to each scan
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

        // Sort by date (newest first)
        allScans.sort((a, b) =>
          new Date(b.started_at).getTime() - new Date(a.started_at).getTime()
        );

        console.log('📊 All scans:', allScans);
        setScans(allScans);
      } catch (error) {
        console.error('Error fetching scans:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllScans();
  }, [token, router]);

  // Fetch findings when scan is selected
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading scans...</div>
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
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-white">Africa Cyber Trust</div>
                <div className="text-xs text-gray-400">Security Monitoring</div>
              </div>
            </a>

            <button
              onClick={() => logout()}
              className="px-4 py-2 text-sm font-semibold text-gray-400 hover:text-red-400 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Scans & Findings</h1>
          <p className="text-gray-400">View security scan results and vulnerability findings</p>
        </div>

        {scans.length === 0 ? (
          <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-12 border border-blue-900/30 text-center">
            <div className="w-20 h-20 rounded-full bg-blue-500/10 flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">No Scans Yet</h3>
            <p className="text-gray-400 mb-6">Add assets and run scans to see results here</p>
            <a
              href="/dashboard/assets"
              className="inline-block px-6 py-3 rounded-xl font-semibold text-white"
              style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
            >
              Go to Assets
            </a>
          </div>
        ) : (
          <div className="grid gap-6">
            {scans.map((scan) => (
              <div
                key={scan.id}
                className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-6 border border-blue-900/30 hover:border-blue-500/50 transition-all cursor-pointer"
                onClick={() => loadFindings(scan)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-1">{scan.asset_name}</h3>
                    <p className="text-sm text-gray-400">{scan.asset_value}</p>
                  </div>
                  <div className="text-right">
                    <div
                      className="text-3xl font-bold mb-1"
                      style={{ color: getScoreColor(scan.score) }}
                    >
                      {scan.score}/100
                    </div>
                    <div className="text-xs text-gray-400">{formatDate(scan.started_at)}</div>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-4 mb-4">
                  <div className="bg-red-500/10 rounded-lg p-3 border border-red-500/30">
                    <div className="text-2xl font-bold text-red-400">{scan.critical_count}</div>
                    <div className="text-xs text-gray-400">Critical</div>
                  </div>
                  <div className="bg-orange-500/10 rounded-lg p-3 border border-orange-500/30">
                    <div className="text-2xl font-bold text-orange-400">{scan.high_count}</div>
                    <div className="text-xs text-gray-400">High</div>
                  </div>
                  <div className="bg-yellow-500/10 rounded-lg p-3 border border-yellow-500/30">
                    <div className="text-2xl font-bold text-yellow-400">{scan.medium_count}</div>
                    <div className="text-xs text-gray-400">Medium</div>
                  </div>
                  <div className="bg-blue-500/10 rounded-lg p-3 border border-blue-500/30">
                    <div className="text-2xl font-bold text-blue-400">{scan.low_count}</div>
                    <div className="text-xs text-gray-400">Low</div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="text-gray-400">
                    Total Findings: <span className="text-white font-semibold">{scan.findings_count}</span>
                  </div>
                  <div className="text-blue-400 font-semibold hover:text-blue-300">
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
            <div className="bg-slate-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-auto p-8" onClick={(e) => e.stopPropagation()}>
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">{selectedScan.asset_name}</h2>
                  <p className="text-gray-400">{selectedScan.asset_value}</p>
                </div>
                <button
                  onClick={() => setSelectedScan(null)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>

              {loadingFindings ? (
                <div className="text-center py-12 text-gray-400">Loading findings...</div>
              ) : findings.length === 0 ? (
                <div className="text-center py-12 text-gray-400">No findings for this scan</div>
              ) : (
                <div className="space-y-4">
                  {findings.map((finding) => (
                    <div
                      key={finding.id}
                      className="bg-slate-900/50 rounded-xl p-6 border"
                      style={{ borderColor: getSeverityColor(finding.severity) + '40' }}
                    >
                      <div className="flex items-start gap-4">
                        <div
                          className="px-3 py-1 rounded-lg text-xs font-bold uppercase"
                          style={{
                            background: getSeverityColor(finding.severity) + '20',
                            color: getSeverityColor(finding.severity)
                          }}
                        >
                          {finding.severity}
                        </div>
                        <div className="flex-1">
                          <h4 className="text-lg font-bold text-white mb-2">{finding.title}</h4>
                          <p className="text-gray-400 text-sm mb-3">{finding.description}</p>
                          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                            <div className="text-xs font-semibold text-green-400 mb-1">RECOMMENDATION:</div>
                            <p className="text-sm text-gray-300">{finding.recommendation}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
