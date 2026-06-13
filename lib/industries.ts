// Shared industry configuration — single source of truth for industry-specific
// branding, compliance standards, security recommendations, finding priorities
// and risk weighting. Used by the registration form, dashboard and assets pages.

export type IndustryId =
  | 'fintech'
  | 'ecommerce'
  | 'healthcare'
  | 'education'
  | 'government'
  | 'technology'
  | 'telecom'
  | 'media'
  | 'other';

export type RiskTier = 'high' | 'medium' | 'standard';

export interface ComplianceBadge {
  label: string;        // e.g. "PCI-DSS"
  full: string;         // e.g. "Payment Card Industry Data Security Standard"
}

export interface ComplianceFocus {
  label: string;        // dashboard compliance row label
  desc: string;         // short description of what it covers
}

export interface IndustryConfig {
  id: IndustryId;
  label: string;        // dropdown / display label
  icon: string;         // emoji used across UI
  /** Risk sensitivity tier — drives stricter scoring for sensitive industries. */
  riskTier: RiskTier;
  /**
   * Multiplier applied when penalising findings against the security score.
   * High-risk industries have lower tolerance (higher multiplier).
   */
  riskMultiplier: number;
  /** Compliance / regulatory badges relevant to the industry. */
  compliance: ComplianceBadge[];
  /** Industry-specific compliance focus areas shown on the dashboard. */
  focusAreas: ComplianceFocus[];
  /** Industry best-practice security recommendations. */
  recommendations: string[];
  /**
   * Finding categories (lowercased, matched as substrings) that are
   * especially relevant to this industry and should be surfaced first.
   */
  priorityCategories: string[];
}

export const INDUSTRIES: Record<IndustryId, IndustryConfig> = {
  fintech: {
    id: 'fintech',
    label: 'Fintech / Payment Services',
    icon: '💰',
    riskTier: 'high',
    riskMultiplier: 1.5,
    compliance: [
      { label: 'PCI-DSS', full: 'Payment Card Industry Data Security Standard' },
      { label: 'GDPR', full: 'General Data Protection Regulation' },
      { label: 'SOC 2', full: 'Service Organization Control 2' },
    ],
    focusAreas: [
      { label: 'PCI-DSS Compliance', desc: 'Cardholder data handling & storage controls' },
      { label: 'Payment API Security', desc: 'Authenticated, rate-limited payment endpoints' },
      { label: 'Financial Data Encryption', desc: 'Encryption at rest & in transit' },
      { label: 'Transaction Monitoring', desc: 'Anomaly & fraud detection alerts' },
    ],
    recommendations: [
      'Tokenize and never store raw card data (PCI-DSS Req. 3)',
      'Enforce TLS 1.2+ on every payment and API endpoint',
      'Require strong authentication & authorization on payment APIs',
      'Enable real-time transaction monitoring and fraud alerting',
      'Run quarterly authorized vulnerability scans (PCI-DSS Req. 11)',
    ],
    priorityCategories: ['auth', 'injection', 'tls', 'ssl', 'api', 'encryption', 'access', 'pci', 'payment', 'data'],
  },
  ecommerce: {
    id: 'ecommerce',
    label: 'E-commerce / Retail',
    icon: '🛒',
    riskTier: 'medium',
    riskMultiplier: 1.25,
    compliance: [
      { label: 'PCI-DSS', full: 'Payment Card Industry Data Security Standard' },
      { label: 'GDPR', full: 'General Data Protection Regulation' },
    ],
    focusAreas: [
      { label: 'Payment Gateway Security', desc: 'Secure checkout & gateway integration' },
      { label: 'Customer Data Protection', desc: 'PII storage & access controls' },
      { label: 'Shopping Cart Security', desc: 'Session integrity & price tampering defence' },
      { label: 'Transaction SSL/TLS', desc: 'Encrypted checkout end to end' },
    ],
    recommendations: [
      'Use a PCI-compliant payment gateway — avoid handling cards directly',
      'Enforce HTTPS site-wide with HSTS to protect checkout',
      'Protect against cart/price tampering and IDOR on order endpoints',
      'Minimize and encrypt stored customer PII',
      'Add bot/fraud protection on login and checkout flows',
    ],
    priorityCategories: ['tls', 'ssl', 'payment', 'session', 'auth', 'data', 'access', 'injection', 'api'],
  },
  healthcare: {
    id: 'healthcare',
    label: 'Healthcare',
    icon: '⚕️',
    riskTier: 'high',
    riskMultiplier: 1.5,
    compliance: [
      { label: 'HIPAA-Ready', full: 'Health Insurance Portability and Accountability Act' },
      { label: 'GDPR', full: 'General Data Protection Regulation' },
      { label: 'ISO 27001', full: 'Information Security Management' },
    ],
    focusAreas: [
      { label: 'Patient Data Protection', desc: 'PHI confidentiality & integrity' },
      { label: 'Medical Data Encryption', desc: 'Records encrypted at rest & in transit' },
      { label: 'Access Control Compliance', desc: 'Least-privilege, audited access to records' },
      { label: 'HIPAA-like Checklist', desc: 'Privacy & breach-notification readiness' },
    ],
    recommendations: [
      'Encrypt all patient health information (PHI) at rest and in transit',
      'Enforce role-based, least-privilege access to medical records',
      'Maintain immutable audit logs of every record access',
      'Implement automatic session timeout on clinical applications',
      'Have a documented breach-notification and incident plan',
    ],
    priorityCategories: ['access', 'encryption', 'auth', 'data', 'privacy', 'audit', 'tls', 'ssl', 'leak'],
  },
  education: {
    id: 'education',
    label: 'Education',
    icon: '🎓',
    riskTier: 'medium',
    riskMultiplier: 1.25,
    compliance: [
      { label: 'FERPA-like', full: 'Family Educational Rights and Privacy Act' },
      { label: 'GDPR', full: 'General Data Protection Regulation' },
    ],
    focusAreas: [
      { label: 'Student Data Protection', desc: 'Student records confidentiality' },
      { label: 'Access Control', desc: 'Role separation for staff/students' },
      { label: 'Data Encryption', desc: 'Records encrypted at rest & in transit' },
      { label: 'Privacy Compliance', desc: 'FERPA-like consent & retention' },
    ],
    recommendations: [
      'Protect student records with strict access controls (FERPA-like)',
      'Encrypt student PII at rest and in transit',
      'Separate staff, faculty and student permission roles',
      'Secure learning-platform logins with MFA where possible',
      'Define data-retention and consent policies for minors',
    ],
    priorityCategories: ['access', 'auth', 'data', 'privacy', 'encryption', 'session', 'tls', 'ssl'],
  },
  government: {
    id: 'government',
    label: 'Government',
    icon: '🏛️',
    riskTier: 'high',
    riskMultiplier: 1.6,
    compliance: [
      { label: 'ISO 27001', full: 'Information Security Management' },
      { label: 'GDPR', full: 'General Data Protection Regulation' },
      { label: 'Data Sovereignty', full: 'National data residency requirements' },
    ],
    focusAreas: [
      { label: 'Data Sovereignty', desc: 'Data residency & jurisdiction controls' },
      { label: 'High-Security Protocols', desc: 'Hardened configuration & crypto' },
      { label: 'Audit Trail Completeness', desc: 'Full, tamper-evident logging' },
      { label: 'Access Control Strictness', desc: 'Zero-trust, least-privilege access' },
    ],
    recommendations: [
      'Keep citizen data within required national/jurisdictional borders',
      'Enforce zero-trust, least-privilege access for all systems',
      'Maintain complete, tamper-evident audit trails',
      'Use strong, approved cryptography and disable legacy protocols',
      'Conduct regular authorized penetration testing',
    ],
    priorityCategories: ['access', 'auth', 'audit', 'encryption', 'tls', 'ssl', 'config', 'data', 'privacy', 'injection'],
  },
  technology: {
    id: 'technology',
    label: 'Technology / SaaS',
    icon: '💻',
    riskTier: 'medium',
    riskMultiplier: 1.2,
    compliance: [
      { label: 'SOC 2', full: 'Service Organization Control 2' },
      { label: 'GDPR', full: 'General Data Protection Regulation' },
      { label: 'ISO 27001', full: 'Information Security Management' },
    ],
    focusAreas: [
      { label: 'API Security', desc: 'OWASP API Top 10 coverage' },
      { label: 'Cloud Infrastructure', desc: 'Hardened cloud config & secrets' },
      { label: 'Authentication & SSO', desc: 'Strong auth, token & session handling' },
      { label: 'Dependency Security', desc: 'No known-vulnerable components' },
    ],
    recommendations: [
      'Secure APIs against the OWASP API Top 10 (auth, BOLA, rate limits)',
      'Manage secrets in a vault — never commit keys to source',
      'Harden cloud infrastructure config and enable logging',
      'Patch vulnerable dependencies continuously (SCA)',
      'Pursue SOC 2 controls for customer trust',
    ],
    priorityCategories: ['api', 'auth', 'config', 'injection', 'access', 'secret', 'dependency', 'tls', 'ssl'],
  },
  telecom: {
    id: 'telecom',
    label: 'Telecommunications',
    icon: '📡',
    riskTier: 'medium',
    riskMultiplier: 1.3,
    compliance: [
      { label: 'ISO 27001', full: 'Information Security Management' },
      { label: 'GDPR', full: 'General Data Protection Regulation' },
    ],
    focusAreas: [
      { label: 'Network Security', desc: 'Infrastructure & perimeter hardening' },
      { label: 'Subscriber Data Protection', desc: 'Subscriber PII & CDR confidentiality' },
      { label: 'Service Availability', desc: 'DoS resilience & uptime' },
      { label: 'Access Control', desc: 'Privileged access to network systems' },
    ],
    recommendations: [
      'Harden network perimeter and segment critical infrastructure',
      'Protect subscriber PII and call-data records with encryption',
      'Defend against DoS to protect service availability',
      'Tightly control privileged access to network management systems',
      'Monitor for anomalous traffic and lateral movement',
    ],
    priorityCategories: ['access', 'config', 'auth', 'dos', 'network', 'data', 'tls', 'ssl', 'encryption'],
  },
  media: {
    id: 'media',
    label: 'Media / Entertainment',
    icon: '🎬',
    riskTier: 'medium',
    riskMultiplier: 1.15,
    compliance: [
      { label: 'GDPR', full: 'General Data Protection Regulation' },
      { label: 'DRM', full: 'Digital Rights Management' },
    ],
    focusAreas: [
      { label: 'Content Protection', desc: 'DRM & anti-piracy controls' },
      { label: 'User Data Protection', desc: 'Account & viewing-history privacy' },
      { label: 'Account Security', desc: 'Credential stuffing & takeover defence' },
      { label: 'Streaming Integrity', desc: 'Secure delivery & token validation' },
    ],
    recommendations: [
      'Protect premium content with DRM and signed delivery tokens',
      'Defend user accounts against credential stuffing & takeover',
      'Encrypt user data and viewing history',
      'Validate and expire streaming/access tokens correctly',
      'Rate-limit APIs to prevent scraping and abuse',
    ],
    priorityCategories: ['auth', 'session', 'data', 'api', 'access', 'tls', 'ssl', 'token'],
  },
  other: {
    id: 'other',
    label: 'Other',
    icon: '🏢',
    riskTier: 'standard',
    riskMultiplier: 1.0,
    compliance: [
      { label: 'GDPR', full: 'General Data Protection Regulation' },
    ],
    focusAreas: [
      { label: 'Data Protection', desc: 'Sensitive data handling baseline' },
      { label: 'Access Control', desc: 'Authentication & authorization' },
      { label: 'Encryption', desc: 'TLS in transit, encryption at rest' },
      { label: 'Secure Configuration', desc: 'Hardened defaults & patching' },
    ],
    recommendations: [
      'Enforce HTTPS/TLS across all services',
      'Apply strong authentication and least-privilege access',
      'Keep software and dependencies patched',
      'Encrypt sensitive data at rest and in transit',
      'Run regular authorized security scans',
    ],
    priorityCategories: ['auth', 'tls', 'ssl', 'config', 'access', 'data', 'encryption', 'injection'],
  },
};

export const INDUSTRY_LIST: IndustryConfig[] = Object.values(INDUSTRIES);

/** Resolve an industry config from a stored id/label, falling back to "other". */
export function getIndustry(value?: string | null): IndustryConfig {
  if (!value) return INDUSTRIES.other;
  const v = value.trim().toLowerCase();
  // direct id match
  if ((INDUSTRIES as Record<string, IndustryConfig>)[v]) {
    return (INDUSTRIES as Record<string, IndustryConfig>)[v];
  }
  // label / partial match
  const found = INDUSTRY_LIST.find(
    (i) => i.label.toLowerCase() === v || i.label.toLowerCase().includes(v) || v.includes(i.id),
  );
  return found || INDUSTRIES.other;
}

export function riskTierLabel(tier: RiskTier): { label: string; color: string } {
  switch (tier) {
    case 'high':
      return { label: 'High-Sensitivity Industry', color: '#EF4444' };
    case 'medium':
      return { label: 'Medium-Sensitivity Industry', color: '#DAA520' };
    default:
      return { label: 'Standard Sensitivity', color: '#10B981' };
  }
}

/**
 * Whether a finding is especially relevant to the given industry,
 * based on its category/title matching the industry's priority categories.
 */
export function isFindingRelevant(
  industry: IndustryConfig,
  finding: { category?: string; title?: string },
): boolean {
  const hay = `${finding.category || ''} ${finding.title || ''}`.toLowerCase();
  return industry.priorityCategories.some((c) => hay.includes(c));
}

/**
 * Sort findings so industry-relevant ones come first, then by severity.
 * Returns a new array; does not mutate the input.
 */
export function prioritizeFindings<T extends { category?: string; title?: string; severity?: string }>(
  industry: IndustryConfig,
  findings: T[],
): T[] {
  const severityRank: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  return [...findings].sort((a, b) => {
    const ra = isFindingRelevant(industry, a) ? 0 : 1;
    const rb = isFindingRelevant(industry, b) ? 0 : 1;
    if (ra !== rb) return ra - rb;
    const sa = severityRank[(a.severity || '').toLowerCase()] ?? 5;
    const sb = severityRank[(b.severity || '').toLowerCase()] ?? 5;
    return sa - sb;
  });
}

/**
 * Adjust a base security score (0-100) for industry sensitivity. High-risk
 * industries are penalised more for the gap below 100 (lower tolerance),
 * producing a stricter, industry-adjusted score.
 */
export function industryAdjustedScore(industry: IndustryConfig, baseScore: number): number {
  if (industry.riskMultiplier <= 1) return Math.round(baseScore);
  const gap = 100 - baseScore;
  const adjusted = 100 - gap * industry.riskMultiplier;
  return Math.max(0, Math.min(100, Math.round(adjusted)));
}
