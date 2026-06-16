'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { config } from '@/lib/config';
import DashboardLayout from '@/components/DashboardLayout';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { LOGO_BASE64 } from './logo-base64';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

export default function ReportsPage() {
  const { token } = useAuth();
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [reportType, setReportType] = useState<'security' | 'compliance' | 'executive'>('security');
  const [dateRange, setDateRange] = useState('30days');
  const [assets, setAssets] = useState<any[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    const fetchAssets = async () => {
      if (!token) return;

      try {
        const res = await fetch(`${config.apiUrl}/api/assets`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (res.ok) {
          const data = await res.json();
          setAssets(data);
        }
      } catch (error) {
        console.error('Error fetching assets:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAssets();
  }, [token]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      if (reportType === 'security') {
        await generateSecurityReport();
      } else if (reportType === 'compliance') {
        await generateComplianceReport();
      } else {
        await generateExecutiveSummary();
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report. Please try again.');
    } finally {
      setGenerating(false);
      setShowGenerateModal(false);
    }
  };

  const generateSecurityReport = async () => {
    // Fetch findings for selected assets
    const assetsToReport = selectedAsset === 'all' ? assets : assets.filter(a => a.id === selectedAsset);

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    let yPos = 20;

    // Header
    doc.setFillColor(0, 71, 171);
    doc.rect(0, 0, pageWidth, 35, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('AFRICA CYBER TRUST', pageWidth / 2, 15, { align: 'center' });
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Security Assessment Report', pageWidth / 2, 25, { align: 'center' });

    yPos = 45;

    // Add logo below header on white background
    try {
      doc.addImage(LOGO_BASE64, 'PNG', pageWidth - 45, 38, 40, 28);
    } catch (e) {
      console.error('[REPORT] Failed to add logo to PDF:', e);
    }

    // Report Info
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, yPos);
    yPos += 7;
    doc.text(`Report ID: ACT-${Date.now().toString().slice(-8)}`, 14, yPos);
    yPos += 7;
    doc.text(`Date Range: ${dateRange === '7days' ? 'Last 7 Days' : dateRange === '30days' ? 'Last 30 Days' : 'Last 90 Days'}`, 14, yPos);
    yPos += 15;

    // Loop through each asset
    for (const asset of assetsToReport) {
      if (yPos > pageHeight - 60) {
        doc.addPage();
        yPos = 20;
      }

      // Asset Info
      doc.setFontSize(16);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(0, 71, 171);
      doc.text(`Asset: ${asset.name}`, 14, yPos);
      yPos += 10;

      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(0, 0, 0);
      doc.text(`Domain/URL: ${asset.value}`, 14, yPos);
      yPos += 7;
      doc.text(`Security Score: ${asset.security_score || 0}/100`, 14, yPos);
      yPos += 7;
      doc.text(`Findings: ${asset.findings_count || 0}`, 14, yPos);
      yPos += 15;

      // Fetch findings for this asset
      try {
        const findingsRes = await fetch(`${config.apiUrl}/api/scans/assets/${asset.id}/findings`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (findingsRes.ok) {
          const findings = await findingsRes.json();

          if (findings.length > 0) {
            // Findings table
            const findingsData = findings.map((f: any) => [
              f.severity.toUpperCase(),
              f.title,
              f.description,
              f.recommendation ? f.recommendation.substring(0, 100) + '...' : 'Review and address'
            ]);

            autoTable(doc, {
              startY: yPos,
              head: [['Severity', 'Issue', 'Problem', 'Recommendation']],
              body: findingsData,
              theme: 'striped',
              headStyles: { fillColor: [0, 71, 171], textColor: 255, fontStyle: 'bold' },
              columnStyles: {
                0: { cellWidth: 20, fontStyle: 'bold' },
                1: { cellWidth: 38 },
                2: { cellWidth: 53 },
                3: { cellWidth: 63 }
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
          } else {
            doc.text('No findings detected for this asset.', 14, yPos);
            yPos += 15;
          }
        }
      } catch (error) {
        console.error('Error fetching findings:', error);
      }
    }

    // Footer
    const totalPages = doc.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      doc.text(
        `Africa Cyber Trust - Security Report | Page ${i} of ${totalPages}`,
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      );
    }

    doc.save(`ACT_Security_Report_${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const generateComplianceReport = async () => {
    const assetsToReport = selectedAsset === 'all' ? assets : assets.filter(a => a.id === selectedAsset);

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    let yPos = 20;

    // Header
    doc.setFillColor(0, 71, 171);
    doc.rect(0, 0, pageWidth, 35, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('AFRICA CYBER TRUST', pageWidth / 2, 15, { align: 'center' });
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Compliance Report', pageWidth / 2, 25, { align: 'center' });

    yPos = 45;

    // Report Info
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, yPos);
    yPos += 7;
    doc.text(`Report ID: ACT-COMP-${Date.now().toString().slice(-8)}`, 14, yPos);
    yPos += 15;

    // Executive Summary
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Executive Summary', 14, yPos);
    yPos += 10;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);

    const avgScore = assets.length > 0 ? Math.round(assets.reduce((sum, a) => sum + (a.security_score || 0), 0) / assets.length) : 0;
    const totalFindings = assets.reduce((sum, a) => sum + (a.findings_count || 0), 0);

    doc.text(`Total Assets Assessed: ${assetsToReport.length}`, 14, yPos);
    yPos += 7;
    doc.text(`Average Security Score: ${avgScore}/100`, 14, yPos);
    yPos += 7;
    doc.text(`Total Security Findings: ${totalFindings}`, 14, yPos);
    yPos += 15;

    // Compliance Standards
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Compliance Standards', 14, yPos);
    yPos += 10;

    const complianceStandards = [
      { name: 'ISO 27001', status: avgScore >= 80 ? 'PASS' : 'FAIL', requirements: ['Security Headers', 'SSL/TLS', 'Access Control'], met: avgScore >= 80 ? 3 : 1 },
      { name: 'PCI DSS', status: avgScore >= 75 ? 'PASS' : 'FAIL', requirements: ['Encryption', 'Vulnerability Management', 'Access Restrictions'], met: avgScore >= 75 ? 3 : 2 },
      { name: 'GDPR', status: avgScore >= 70 ? 'PASS' : 'FAIL', requirements: ['Data Protection', 'Secure Transmission', 'Access Logging'], met: avgScore >= 70 ? 3 : 2 },
      { name: 'NIST CSF', status: avgScore >= 65 ? 'PASS' : 'FAIL', requirements: ['Identify', 'Protect', 'Detect'], met: avgScore >= 65 ? 3 : 1 }
    ];

    const complianceData = complianceStandards.map(std => [
      std.name,
      std.status,
      `${std.met}/${std.requirements.length}`,
      std.requirements.join(', ')
    ]);

    autoTable(doc, {
      startY: yPos,
      head: [['Standard', 'Status', 'Requirements Met', 'Key Requirements']],
      body: complianceData,
      theme: 'grid',
      headStyles: { fillColor: [0, 71, 171], textColor: 255 },
      columnStyles: {
        0: { cellWidth: 35 },
        1: { cellWidth: 25, fontStyle: 'bold' },
        2: { cellWidth: 35 },
        3: { cellWidth: 85 }
      },
      styles: { fontSize: 10 },
      didParseCell: function(data: any) {
        if (data.section === 'body' && data.column.index === 1) {
          if (data.cell.raw === 'PASS') {
            data.cell.styles.textColor = [16, 185, 129];
          } else {
            data.cell.styles.textColor = [239, 68, 68];
          }
        }
      }
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;

    // Recommendations
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Recommendations', 14, yPos);
    yPos += 10;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);

    const recommendations = [
      '1. Implement missing security headers to improve ISO 27001 compliance',
      '2. Enable HSTS and strengthen SSL/TLS configuration for PCI DSS',
      '3. Add SPF/DMARC records for email security and GDPR compliance',
      '4. Regular security assessments every 90 days',
      '5. Maintain detailed audit logs for compliance verification'
    ];

    recommendations.forEach(rec => {
      doc.text(rec, 14, yPos);
      yPos += 7;
    });

    // Footer
    doc.setFontSize(8);
    doc.setTextColor(128, 128, 128);
    doc.text(
      `Africa Cyber Trust - Compliance Report | Page 1 of 1`,
      pageWidth / 2,
      pageHeight - 10,
      { align: 'center' }
    );

    doc.save(`ACT_Compliance_Report_${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const generateExecutiveSummary = async () => {
    const assetsToReport = selectedAsset === 'all' ? assets : assets.filter(a => a.id === selectedAsset);

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    let yPos = 20;

    // Header
    doc.setFillColor(0, 71, 171);
    doc.rect(0, 0, pageWidth, 35, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('AFRICA CYBER TRUST', pageWidth / 2, 15, { align: 'center' });
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Executive Summary', pageWidth / 2, 25, { align: 'center' });

    yPos = 45;

    // Report Info
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, yPos);
    yPos += 7;
    doc.text(`Report Period: ${dateRange === '7days' ? 'Last 7 Days' : dateRange === '30days' ? 'Last 30 Days' : 'Last 90 Days'}`, 14, yPos);
    yPos += 15;

    // Key Metrics
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Security Posture Overview', 14, yPos);
    yPos += 12;

    const avgScore = assets.length > 0 ? Math.round(assets.reduce((sum, a) => sum + (a.security_score || 0), 0) / assets.length) : 0;
    const totalFindings = assets.reduce((sum, a) => sum + (a.findings_count || 0), 0);

    // Draw score card
    doc.setFillColor(avgScore >= 80 ? 16 : avgScore >= 60 ? 245 : 239, avgScore >= 80 ? 185 : avgScore >= 60 ? 158 : 68, avgScore >= 80 ? 129 : avgScore >= 60 ? 11 : 68);
    doc.roundedRect(14, yPos - 5, 60, 30, 3, 3, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text(`${avgScore}/100`, 44, yPos + 12, { align: 'center' });
    doc.setFontSize(10);
    doc.text('Security Score', 44, yPos + 20, { align: 'center' });

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text(`Total Assets: ${assetsToReport.length}`, 80, yPos + 5);
    doc.text(`Security Findings: ${totalFindings}`, 80, yPos + 15);
    doc.text(`Scanned Assets: ${assetsToReport.filter(a => a.security_score).length}`, 80, yPos + 25);

    yPos += 40;

    // Risk Summary
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Risk Summary', 14, yPos);
    yPos += 10;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);

    let riskLevel = 'LOW';
    let riskColor = [16, 185, 129];
    if (avgScore < 60) {
      riskLevel = 'HIGH';
      riskColor = [239, 68, 68];
    } else if (avgScore < 80) {
      riskLevel = 'MEDIUM';
      riskColor = [245, 158, 11];
    }

    doc.setTextColor(riskColor[0], riskColor[1], riskColor[2]);
    doc.setFont('helvetica', 'bold');
    doc.text(`Overall Risk Level: ${riskLevel}`, 14, yPos);
    yPos += 10;

    doc.setTextColor(0, 0, 0);
    doc.setFont('helvetica', 'normal');

    const riskDescription = avgScore >= 80
      ? 'Your organization maintains a strong security posture with minimal vulnerabilities.'
      : avgScore >= 60
      ? 'Your organization has a moderate security posture. Address medium and high-severity findings to improve.'
      : 'Your organization has critical security gaps that require immediate attention.';

    const splitText = doc.splitTextToSize(riskDescription, 180);
    doc.text(splitText, 14, yPos);
    yPos += splitText.length * 7 + 10;

    // Key Findings
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Key Findings', 14, yPos);
    yPos += 10;

    const keyFindings = [
      `${totalFindings} total security findings across ${assetsToReport.length} assets`,
      `Average security score: ${avgScore}/100`,
      avgScore < 70 ? 'Critical: Missing essential security headers' : 'Security headers properly configured',
      'SSL/TLS certificates valid and up to date',
      avgScore < 80 ? 'Recommendation: Implement HSTS and strengthen cipher suites' : 'Strong encryption protocols in place'
    ];

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);

    keyFindings.forEach(finding => {
      doc.text(`• ${finding}`, 14, yPos);
      yPos += 7;
    });

    yPos += 10;

    // Immediate Actions
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(0, 71, 171);
    doc.text('Recommended Actions', 14, yPos);
    yPos += 10;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(0, 0, 0);

    const actions = avgScore >= 80
      ? [
          '1. Maintain current security posture with quarterly reviews',
          '2. Continue monitoring for new vulnerabilities',
          '3. Update security policies as needed'
        ]
      : avgScore >= 60
      ? [
          '1. Address all high-severity findings within 7 days',
          '2. Implement missing security headers',
          '3. Schedule monthly security assessments',
          '4. Review and update access controls'
        ]
      : [
          '1. URGENT: Address critical security gaps immediately',
          '2. Enable HSTS and fix SSL/TLS configuration',
          '3. Implement comprehensive security headers',
          '4. Conduct full security audit',
          '5. Establish weekly security review meetings'
        ];

    actions.forEach(action => {
      doc.text(action, 14, yPos);
      yPos += 7;
    });

    // Footer
    doc.setFontSize(8);
    doc.setTextColor(128, 128, 128);
    doc.text(
      `Africa Cyber Trust - Executive Summary | Confidential`,
      pageWidth / 2,
      pageHeight - 10,
      { align: 'center' }
    );

    doc.save(`ACT_Executive_Summary_${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const reportTypes = [
    {
      id: 'security',
      name: 'Security Report',
      description: 'Detailed technical security assessment with findings and recommendations',
      icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z'
    },
    {
      id: 'compliance',
      name: 'Compliance Report',
      description: 'Compliance status report for regulatory requirements and standards',
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    {
      id: 'executive',
      name: 'Executive Summary',
      description: 'High-level overview for executives and stakeholders',
      icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
    }
  ];

  return (
    <DashboardLayout title="Reports" subtitle="Generate and download security reports">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="cyber-card p-6">
          <div className="text-3xl font-bold text-white mb-1">{assets.length}</div>
          <div className="text-sm text-cyber-muted">Total Assets</div>
        </div>
        <div className="cyber-card p-6">
          <div className="text-3xl font-bold" style={{ color: BLUE }}>{assets.filter(a => a.security_score).length}</div>
          <div className="text-sm text-cyber-muted">Scanned Assets</div>
        </div>
        <div className="cyber-card p-6">
          <div className="text-3xl font-bold" style={{ color: GOLD }}>
            {assets.length > 0 ? Math.round(assets.reduce((sum, a) => sum + (a.security_score || 0), 0) / assets.length) : 0}
          </div>
          <div className="text-sm text-cyber-muted">Avg Score</div>
        </div>
        <div className="cyber-card p-6">
          <div className="text-3xl font-bold text-green-400">{assets.reduce((sum, a) => sum + (a.findings_count || 0), 0)}</div>
          <div className="text-sm text-cyber-muted">Total Findings</div>
        </div>
      </div>

      {/* Generate Report Button */}
      <div className="mb-8">
        <button
          onClick={() => setShowGenerateModal(true)}
          className="px-6 py-3 rounded-xl font-semibold text-white transition-opacity hover:opacity-90"
          style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
        >
          + Generate New Report
        </button>
      </div>

      {/* Report Types */}
      <div className="grid md:grid-cols-3 gap-6">
        {reportTypes.map((report) => (
          <div key={report.id} className="cyber-card-raised p-6 hover:cyber-glow-blue transition-all">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{ background: `${BLUE}20` }}>
              <svg className="w-6 h-6" style={{ color: BLUE }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={report.icon} />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{report.name}</h3>
            <p className="text-sm text-cyber-muted">{report.description}</p>
          </div>
        ))}
      </div>

      {/* Generate Report Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setShowGenerateModal(false)}>
          <div className="cyber-card-raised max-w-2xl w-full p-8" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Generate Report</h2>
              <button
                onClick={() => setShowGenerateModal(false)}
                className="text-cyber-muted hover:text-white text-3xl font-light"
              >
                ×
              </button>
            </div>

            <div className="space-y-6">
              {/* Report Type */}
              <div>
                <label className="block text-sm font-semibold text-white mb-3">Report Type</label>
                <div className="space-y-2">
                  {reportTypes.map((report) => (
                    <div
                      key={report.id}
                      onClick={() => setReportType(report.id as any)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        reportType === report.id
                          ? 'border-blue-500 bg-blue-500/10'
                          : 'border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <div className="font-semibold text-white">{report.name}</div>
                      <div className="text-sm text-cyber-muted">{report.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Asset Selection */}
              <div>
                <label className="block text-sm font-semibold text-white mb-3">Select Asset</label>
                <select
                  value={selectedAsset}
                  onChange={(e) => setSelectedAsset(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-slate-800 border border-slate-700 text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="all">All Assets</option>
                  {assets.map((asset) => (
                    <option key={asset.id} value={asset.id}>{asset.name}</option>
                  ))}
                </select>
              </div>

              {/* Date Range */}
              <div>
                <label className="block text-sm font-semibold text-white mb-3">Date Range</label>
                <div className="grid grid-cols-3 gap-3">
                  {['7days', '30days', '90days'].map((range) => (
                    <button
                      key={range}
                      onClick={() => setDateRange(range)}
                      className={`px-4 py-3 rounded-lg font-semibold transition-all ${
                        dateRange === range
                          ? 'text-white'
                          : 'bg-slate-800 text-cyber-muted hover:text-white'
                      }`}
                      style={dateRange === range ? { background: BLUE } : {}}
                    >
                      {range === '7days' ? '7 Days' : range === '30days' ? '30 Days' : '90 Days'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerateReport}
                disabled={generating}
                className="w-full px-6 py-4 rounded-xl font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                style={{ background: `linear-gradient(135deg, ${BLUE} 0%, #1E90FF 100%)` }}
              >
                {generating ? 'Generating PDF...' : 'Generate Report (PDF)'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 cyber-card p-6">
        <div className="flex items-start gap-4">
          <svg className="w-6 h-6 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h4 className="font-semibold text-white mb-2">About Reports</h4>
            <p className="text-sm text-cyber-muted leading-relaxed">
              Reports are generated from your security scan data and include vulnerability findings,
              security scores, and recommendations. PDF reports can be shared with stakeholders and
              compliance teams.
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
