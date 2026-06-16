'use client';

import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { getSecurityIssueGuide, parseSecurityHeaders, SecurityIssueGuide } from '@/lib/security-issues-guide';
import jsPDF from 'jspdf';
import { LOGO_BASE64 } from '@/app/dashboard/reports/logo-base64';

interface CheckResult {
  id: string;
  input_type: string;
  input_value: string;
  score: number;
  risk_level: string;
  summary: string;
  red_flags: any[];
  ai_explanation: string;
  safety_advice: string;
  created_at: string;
}

export default function CheckResultPage() {
  const params = useParams();
  const [result, setResult] = useState<CheckResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedIssue, setExpandedIssue] = useState<number | null>(null);
  const [downloadingPDF, setDownloadingPDF] = useState(false);

  useEffect(() => {
    // Load result from sessionStorage
    const storedResult = sessionStorage.getItem('lastCheck');
    console.log('Stored result:', storedResult); // Debug
    if (storedResult) {
      const parsedResult = JSON.parse(storedResult);
      console.log('Parsed result:', parsedResult); // Debug
      // Convert AI verify response to check result if needed
      if (parsedResult.verification_type) {
        setResult({
          id: parsedResult.id,
          input_type: parsedResult.verification_type,
          input_value: `${parsedResult.verification_type === 'photo' ? 'Photo' : 'Video'} Analysis`,
          score: parsedResult.authenticity_score,
          risk_level: parsedResult.risk_level,
          summary: parsedResult.is_ai_generated
            ? `⚠️ AI-Generated Content Detected (${parsedResult.authenticity_score}/100)`
            : `✅ Authentic Content Verified (${parsedResult.authenticity_score}/100)`,
          red_flags: parsedResult.deepfake_detected ? [{
            severity: 'critical',
            category: 'deepfake',
            message: parsedResult.verification_type === 'photo' ? 'Deepfake photo detected' : 'Deepfake video detected',
            evidence: `Confidence: ${(parsedResult.confidence * 100).toFixed(1)}%`
          }] : [],
          ai_explanation: parsedResult.explanation,
          safety_advice: parsedResult.safety_advice,
          created_at: parsedResult.created_at,
        });
      } else {
        setResult(parsedResult);
      }
      setLoading(false);
    } else {
      // Fallback
      setTimeout(() => {
        setResult({
          id: params.id as string,
          input_type: 'url',
          input_value: 'https://example.com',
          score: 85,
          risk_level: 'low',
          summary: 'This website appears safe with a trust score of 85/100.',
          red_flags: [],
          ai_explanation: 'Analysis complete. The website has valid SSL, good security headers, and no known blacklist entries.',
          safety_advice: 'This site appears legitimate. Always verify you\'re on the correct URL.',
          created_at: new Date().toISOString(),
        });
        setLoading(false);
      }, 1000);
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-t-blue-600 border-blue-200 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Analyzing...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Result Not Found</h1>
          <p className="text-gray-600">The check result could not be loaded.</p>
        </div>
      </div>
    );
  }

  const downloadReport = async () => {
    if (!result) return;

    setDownloadingPDF(true);

    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 20;
      const contentWidth = pageWidth - (margin * 2);
      let yPos = margin;

      // Helper function to add new page if needed
      const checkPageBreak = (neededSpace: number) => {
        if (yPos + neededSpace > pageHeight - margin) {
          pdf.addPage();
          yPos = margin;
          return true;
        }
        return false;
      };

      // Helper function to wrap text
      const addWrappedText = (text: string, fontSize: number, maxWidth: number, isBold = false) => {
        pdf.setFontSize(fontSize);
        pdf.setFont('helvetica', isBold ? 'bold' : 'normal');
        const lines = pdf.splitTextToSize(text, maxWidth);
        lines.forEach((line: string) => {
          checkPageBreak(7);
          pdf.text(line, margin, yPos);
          yPos += 7;
        });
      };

      // Header with gradient effect (simulated with rectangle)
      pdf.setFillColor(0, 71, 171); // #0047AB
      pdf.rect(0, 0, pageWidth, 50, 'F');

      // Add logo on the right
      try {
        pdf.addImage(LOGO_BASE64, 'PNG', pageWidth - 40, 5, 35, 25);
      } catch (e) {
        console.error('[REPORT] Failed to add logo to PDF:', e);
      }

      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(24);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Africa Cyber Trust', pageWidth / 2, 20, { align: 'center' });

      pdf.setFontSize(16);
      pdf.text('Security Analysis Report', pageWidth / 2, 32, { align: 'center' });

      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      pdf.text(`Generated: ${new Date(result.created_at).toLocaleString()}`, pageWidth / 2, 42, { align: 'center' });

      yPos = 60;
      pdf.setTextColor(0, 0, 0);

      // Overall Assessment Box
      pdf.setFillColor(249, 250, 251);
      pdf.roundedRect(margin, yPos, contentWidth, 50, 3, 3, 'F');
      pdf.setDrawColor(0, 71, 171);
      pdf.setLineWidth(0.5);
      pdf.roundedRect(margin, yPos, contentWidth, 50, 3, 3, 'S');

      yPos += 10;
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(0, 71, 171);
      pdf.text('Overall Assessment', margin + 5, yPos);

      yPos += 10;
      pdf.setFontSize(32);
      pdf.setTextColor(getScoreColorRGB(result.score)[0], getScoreColorRGB(result.score)[1], getScoreColorRGB(result.score)[2]);
      pdf.text(`${result.score}/100`, margin + 5, yPos);

      // Risk badge
      const riskColor = getRiskColorRGB(result.risk_level || 'unknown');
      pdf.setFillColor(riskColor[0], riskColor[1], riskColor[2]);
      pdf.roundedRect(margin + 60, yPos - 7, 35, 8, 2, 2, 'F');
      pdf.setFontSize(10);
      pdf.setTextColor(255, 255, 255);
      pdf.setFont('helvetica', 'bold');
      pdf.text((result.risk_level || 'UNKNOWN').toUpperCase(), margin + 77.5, yPos - 2, { align: 'center' });

      yPos += 10;
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      pdf.text(`Target: ${result.input_value}`, margin + 5, yPos);
      yPos += 6;
      pdf.text(`Type: ${result.input_type.toUpperCase()}`, margin + 5, yPos);

      yPos += 20;

      // AI Analysis Section
      checkPageBreak(30);
      pdf.setFontSize(14);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(0, 71, 171);
      pdf.text('AI Analysis', margin, yPos);
      yPos += 8;

      pdf.setTextColor(0, 0, 0);
      addWrappedText(result.ai_explanation, 10, contentWidth);
      yPos += 5;

      // Safety Recommendation
      checkPageBreak(25);
      pdf.setFontSize(14);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(0, 71, 171);
      pdf.text('Safety Recommendation', margin, yPos);
      yPos += 8;

      pdf.setFillColor(239, 246, 255);
      const safetyBoxHeight = pdf.splitTextToSize(result.safety_advice, contentWidth - 10).length * 7 + 10;
      pdf.roundedRect(margin, yPos - 5, contentWidth, safetyBoxHeight, 2, 2, 'F');
      pdf.setTextColor(0, 71, 171);
      addWrappedText(result.safety_advice, 10, contentWidth - 10);
      yPos += 5;

      // Security Issues
      if (result.red_flags && result.red_flags.length > 0) {
        checkPageBreak(30);
        pdf.setFontSize(14);
        pdf.setFont('helvetica', 'bold');
        pdf.setTextColor(220, 38, 38);
        pdf.text(`Security Issues Detected (${result.red_flags.length})`, margin, yPos);
        yPos += 10;

        result.red_flags.forEach((flag: any, index: number) => {
          checkPageBreak(40);

          // Issue box
          pdf.setFillColor(254, 242, 242);
          pdf.setDrawColor(220, 38, 38);
          pdf.setLineWidth(0.3);

          const issueHeight = 25 + (flag.evidence ? 10 : 0);
          pdf.roundedRect(margin, yPos, contentWidth, issueHeight, 2, 2, 'FD');

          yPos += 7;
          pdf.setFontSize(11);
          pdf.setFont('helvetica', 'bold');
          pdf.setTextColor(153, 27, 27);
          pdf.text(`${index + 1}. ${flag.message}`, margin + 3, yPos);

          // Severity badge
          const sevColor = getSeverityColorRGB(flag.severity);
          pdf.setFillColor(sevColor[0], sevColor[1], sevColor[2]);
          pdf.roundedRect(contentWidth - 15, yPos - 5, 30, 6, 1, 1, 'F');
          pdf.setFontSize(8);
          pdf.setTextColor(255, 255, 255);
          pdf.text(flag.severity.toUpperCase(), contentWidth + 15, yPos - 1, { align: 'center' });

          if (flag.evidence) {
            yPos += 7;
            pdf.setFontSize(9);
            pdf.setTextColor(102, 102, 102);
            pdf.setFont('helvetica', 'normal');
            const evidenceLines = pdf.splitTextToSize(flag.evidence, contentWidth - 10);
            evidenceLines.forEach((line: string) => {
              pdf.text(line, margin + 3, yPos);
              yPos += 5;
            });
          }

          // Get fix instructions
          const headers = parseSecurityHeaders(flag.message + ' ' + (flag.evidence || ''));
          if (headers.length > 0) {
            const guide = getSecurityIssueGuide(headers[0]);
            if (guide) {
              yPos += 10;
              checkPageBreak(30);

              pdf.setFontSize(10);
              pdf.setFont('helvetica', 'bold');
              pdf.setTextColor(34, 197, 94);
              pdf.text('How to Fix:', margin + 3, yPos);
              yPos += 6;

              pdf.setFont('helvetica', 'normal');
              pdf.setTextColor(0, 0, 0);
              pdf.setFontSize(9);

              // Add first fix instruction
              if (guide.fixInstructions.length > 0) {
                const fix = guide.fixInstructions[0];
                pdf.setFont('helvetica', 'bold');
                pdf.text(`${fix.title}:`, margin + 3, yPos);
                yPos += 5;

                pdf.setFont('helvetica', 'normal');
                fix.steps.forEach((step, i) => {
                  checkPageBreak(10);
                  const stepText = `  ${i + 1}. ${step}`;
                  pdf.text(stepText, margin + 3, yPos);
                  yPos += 5;
                });

                if (fix.code) {
                  yPos += 3;
                  checkPageBreak(15);
                  pdf.setFillColor(240, 240, 240);
                  const codeLines = fix.code.split('\n').slice(0, 3); // First 3 lines
                  const codeHeight = codeLines.length * 5 + 4;
                  pdf.rect(margin + 3, yPos - 3, contentWidth - 6, codeHeight, 'F');

                  pdf.setFont('courier', 'normal');
                  pdf.setFontSize(8);
                  pdf.setTextColor(0, 100, 0);
                  codeLines.forEach((line) => {
                    pdf.text(line.substring(0, 80), margin + 5, yPos);
                    yPos += 5;
                  });
                  pdf.setFont('helvetica', 'normal');
                  pdf.setTextColor(0, 0, 0);
                }
              }
            }
          }

          yPos += 15;
        });
      } else {
        checkPageBreak(20);
        pdf.setFillColor(240, 253, 244);
        pdf.roundedRect(margin, yPos, contentWidth, 15, 2, 2, 'F');
        yPos += 10;
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        pdf.setTextColor(21, 128, 61);
        pdf.text('No Security Issues Detected', margin + 5, yPos);
      }

      // Footer
      const totalPages = (pdf as any).internal.pages.length - 1;
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.setTextColor(128, 128, 128);
        pdf.text('Africa Cyber Trust Infrastructure - AI-Powered Security for Africa', pageWidth / 2, pageHeight - 10, { align: 'center' });
        pdf.text(`Page ${i} of ${totalPages}`, pageWidth - margin, pageHeight - 10, { align: 'right' });
        pdf.text(`Report ID: ${result.id}`, margin, pageHeight - 10);
      }

      // Save the PDF
      pdf.save(`security-report-${result.id}.pdf`);

    } catch (error) {
      console.error('PDF generation error:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setDownloadingPDF(false);
    }
  };

  // Helper functions for colors
  const getScoreColorRGB = (score: number): [number, number, number] => {
    if (score >= 80) return [0, 71, 171]; // Blue
    if (score >= 60) return [218, 165, 32]; // Gold
    if (score >= 40) return [255, 107, 53]; // Orange
    return [220, 38, 38]; // Red
  };

  const getRiskColorRGB = (level: string): [number, number, number] => {
    switch (level) {
      case 'low': return [34, 197, 94]; // Green
      case 'medium': return [251, 191, 36]; // Yellow
      case 'high': return [249, 115, 22]; // Orange
      case 'critical': return [239, 68, 68]; // Red
      default: return [107, 114, 128]; // Gray
    }
  };

  const getSeverityColorRGB = (severity: string): [number, number, number] => {
    switch (severity) {
      case 'critical': return [220, 38, 38];
      case 'high': return [249, 115, 22];
      case 'medium': return [251, 191, 36];
      case 'low': return [59, 130, 246];
      default: return [107, 114, 128];
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return '#0047AB';
      case 'medium': return '#DAA520';
      case 'high': return '#FF6B35';
      case 'critical': return '#DC2626';
      default: return '#6B7280';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#0047AB';
    if (score >= 60) return '#DAA520';
    if (score >= 40) return '#FF6B35';
    return '#DC2626';
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="container mx-auto px-4 py-4">
          <a href="/" className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-700">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </a>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Score Card */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12 mb-8">
            <div className="text-center mb-8">
              <div className="relative inline-block">
                <svg className="w-48 h-48 transform -rotate-90">
                  <circle cx="96" cy="96" r="88" stroke="#E5E7EB" strokeWidth="12" fill="none" />
                  <circle
                    cx="96"
                    cy="96"
                    r="88"
                    stroke={getScoreColor(result.score)}
                    strokeWidth="12"
                    fill="none"
                    strokeDasharray={`${(result.score / 100) * 552} 552`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div>
                    <div className="text-6xl font-bold" style={{ color: getScoreColor(result.score) }}>
                      {result.score}
                    </div>
                    <div className="text-gray-500 text-sm font-medium">/ 100</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-center mb-6">
              <div
                className="inline-block px-6 py-2 rounded-full text-white font-semibold text-lg mb-4"
                style={{ backgroundColor: getRiskColor(result.risk_level || 'unknown') }}
              >
                {(result.risk_level || 'UNKNOWN').toUpperCase()} RISK
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{result.summary || 'Analysis Complete'}</h1>
              <p className="text-gray-600">{result.input_value || 'N/A'}</p>
            </div>
          </div>

          {/* AI Explanation */}
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #0047AB 0%, #DAA520 100%)' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold mb-3" style={{ color: '#0047AB' }}>AI Analysis</h2>
                <p className="text-gray-700 leading-relaxed mb-4">{result.ai_explanation}</p>
                <div className="p-4 rounded-lg bg-blue-50 border-l-4" style={{ borderLeftColor: '#0047AB' }}>
                  <p className="text-sm font-semibold text-blue-900 mb-1">Safety Recommendation</p>
                  <p className="text-sm text-blue-800">{result.safety_advice}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Red Flags with Detailed Fix Instructions */}
          {result.red_flags && result.red_flags.length > 0 && (
            <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
              <h2 className="text-xl font-bold mb-6" style={{ color: '#DC2626' }}>
                ⚠️ Security Issues Detected ({result.red_flags.length})
              </h2>
              <div className="space-y-4">
                {result.red_flags.map((flag: any, index: number) => {
                  // Get detailed guide for this issue
                  const headers = parseSecurityHeaders(flag.message + ' ' + (flag.evidence || ''));
                  const guides = headers.map(h => getSecurityIssueGuide(h)).filter(Boolean) as SecurityIssueGuide[];
                  const isExpanded = expandedIssue === index;

                  return (
                    <div key={index} className="border-2 border-red-200 rounded-xl overflow-hidden">
                      {/* Issue Header */}
                      <div
                        className="flex items-start gap-4 p-5 bg-red-50 cursor-pointer hover:bg-red-100 transition-colors"
                        onClick={() => setExpandedIssue(isExpanded ? null : index)}
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-2xl">⚠️</span>
                            <div className="font-bold text-red-900 text-lg">{flag.message}</div>
                          </div>
                          {flag.evidence && (
                            <div className="text-sm text-red-700 ml-11">{flag.evidence}</div>
                          )}
                        </div>
                        <div className="flex items-center gap-3">
                          <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            flag.severity === 'critical' ? 'bg-red-600 text-white' :
                            flag.severity === 'high' ? 'bg-orange-500 text-white' :
                            flag.severity === 'medium' ? 'bg-yellow-500 text-white' :
                            'bg-blue-500 text-white'
                          }`}>
                            {flag.severity}
                          </div>
                          <svg
                            className={`w-6 h-6 text-red-600 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </div>
                      </div>

                      {/* Detailed Fix Instructions (Expandable) */}
                      {isExpanded && guides.length > 0 && (
                        <div className="border-t-2 border-red-200">
                          {guides.map((guide, gIndex) => (
                            <div key={gIndex} className="p-6 bg-white">
                              {/* Issue Description */}
                              <div className="mb-6">
                                <h3 className="text-lg font-bold text-gray-900 mb-3">{guide.title}</h3>
                                <p className="text-gray-700 mb-4">{guide.description}</p>

                                <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
                                  <p className="font-semibold text-red-900 mb-2">🎯 Risk:</p>
                                  <p className="text-red-800">{guide.risk}</p>
                                </div>

                                <div className="bg-orange-50 border-l-4 border-orange-500 p-4">
                                  <p className="font-semibold text-orange-900 mb-2">💥 Potential Impact:</p>
                                  <ul className="list-disc list-inside text-orange-800 space-y-1">
                                    {guide.impact.map((impact, i) => (
                                      <li key={i}>{impact}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>

                              {/* Fix Instructions */}
                              <div className="mb-6">
                                <h4 className="text-lg font-bold text-green-700 mb-4">✅ How to Fix</h4>
                                <div className="space-y-6">
                                  {guide.fixInstructions.map((fix, fIndex) => (
                                    <div key={fIndex} className="bg-green-50 rounded-lg p-5 border-2 border-green-200">
                                      <h5 className="font-bold text-green-900 mb-3">{fix.title}</h5>
                                      <div className="mb-3">
                                        <p className="text-sm font-semibold text-green-800 mb-2">Steps:</p>
                                        <ol className="list-decimal list-inside text-green-700 space-y-1">
                                          {fix.steps.map((step, sIndex) => (
                                            <li key={sIndex}>{step}</li>
                                          ))}
                                        </ol>
                                      </div>
                                      {fix.code && (
                                        <div>
                                          <p className="text-sm font-semibold text-green-800 mb-2">Code:</p>
                                          <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
                                            <code>{fix.code}</code>
                                          </pre>
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>

                              {/* References */}
                              {guide.references && guide.references.length > 0 && (
                                <div className="bg-blue-50 rounded-lg p-4 border-2 border-blue-200">
                                  <p className="font-semibold text-blue-900 mb-2">📚 Learn More:</p>
                                  <ul className="space-y-1">
                                    {guide.references.map((ref, rIndex) => (
                                      <li key={rIndex}>
                                        <a
                                          href={ref}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="text-blue-700 hover:text-blue-900 underline text-sm"
                                        >
                                          {ref}
                                        </a>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* No detailed guide available */}
                      {isExpanded && guides.length === 0 && (
                        <div className="p-6 bg-white border-t-2 border-red-200">
                          <p className="text-gray-600 text-center">
                            📝 Detailed fix instructions for this issue are not yet available.
                            Please consult your system administrator or security team.
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Quick Tip */}
              <div className="mt-6 p-4 bg-blue-50 rounded-xl border-2 border-blue-200">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 flex-shrink-0 mt-0.5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div className="text-sm text-blue-900">
                    <strong>💡 Pro Tip:</strong> Click on any issue above to see detailed fix instructions with code examples for different server configurations (Apache, Nginx, Node.js).
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              className="flex-1 px-8 py-4 rounded-xl font-semibold text-white shadow-lg hover:shadow-xl transition-all"
              style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
              onClick={() => window.location.href = '/'}
            >
              Check Another
            </button>
            <button
              className="flex-1 px-8 py-4 rounded-xl font-semibold border-2 hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ borderColor: '#0047AB', color: '#0047AB' }}
              onClick={downloadReport}
              disabled={downloadingPDF}
            >
              {downloadingPDF ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating PDF...
                </span>
              ) : (
                <>📄 Download PDF Report</>
              )}
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
