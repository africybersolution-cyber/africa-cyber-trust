'use client';
import { config } from '@/lib/config';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { AssetVerificationModal } from '@/components/asset-verification-modal';
import { getIndustry, prioritizeFindings, isFindingRelevant } from '@/lib/industries';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export default function AssetsPage() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showMobileUpload, setShowMobileUpload] = useState(false);
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [mobileAppName, setMobileAppName] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [fileError, setFileError] = useState('');
  const [verifyingAsset, setVerifyingAsset] = useState<any>(null);
  const [selectedAsset, setSelectedAsset] = useState<any>(null);
  const [scanResults, setScanResults] = useState<any>(null);
  const [findings, setFindings] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [toast, setToast] = useState<{message: string, type: 'success'|'error'|'info'} | null>(null);
  const [scanningAssetId, setScanningAssetId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<any>(null);
  const { token, company, loading: authLoading } = useAuth();
  const [subscription, setSubscription] = useState<any>(null);
  const [assetLimit, setAssetLimit] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    asset_type: 'domain',
    value: '',
    description: ''
  });

  const industry = getIndustry(company?.industry);

  // Validate mobile app file
  const validateMobileFile = (file: File): string | null => {
    const validExtensions = ['.apk', '.ipa', '.aab'];
    const extension = file.name.toLowerCase().match(/\.\w+$/)?.[0];
    const maxSize = 200 * 1024 * 1024; // 200MB

    if (!extension || !validExtensions.includes(extension)) {
      return '❌ Only APK, IPA, or AAB files are allowed';
    }
    if (file.size > maxSize) {
      return `❌ File size must be under 200MB (current: ${(file.size / (1024 * 1024)).toFixed(1)}MB)`;
    }
    return null;
  };

  useEffect(() => {
    if (token) {
      loadAssets();
      loadSubscription();
    }
  }, [token]);

  const loadSubscription = async () => {
    try {
      const res = await fetch(`${config.apiUrl}/api/payments/subscription`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSubscription(data);

        // Determine asset limit based on plan
        if (data.plan === 'starter') {
          setAssetLimit(5);
        } else if (data.plan === 'professional' || data.plan === 'enterprise') {
          setAssetLimit(null); // Unlimited
        } else {
          setAssetLimit(0); // FREE tier
        }
      }
    } catch (err) {
      console.error('Error loading subscription:', err);
    }
  };

  const handleAddAssetClick = () => {
    // Check asset limit
    if (assetLimit !== null && assets.length >= assetLimit) {
      setToast({
        message: `⚠️ Asset limit reached (${assetLimit} max on ${subscription?.plan?.toUpperCase()} plan). Upgrade to Professional for unlimited assets.`,
        type: 'error'
      });
      setTimeout(() => {
        window.location.href = '/dashboard/billing';
      }, 2000);
      return;
    }
    setShowAddModal(true);
  };

  const loadAssets = async () => {
    try {
      const res = await fetch(`${config.apiUrl}/api/assets/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setAssets(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generatePDFReport = () => {
    if (!selectedAsset) return;

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    let yPos = 20;

    // Header with branding
    doc.setFillColor(0, 71, 171); // #0047AB
    doc.rect(0, 0, pageWidth, 35, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('AFRICA CYBER TRUST', pageWidth / 2, 15, { align: 'center' });

    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Security Assessment Report', pageWidth / 2, 25, { align: 'center' });

    yPos = 45;

    // Report Info
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, yPos);
    yPos += 7;
    doc.text(`Report ID: ACT-${Date.now().toString().slice(-8)}`, 14, yPos);
    yPos += 15;

    // Asset Information
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Asset Information', 14, yPos);
    yPos += 10;

    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);
    doc.text(`Asset Name: ${selectedAsset.name}`, 14, yPos);
    yPos += 7;
    doc.text(`Domain/URL: ${selectedAsset.value}`, 14, yPos);
    yPos += 7;
    doc.text(`Verification Status: ${selectedAsset.verification_status || 'N/A'}`, 14, yPos);
    yPos += 15;

    // Security Score Section
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Security Assessment', 14, yPos);
    yPos += 10;

    const score = selectedAsset.security_score || 0;
    const scoreColor = score >= 80 ? [16, 185, 129] : score >= 60 ? [245, 158, 11] : score >= 40 ? [251, 146, 60] : [239, 68, 68];

    doc.setFillColor(scoreColor[0], scoreColor[1], scoreColor[2]);
    doc.roundedRect(14, yPos - 5, 50, 20, 3, 3, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text(`${score}/100`, 39, yPos + 7, { align: 'center' });

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.text(`Issues Found: ${selectedAsset.findings_count || 0}`, 70, yPos + 5);

    yPos += 25;

    // Scan History Summary
    if (scanResults && scanResults.length > 0) {
      const latestScan = scanResults[0];
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Latest Scan Results', 14, yPos);
      yPos += 8;

      const summaryData = [
        ['Critical Issues', latestScan.critical_count || 0],
        ['High Severity', latestScan.high_count || 0],
        ['Medium Severity', latestScan.medium_count || 0],
        ['Low Severity', latestScan.low_count || 0]
      ];

      autoTable(doc, {
        startY: yPos,
        head: [['Severity Level', 'Count']],
        body: summaryData,
        theme: 'grid',
        headStyles: { fillColor: [0, 71, 171], textColor: 255 },
        margin: { left: 14, right: 14 },
        styles: { fontSize: 10 }
      });

      yPos = (doc as any).lastAutoTable.finalY + 15;
    }

    // Findings Details
    if (findings && findings.length > 0) {
      // Check if we need a new page
      if (yPos > pageHeight - 60) {
        doc.addPage();
        yPos = 20;
      }

      doc.setFontSize(16);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(0, 71, 171);
      doc.text('Security Issues & Recommendations', 14, yPos);
      yPos += 10;

      const findingsData = findings.map((finding: any) => {
        const severityColors: any = {
          critical: [220, 38, 38],
          high: [249, 115, 22],
          medium: [234, 179, 8],
          low: [59, 130, 246]
        };

        return [
          finding.severity.toUpperCase(),
          finding.title,
          finding.description,
          finding.recommendation || 'Review and address'
        ];
      });

      autoTable(doc, {
        startY: yPos,
        head: [['Severity', 'Issue', 'Problem', 'Recommendation']],
        body: findingsData,
        theme: 'striped',
        headStyles: { fillColor: [0, 71, 171], textColor: 255, fontStyle: 'bold' },
        columnStyles: {
          0: { cellWidth: 20, fontStyle: 'bold' },
          1: { cellWidth: 40 },
          2: { cellWidth: 60 },
          3: { cellWidth: 60 }
        },
        margin: { left: 14, right: 14 },
        styles: { fontSize: 9, cellPadding: 3 },
        didParseCell: function(data: any) {
          if (data.section === 'body' && data.column.index === 0) {
            const severity = data.cell.raw.toLowerCase();
            const colors: any = {
              critical: [220, 38, 38],
              high: [249, 115, 22],
              medium: [234, 179, 8],
              low: [59, 130, 246]
            };
            if (colors[severity]) {
              data.cell.styles.textColor = colors[severity];
              data.cell.styles.fontStyle = 'bold';
            }
          }
        }
      });

      yPos = (doc as any).lastAutoTable.finalY + 15;
    }

    // Footer on last page
    const totalPages = doc.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      doc.text(
        `Africa Cyber Trust - Security Assessment Report | Page ${i} of ${totalPages}`,
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      );
      doc.text(
        'Confidential - For Internal Use Only',
        pageWidth / 2,
        pageHeight - 6,
        { align: 'center' }
      );
    }

    // Save PDF
    const fileName = `ACT_Security_Report_${selectedAsset.name.replace(/[^a-z0-9]/gi, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
    doc.save(fileName);
  };

  const handleAddAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Debug logging
    console.log('Token:', token ? 'EXISTS' : 'NULL');
    console.log('Token length:', token?.length);
    console.log('Form data:', formData);

    try {
      const res = await fetch(`${config.apiUrl}/api/assets/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      console.log('Response status:', res.status);

      if (res.ok) {
        const newAsset = await res.json();
        setShowAddModal(false);
        setFormData({ name: '', asset_type: 'domain', value: '', description: '' });

        // Show verification modal for domain/subdomain assets
        if (formData.asset_type === 'domain' || formData.asset_type === 'subdomain') {
          setVerifyingAsset(newAsset);
          setShowVerifyModal(true);
        } else {
          loadAssets();
        }
      } else {
        const errorData = await res.json().catch(() => ({ detail: `HTTP ${res.status}: ${res.statusText}` }));
        console.log('Error response:', errorData);
        console.log('Response headers:', res.headers);
        const errorMsg = errorData.detail || `Failed with status ${res.status}`;

        // Show detailed error
        setError(`${errorMsg}${!token ? ' - No authentication token found!' : ''}`);

        // Show toast with more details
        setToast({
          message: `❌ ${errorMsg}`,
          type: 'error'
        });
      }
    } catch (err) {
      console.error('Add asset error:', err);
      const errorMsg = `Network error: ${err instanceof Error ? err.message : 'Unknown error'}. Backend might not be running.`;
      setError(errorMsg);
      setToast({
        message: `❌ ${errorMsg}`,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Wait for auth to load
  if (authLoading) {
    return (
      <div className="min-h-screen cyber-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-t-blue-500 border-[#1B2C4F] rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-cyber-muted text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  // Everyone can now add assets with STARTER tier - no business account required

  return (
    <div className="min-h-screen cyber-bg p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-2">
          <a href="/dashboard" className="text-sm text-cyber-muted hover:text-white transition">← Back to dashboard</a>
        </div>
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Assets</h1>
            <p className="text-cyber-muted text-sm mt-1">Deep scanning runs only on assets with verified ownership.</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleAddAssetClick}
              className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg"
              style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
            >
              + Add Asset
            </button>
            <button
              onClick={() => setShowMobileUpload(true)}
              className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg"
              style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
            >
              📱 Add Mobile App
            </button>
          </div>
        </div>

        {/* Asset Limit Warning Banner */}
        {assetLimit !== null && assets.length >= assetLimit - 1 && (
          <div className={`mb-6 rounded-xl p-4 border-2 ${
            assets.length >= assetLimit
              ? 'bg-red-500/10 border-red-500/50'
              : 'bg-yellow-500/10 border-yellow-500/50'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className={`font-bold mb-1 ${
                  assets.length >= assetLimit ? 'text-red-400' : 'text-yellow-400'
                }`}>
                  {assets.length >= assetLimit
                    ? '⚠️ Asset Limit Reached'
                    : '⚠️ Approaching Asset Limit'}
                </h3>
                <p className="text-sm text-cyber-muted">
                  You have {assets.length} of {assetLimit} assets on the {subscription?.plan?.toUpperCase()} plan.
                  {assets.length >= assetLimit
                    ? ' Upgrade to Professional for unlimited assets.'
                    : ' Upgrade soon for unlimited assets.'}
                </p>
              </div>
              <a
                href="/dashboard/billing"
                className="px-6 py-3 rounded-xl font-semibold text-white shadow-lg whitespace-nowrap"
                style={{ background: 'linear-gradient(135deg, #DAA520 0%, #B8860B 100%)' }}
              >
                Upgrade to Professional
              </a>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 border-4 border-t-blue-500 border-[#1B2C4F] rounded-full animate-spin mx-auto"></div>
          </div>
        ) : assets.length === 0 ? (
          <div className="cyber-card-raised p-12 text-center max-w-3xl mx-auto">
            <div className="text-6xl mb-6">🛡️</div>
            <h3 className="text-2xl font-bold mb-3 text-white">Start Monitoring Your Digital Assets</h3>
            <p className="text-cyber-muted mb-8">Add a website or mobile app, verify ownership, then run deep security scans.</p>

            <div className="grid md:grid-cols-2 gap-4 mb-8">
              <div className="cyber-card p-6 hover:cyber-glow-blue transition-all cursor-pointer text-left" onClick={() => setShowAddModal(true)}>
                <div className="text-4xl mb-3">🌐</div>
                <h4 className="font-bold text-lg mb-2 text-white">Add Website</h4>
                <p className="text-sm text-cyber-muted mb-3">Monitor domains, subdomains, or APIs</p>
                <div className="bg-[#050B1A] border border-cyber rounded-lg p-2 text-xs text-cyber-muted">
                  Example: https://example.com
                </div>
              </div>

              <div className="cyber-card p-6 hover:cyber-glow-gold transition-all cursor-pointer text-left" onClick={() => setShowMobileUpload(true)}>
                <div className="text-4xl mb-3">📱</div>
                <h4 className="font-bold text-lg mb-2" style={{ color: '#10B981' }}>Add Mobile App</h4>
                <p className="text-sm text-cyber-muted mb-3">Scan Android APK files for vulnerabilities</p>
                <div className="bg-[#050B1A] border border-cyber rounded-lg p-2 text-xs text-cyber-muted">
                  Upload: MyApp.apk
                </div>
              </div>
            </div>

            <div className="bg-[#0A1428] border-l-4 p-4 text-left rounded" style={{ borderColor: '#DAA520' }}>
              <p className="text-sm text-cyber-muted">
                <strong className="text-white">What you&apos;ll get:</strong> Security score (0-100), CVSS-scored vulnerability findings, remediation guidance, PDF reports, and continuous monitoring.
              </p>
            </div>
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-6">
            {assets.map((asset: any) => {
              const verified = String(asset.verification_status).toUpperCase() === 'VERIFIED';
              const failed = String(asset.verification_status).toUpperCase() === 'FAILED';
              const sc = asset.security_score;
              const scColor = sc == null ? '#8FA3C4' : sc >= 80 ? '#10B981' : sc >= 60 ? '#DAA520' : sc >= 40 ? '#F97316' : '#EF4444';
              return (
              <div
                key={asset.id}
                className="cyber-card-raised p-6 hover:cyber-glow-blue transition-all"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold mb-1 text-white truncate">{asset.name}</h3>
                    <p className="text-sm text-cyber-muted truncate">{asset.value}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeleteConfirm(asset);
                      }}
                      className="p-2 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors"
                      title="Delete asset"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="text-[10px] text-cyber-muted uppercase">Ownership</div>
                    <div className={`font-bold px-2 py-1 rounded-full text-[10px] inline-flex items-center gap-1 mt-1 ${
                      verified ? 'bg-green-500/15 text-green-400' : failed ? 'bg-red-500/15 text-red-400' : 'bg-yellow-500/15 text-yellow-400'
                    }`}>
                      {verified && (
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                      )}
                      {verified ? 'VERIFIED' : failed ? 'FAILED' : 'PENDING'}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] text-cyber-muted uppercase">Score</div>
                    <div className="text-2xl font-bold" style={{ color: scColor }}>
                      {sc !== null && sc !== undefined ? sc : '—'}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] text-cyber-muted uppercase">Findings</div>
                    <div className="text-2xl font-bold" style={{ color: '#DAA520' }}>
                      {asset.findings_count || 0}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={async (e) => {
                      e.stopPropagation();
                      if (scanningAssetId) return; // Prevent multiple clicks

                      // Check if asset is verified before scanning
                      const isVerified = String(asset.verification_status).toUpperCase() === 'VERIFIED';
                      if (!isVerified) {
                        setToast({
                          message: '⚠️ Please verify domain ownership before scanning. Click "Verify" to start.',
                          type: 'error'
                        });
                        setTimeout(() => setToast(null), 5000);
                        return;
                      }

                      try {
                        setScanningAssetId(asset.id);
                        setToast({ message: 'Starting security scan...', type: 'info' });

                        const res = await fetch(`${config.apiUrl}/api/scans/assets/${asset.id}/scan`, {
                          method: 'POST',
                          headers: { 'Authorization': `Bearer ${token}` }
                        });

                        if (res.ok) {
                          const data = await res.json();
                          setToast({ message: '⏳ Scanning... This takes ~10 seconds', type: 'info' });

                          setTimeout(async () => {
                            await loadAssets();
                            setScanningAssetId(null);
                            setToast({ message: `✅ Scan complete! Score: ${data.score || 'N/A'}/100`, type: 'success' });
                            setTimeout(() => setToast(null), 5000);
                          }, 10000);
                        } else {
                          setScanningAssetId(null);
                          setToast({ message: '❌ Scan failed. Please try again.', type: 'error' });
                          setTimeout(() => setToast(null), 5000);
                        }
                      } catch (err) {
                        console.error(err);
                        setScanningAssetId(null);
                        setToast({ message: '❌ Scan failed. Please try again.', type: 'error' });
                        setTimeout(() => setToast(null), 5000);
                      }
                    }}
                    disabled={scanningAssetId === asset.id}
                    className="flex-1 py-2 rounded-xl font-semibold text-white text-sm hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
                  >
                    {scanningAssetId === asset.id ? (
                      <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Scanning...
                      </span>
                    ) : '🔄 Scan Now'}
                  </button>
                  <button
                    onClick={async (e) => {
                      e.stopPropagation();
                      setSelectedAsset(asset);

                      // Fetch scan results and findings
                      try {
                        const res = await fetch(`${config.apiUrl}/api/scans/assets/${asset.id}/scans`, {
                          headers: { 'Authorization': `Bearer ${token}` }
                        });
                        if (res.ok) {
                          const scans = await res.json();
                          setScanResults(scans);
                        }

                        // Fetch findings
                        const findingsRes = await fetch(`${config.apiUrl}/api/scans/assets/${asset.id}/findings`, {
                          headers: { 'Authorization': `Bearer ${token}` }
                        });
                        if (findingsRes.ok) {
                          const findingsData = await findingsRes.json();
                          setFindings(findingsData);
                        }
                      } catch (err) {
                        console.error(err);
                      }

                      setShowReportModal(true);
                    }}
                    className="flex-1 py-2 rounded-xl font-semibold border-2 hover:bg-white/5 transition-colors"
                    style={{ borderColor: '#1E90FF', color: '#1E90FF' }}
                  >
                    📄 View Report
                  </button>
                </div>
                {!verified && (
                  <p className="mt-3 text-[11px] text-yellow-400/90">
                    Verify ownership to unlock authorized deep scanning.
                  </p>
                )}
              </div>
              );
            })}
          </div>
        )}

        {showAddModal && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="cyber-card-raised shadow-2xl max-w-md w-full p-8">
              <h2 className="text-2xl font-bold mb-6 text-white">Add New Asset</h2>
              <form onSubmit={handleAddAsset} className="space-y-4">
                {error && (
                  <div className="bg-red-500/10 border-l-4 border-red-500 p-4 rounded">
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}
                <div>
                  <label className="block text-sm font-semibold mb-2 text-cyber-muted">Asset Name</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl bg-[#050B1A] border border-cyber text-white focus:border-blue-500 focus:outline-none"
                    placeholder="My Website"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2 text-cyber-muted">Type</label>
                  <select
                    value={formData.asset_type}
                    onChange={(e) => setFormData({ ...formData, asset_type: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl bg-[#050B1A] border border-cyber text-white focus:border-blue-500 focus:outline-none"
                  >
                    <option value="domain">🌐 Domain / Website</option>
                    <option value="subdomain">📂 Subdomain</option>
                    <option value="api_endpoint">🔌 API Endpoint</option>
                    <option value="ip_address">🖥️ IP Address</option>
                    <option value="ip_range">🌐 IP Range (CIDR)</option>
                    <option value="cloud_storage">☁️ Cloud Storage (S3, Azure, GCP)</option>
                    <option value="email_domain">📧 Email Domain (SPF/DMARC)</option>
                    <option value="source_code_repo">🔐 Source Code Repo (GitHub/GitLab)</option>
                    <option value="ssl_certificate">🔒 SSL Certificate</option>
                  </select>
                  <p className="text-xs text-cyber-muted mt-1">For mobile apps, use the &quot;📱 Add Mobile App&quot; button</p>
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2 text-cyber-muted">
                    {formData.asset_type === 'ip_address' ? 'IP Address' :
                     formData.asset_type === 'ip_range' ? 'IP Range (CIDR)' :
                     formData.asset_type === 'cloud_storage' ? 'Bucket URL' :
                     formData.asset_type === 'email_domain' ? 'Domain Name' :
                     formData.asset_type === 'source_code_repo' ? 'Repository URL' :
                     formData.asset_type === 'ssl_certificate' ? 'Domain Name' :
                     'URL / Value'}
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.value}
                    onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl bg-[#050B1A] border border-cyber text-white focus:border-blue-500 focus:outline-none"
                    placeholder={
                      formData.asset_type === 'api_endpoint' ? 'https://api.example.com/v1' :
                      formData.asset_type === 'ip_address' ? '203.0.113.45' :
                      formData.asset_type === 'ip_range' ? '203.0.113.0/24' :
                      formData.asset_type === 'cloud_storage' ? 's3://my-bucket or https://my-bucket.s3.amazonaws.com' :
                      formData.asset_type === 'email_domain' ? 'example.com' :
                      formData.asset_type === 'source_code_repo' ? 'https://github.com/user/repo' :
                      formData.asset_type === 'ssl_certificate' ? 'example.com' :
                      'https://example.com'
                    }
                  />
                </div>
                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="flex-1 py-3 rounded-xl font-semibold border border-cyber text-cyber-muted hover:bg-white/5"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-3 rounded-xl font-semibold text-white shadow-lg"
                    style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                  >
                    Add Asset
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Mobile App Upload Modal */}
        {showMobileUpload && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="cyber-card-raised shadow-2xl max-w-md w-full p-8">
              <h2 className="text-2xl font-bold mb-6" style={{ color: '#10B981' }}>📱 Upload Mobile App</h2>

              <div className="space-y-4">
                {error && (
                  <div className="bg-red-500/10 border-l-4 border-red-500 p-4 rounded">
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-semibold mb-2 text-cyber-muted">App Name</label>
                  <input
                    type="text"
                    required
                    value={mobileAppName}
                    onChange={(e) => setMobileAppName(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-[#050B1A] border border-cyber text-white focus:border-green-500 focus:outline-none"
                    placeholder="My Awesome App"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-cyber-muted">APK/IPA File</label>
                  <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                    fileError ? 'border-red-500' : 'border-cyber hover:border-green-500'
                  }`}>
                    <input
                      type="file"
                      accept=".apk,.ipa,.aab"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          const file = e.target.files[0];
                          const error = validateMobileFile(file);
                          if (error) {
                            setFileError(error);
                            setUploadFile(null);
                          } else {
                            setFileError('');
                            setUploadFile(file);
                          }
                        }
                      }}
                      className="hidden"
                      id="apk-upload"
                      disabled={uploading}
                    />
                    <label htmlFor="apk-upload" className={`cursor-pointer ${uploading ? 'opacity-50' : ''}`}>
                      {uploadFile ? (
                        <div>
                          <div className="text-4xl mb-2">✅</div>
                          <p className="text-green-400 font-semibold">{uploadFile.name}</p>
                          <p className="text-cyber-muted text-sm">{(uploadFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                        </div>
                      ) : (
                        <div>
                          <div className="text-4xl mb-2">📤</div>
                          <p className="text-cyber-muted font-semibold">Click to upload APK/IPA/AAB</p>
                          <p className="text-cyber-muted/70 text-sm mt-1">Max size: 200MB</p>
                        </div>
                      )}
                    </label>
                  </div>
                  {fileError && (
                    <p className="text-red-400 text-sm mt-2">{fileError}</p>
                  )}
                </div>

                {/* Upload Progress Bar */}
                {uploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-cyber-muted">Uploading...</span>
                      <span className="text-white font-semibold">{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                <div className="bg-[#0A1428] border-l-4 border-blue-500 p-4 rounded">
                  <p className="text-cyber-muted text-sm">
                    <strong className="text-white">Supported:</strong> Android APK/AAB, iOS IPA files<br />
                    <strong className="text-white">Max size:</strong> 200MB per file
                  </p>
                </div>

                <div className="flex gap-4 mt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setShowMobileUpload(false);
                      setUploadFile(null);
                      setMobileAppName('');
                    }}
                    className="flex-1 py-3 rounded-xl font-semibold border border-cyber text-cyber-muted hover:bg-white/5"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => {
                      if (!uploadFile || !mobileAppName) {
                        setError('Please provide app name and file');
                        return;
                      }

                      setUploading(true);
                      setUploadProgress(0);
                      setToast({ message: '📤 Uploading mobile app...', type: 'info' });

                      const formData = new FormData();
                      formData.append('file', uploadFile);
                      formData.append('name', mobileAppName);

                      const xhr = new XMLHttpRequest();

                      // Progress tracking
                      xhr.upload.addEventListener('progress', (e) => {
                        if (e.lengthComputable) {
                          const percent = Math.round((e.loaded / e.total) * 100);
                          setUploadProgress(percent);
                        }
                      });

                      // Success
                      xhr.addEventListener('load', () => {
                        setUploading(false);
                        if (xhr.status === 200) {
                          setToast({ message: `✅ ${mobileAppName} uploaded! Security scan started.`, type: 'success' });
                          setTimeout(() => setToast(null), 5000);
                          setShowMobileUpload(false);
                          setUploadFile(null);
                          setMobileAppName('');
                          setUploadProgress(0);
                          loadAssets();
                        } else {
                          setError('Upload failed');
                          setToast({ message: '❌ Upload failed. Please try again.', type: 'error' });
                          setTimeout(() => setToast(null), 5000);
                        }
                      });

                      // Error
                      xhr.addEventListener('error', () => {
                        setUploading(false);
                        setError('Upload failed');
                        setToast({ message: '❌ Upload failed. Please try again.', type: 'error' });
                        setTimeout(() => setToast(null), 5000);
                      });

                      // Send request
                      xhr.open('POST', `${config.apiUrl}/api/assets/mobile-app/upload`);
                      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
                      xhr.send(formData);
                    }}
                    disabled={!uploadFile || !mobileAppName || uploading || !!fileError}
                    className="flex-1 py-3 rounded-xl font-semibold text-white shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
                  >
                    {uploading ? `⏳ Uploading ${uploadProgress}%` : '📤 Upload & Scan'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Verification Modal */}
        {showVerifyModal && verifyingAsset && (
          <AssetVerificationModal
            assetId={verifyingAsset.id}
            domain={verifyingAsset.value}
            onClose={() => {
              setShowVerifyModal(false);
              setVerifyingAsset(null);
              loadAssets();
            }}
            onVerified={() => {
              setShowVerifyModal(false);
              setVerifyingAsset(null);
              loadAssets();
            }}
          />
        )}

        {/* Report Modal */}
        {showReportModal && selectedAsset && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="cyber-card-raised shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className="sticky top-0 bg-[#0F1E3D] border-b border-cyber p-6 rounded-t-2xl">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-2xl font-bold mb-2 text-white">
                      Security Report: {selectedAsset.name}
                    </h2>
                    <p className="text-cyber-muted text-sm">{selectedAsset.value}</p>
                  </div>
                  <button
                    onClick={() => {
                      setShowReportModal(false);
                      setSelectedAsset(null);
                      setScanResults(null);
                      setFindings([]);
                    }}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <svg className="w-6 h-6 text-cyber-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                {/* Security Score Card */}
                <div className="cyber-card p-6 mb-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-cyber-muted mb-1">Security Score</div>
                      <div className={`text-6xl font-bold ${
                        (selectedAsset.security_score || 0) >= 80 ? 'text-green-600' :
                        (selectedAsset.security_score || 0) >= 60 ? 'text-yellow-600' :
                        (selectedAsset.security_score || 0) >= 40 ? 'text-orange-600' : 'text-red-600'
                      }`}>
                        {selectedAsset.security_score !== null && selectedAsset.security_score !== undefined
                          ? selectedAsset.security_score
                          : '—'}
                        <span className="text-2xl">/100</span>
                      </div>
                      <div className="text-sm text-cyber-muted mt-2">
                        {(selectedAsset.security_score || 0) >= 80 ? '🟢 Low Risk' :
                         (selectedAsset.security_score || 0) >= 60 ? '🟡 Medium Risk' :
                         (selectedAsset.security_score || 0) >= 40 ? '🟠 High Risk' : '🔴 Critical Risk'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-cyber-muted mb-2">Findings</div>
                      <div className="text-4xl font-bold" style={{ color: '#DAA520' }}>
                        {selectedAsset.findings_count || 0}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Scan Schedule Settings */}
                <div className="mb-6 cyber-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-bold" style={{ color: '#10B981' }}>⏰ Automatic Scanning</h3>
                      <p className="text-sm text-cyber-muted mt-1">Schedule regular authorized security scans</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedAsset?.scan_enabled ?? true}
                        onChange={async (e) => {
                          const enabled = e.target.checked;
                          try {
                            const res = await fetch(`${config.apiUrl}/api/assets/${selectedAsset.id}`, {
                              method: 'PATCH',
                              headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`
                              },
                              body: JSON.stringify({ scan_enabled: enabled })
                            });
                            if (res.ok) {
                              setSelectedAsset({ ...selectedAsset, scan_enabled: enabled });
                              loadAssets();
                            }
                          } catch (err) {
                            console.error(err);
                          }
                        }}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                    </label>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-semibold text-cyber-muted mb-2">Scan Frequency:</label>
                      <select
                        value={selectedAsset?.scan_interval || 'daily'}
                        onChange={async (e) => {
                          const interval = e.target.value;
                          try {
                            const res = await fetch(`${config.apiUrl}/api/assets/${selectedAsset.id}`, {
                              method: 'PATCH',
                              headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`
                              },
                              body: JSON.stringify({ scan_interval: interval })
                            });
                            if (res.ok) {
                              setSelectedAsset({ ...selectedAsset, scan_interval: interval });
                              loadAssets();
                            }
                          } catch (err) {
                            console.error(err);
                          }
                        }}
                        disabled={!selectedAsset?.scan_enabled}
                        className="w-full px-4 py-2 bg-[#050B1A] border border-cyber text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <option value="1h">Every Hour</option>
                        <option value="6h">Every 6 Hours</option>
                        <option value="12h">Every 12 Hours</option>
                        <option value="24h">Daily (24 hours)</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                      </select>
                    </div>

                    {selectedAsset?.next_scan_at && (
                      <div className="bg-[#050B1A] border border-cyber rounded-lg p-3">
                        <p className="text-xs text-cyber-muted">Next scheduled scan:</p>
                        <p className="text-sm font-semibold text-white">
                          {new Date(selectedAsset.next_scan_at).toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Scan History */}
                <div className="mb-6">
                  <h3 className="text-lg font-bold mb-4 text-white">Scan History</h3>
                  {!scanResults || scanResults.length === 0 ? (
                    <div className="cyber-card p-8 text-center">
                      <p className="text-cyber-muted mb-4">No scans performed yet</p>
                      <button
                        onClick={async () => {
                          try {
                            const res = await fetch(`${config.apiUrl}/api/scans/assets/${selectedAsset.id}/scan`, {
                              method: 'POST',
                              headers: { 'Authorization': `Bearer ${token}` }
                            });
                            if (res.ok) {
                              alert('🔍 Investigation started! Close and reopen report in 10 seconds.');
                            }
                          } catch (err) {
                            console.error(err);
                          }
                        }}
                        className="px-6 py-2 rounded-xl font-semibold text-white"
                        style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
                      >
                        Run First Investigation
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {scanResults.map((scan: any) => (
                        <div key={scan.id} className="cyber-card p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <div className="font-bold text-lg text-white">
                                Score: {scan.score}/100
                              </div>
                              <div className="text-sm text-cyber-muted">
                                {new Date(scan.started_at).toLocaleString()}
                              </div>
                            </div>
                            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              scan.status === 'completed' ? 'bg-green-500/15 text-green-400' :
                              scan.status === 'running' ? 'bg-blue-500/15 text-blue-400' :
                              scan.status === 'failed' ? 'bg-red-500/15 text-red-400' :
                              'bg-yellow-500/15 text-yellow-400'
                            }`}>
                              {scan.status}
                            </div>
                          </div>
                          <div className="grid grid-cols-4 gap-4">
                            <div>
                              <div className="text-xs text-cyber-muted">Critical</div>
                              <div className="text-lg font-bold text-red-400">{scan.critical_count || 0}</div>
                            </div>
                            <div>
                              <div className="text-xs text-cyber-muted">High</div>
                              <div className="text-lg font-bold text-orange-400">{scan.high_count || 0}</div>
                            </div>
                            <div>
                              <div className="text-xs text-cyber-muted">Medium</div>
                              <div className="text-lg font-bold text-yellow-400">{scan.medium_count || 0}</div>
                            </div>
                            <div>
                              <div className="text-xs text-cyber-muted">Low</div>
                              <div className="text-lg font-bold text-cyber-muted">{scan.low_count || 0}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Security Issues / Findings */}
                {findings && findings.length > 0 && (
                  <div className="mb-6">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                      <h3 className="text-lg font-bold text-white">
                        🔍 Security Findings
                      </h3>
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border" style={{ borderColor: '#DAA520', color: '#DAA520' }}>
                        {industry.icon} Prioritized for {industry.label}
                      </span>
                    </div>
                    <p className="text-xs text-cyber-muted mb-4">
                      Findings most relevant to your industry are shown first and tagged <span style={{ color: '#DAA520' }} className="font-semibold">Industry Priority</span>.
                    </p>
                    <div className="space-y-3">
                      {prioritizeFindings(industry, findings).map((finding: any) => {
                        const relevant = isFindingRelevant(industry, finding);
                        return (
                        <div
                          key={finding.id}
                          className={`border-l-4 rounded-lg p-4 bg-[#0A1428] ${
                            finding.severity === 'critical' ? 'border-red-500' :
                            finding.severity === 'high' ? 'border-orange-500' :
                            finding.severity === 'medium' ? 'border-yellow-500' :
                            'border-blue-500'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1 flex-wrap">
                                <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                                  finding.severity === 'critical' ? 'bg-red-600 text-white' :
                                  finding.severity === 'high' ? 'bg-orange-600 text-white' :
                                  finding.severity === 'medium' ? 'bg-yellow-600 text-white' :
                                  'bg-blue-600 text-white'
                                }`}>
                                  {finding.severity}
                                </span>
                                {relevant && (
                                  <span className="px-2 py-1 rounded text-xs font-bold" style={{ background: '#DAA52022', color: '#DAA520' }}>
                                    ⭐ Industry Priority
                                  </span>
                                )}
                                {finding.cvss && (
                                  <span className="px-2 py-1 rounded text-xs font-bold bg-white/10 text-white">CVSS {finding.cvss}</span>
                                )}
                                <span className="text-xs text-cyber-muted">{finding.category}</span>
                              </div>
                              <h4 className="font-bold text-white">{finding.title}</h4>
                            </div>
                          </div>

                          <div className="space-y-2 text-sm">
                            <div>
                              <span className="font-semibold text-cyber-muted">Problem:</span>
                              <p className="text-cyber-muted mt-1">{finding.description}</p>
                            </div>

                            {finding.recommendation && (
                              <div>
                                <span className="font-semibold text-green-400">✓ Remediation:</span>
                                <p className="text-cyber-muted mt-1">{finding.recommendation}</p>
                              </div>
                            )}
                          </div>
                        </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Industry best-practice recommendations */}
                <div className="cyber-card p-6 mb-6 border-l-4" style={{ borderColor: '#DAA520' }}>
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-bold text-white">{industry.icon} {industry.label} Best Practices</h3>
                  </div>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {industry.compliance.map((c) => (
                      <span key={c.label} title={c.full} className="px-2 py-0.5 rounded-full text-[10px] font-bold border" style={{ borderColor: '#DAA520', color: '#DAA520' }}>
                        {c.label}
                      </span>
                    ))}
                  </div>
                  <ul className="space-y-2 text-sm text-cyber-muted">
                    {industry.recommendations.map((r) => (
                      <li key={r} className="flex items-start gap-2">
                        <span style={{ color: '#DAA520' }}>•</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Recommendations */}
                <div className="cyber-card p-6">
                  <h3 className="text-lg font-bold mb-3 text-white">
                    💡 Recommendations
                  </h3>
                  <ul className="space-y-2 text-sm text-cyber-muted">
                    {selectedAsset.security_score === 0 || !selectedAsset.last_scan_at ? (
                      <li>• Run your first security investigation to get detailed recommendations</li>
                    ) : (
                      <>
                        <li>• Run regular security investigations (weekly recommended)</li>
                        <li>• Monitor security score trends over time</li>
                        <li>• Address critical and high severity issues immediately</li>
                        <li>• Keep SSL certificates up to date</li>
                        <li>• Implement security headers for better protection</li>
                      </>
                    )}
                  </ul>
                </div>
              </div>

              {/* Footer */}
              <div className="sticky bottom-0 bg-[#0F1E3D] border-t border-cyber p-4 rounded-b-2xl flex gap-3">
                <button
                  onClick={() => {
                    setShowReportModal(false);
                    setSelectedAsset(null);
                    setScanResults(null);
                    setFindings([]);
                  }}
                  className="py-3 px-6 rounded-xl font-semibold border border-cyber text-cyber-muted hover:bg-white/5 transition-colors"
                >
                  Close
                </button>
                <button
                  onClick={generatePDFReport}
                  className="flex-1 py-3 rounded-xl font-semibold text-white hover:opacity-90 transition-opacity"
                  style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                >
                  📥 Download Report
                </button>
                <button
                  onClick={async () => {
                    try {
                      const res = await fetch(`${config.apiUrl}/api/scans/assets/${selectedAsset.id}/scan`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                      });
                      if (res.ok) {
                        alert('🔍 New investigation started! Results in 10 seconds.');
                        setTimeout(() => {
                          setShowReportModal(false);
                          loadAssets();
                        }, 10000);
                      }
                    } catch (err) {
                      console.error(err);
                    }
                  }}
                  className="flex-1 py-3 rounded-xl font-semibold text-white hover:opacity-90 transition-opacity"
                  style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
                >
                  🔍 Run New Investigation
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Toast Notification */}
        {toast && (
          <div className="fixed top-4 right-4 z-50 animate-slide-in">
            <div className={`rounded-xl shadow-2xl p-4 min-w-[300px] ${
              toast.type === 'success' ? 'bg-green-500' :
              toast.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
            } text-white font-semibold`}>
              {toast.message}
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="cyber-card-raised shadow-2xl max-w-md w-full p-8">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-red-500/15 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Delete Asset?</h3>
                <p className="text-cyber-muted mb-1">Are you sure you want to delete <strong className="text-white">{deleteConfirm.name}</strong>?</p>
                <p className="text-sm text-cyber-muted">This will permanently delete:</p>
                <ul className="text-sm text-cyber-muted mt-2 space-y-1">
                  <li>• All scan history</li>
                  <li>• All security findings</li>
                  <li>• All verification data</li>
                </ul>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="flex-1 py-3 rounded-xl font-semibold border border-cyber text-cyber-muted hover:bg-white/5"
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    try {
                      const res = await fetch(`${config.apiUrl}/api/assets/${deleteConfirm.id}`, {
                        method: 'DELETE',
                        headers: { 'Authorization': `Bearer ${token}` }
                      });
                      if (res.ok) {
                        setToast({ message: `✅ ${deleteConfirm.name} deleted successfully`, type: 'success' });
                        setTimeout(() => setToast(null), 5000);
                        setDeleteConfirm(null);
                        loadAssets();
                      } else {
                        setToast({ message: '❌ Failed to delete asset', type: 'error' });
                        setTimeout(() => setToast(null), 5000);
                      }
                    } catch (err) {
                      setToast({ message: '❌ Failed to delete asset', type: 'error' });
                      setTimeout(() => setToast(null), 5000);
                    }
                  }}
                  className="flex-1 py-3 rounded-xl font-semibold text-white bg-red-600 hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
