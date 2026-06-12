-- Africa Cyber Trust Infrastructure - Database Schema
-- PostgreSQL Schema for MVP

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User roles enum
CREATE TYPE user_role AS ENUM ('normal_user', 'company_owner', 'company_admin', 'company_analyst', 'company_developer', 'company_viewer', 'platform_admin', 'security_analyst');

-- Asset types enum
CREATE TYPE asset_type AS ENUM ('domain', 'subdomain', 'api_endpoint', 'mobile_app', 'ip_address', 'ip_range');

-- Verification methods enum
CREATE TYPE verification_method AS ENUM ('dns_txt', 'html_file', 'admin_email', 'signed_authorization', 'manual_approval');

-- Verification status enum
CREATE TYPE verification_status AS ENUM ('pending', 'verified', 'failed', 'expired');

-- Scan types enum
CREATE TYPE scan_type AS ENUM ('public_check', 'verified_web_scan', 'api_security_scan', 'mobile_app_scan', 'network_scan');

-- Scan job status enum
CREATE TYPE scan_job_status AS ENUM ('queued', 'running', 'completed', 'failed', 'cancelled');

-- Risk levels enum
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical', 'unknown');

-- Finding severity enum
CREATE TYPE finding_severity AS ENUM ('info', 'low', 'medium', 'high', 'critical');

-- Finding status enum
CREATE TYPE finding_status AS ENUM ('open', 'in_progress', 'fixed', 'accepted_risk', 'false_positive', 'wont_fix');

-- Alert channels enum
CREATE TYPE alert_channel AS ENUM ('email', 'sms', 'whatsapp', 'dashboard');

-- Alert status enum
CREATE TYPE alert_status AS ENUM ('pending', 'sent', 'failed', 'acknowledged');

-- Subscription plans enum
CREATE TYPE subscription_plan AS ENUM ('free', 'starter', 'business', 'enterprise');

-- Report status enum
CREATE TYPE report_status AS ENUM ('pending', 'in_review', 'verified', 'false_positive', 'dismissed');

-- =====================================================
-- Core Tables
-- =====================================================

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'normal_user',
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    industry VARCHAR(100),
    plan_id subscription_plan NOT NULL DEFAULT 'free',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_companies_country ON companies(country);
CREATE INDEX idx_companies_plan_id ON companies(plan_id);

-- Company users (junction table for company-user relationship)
CREATE TABLE company_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role user_role NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, user_id)
);

CREATE INDEX idx_company_users_company_id ON company_users(company_id);
CREATE INDEX idx_company_users_user_id ON company_users(user_id);

-- Assets table
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    type asset_type NOT NULL,
    value TEXT NOT NULL,  -- Domain, IP, app package name, etc.
    description TEXT,
    verification_status verification_status NOT NULL DEFAULT 'pending',
    verification_method verification_method,
    verified_at TIMESTAMPTZ,
    scan_enabled BOOLEAN DEFAULT TRUE,
    last_scanned_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assets_company_id ON assets(company_id);
CREATE INDEX idx_assets_type ON assets(type);
CREATE INDEX idx_assets_verification_status ON assets(verification_status);

-- Verifications table (tracks verification attempts)
CREATE TABLE verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    method verification_method NOT NULL,
    token VARCHAR(255),  -- Verification token/code
    status verification_status NOT NULL DEFAULT 'pending',
    verification_data JSONB,  -- Store method-specific data
    verified_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_verifications_asset_id ON verifications(asset_id);
CREATE INDEX idx_verifications_token ON verifications(token);

-- =====================================================
-- Scanning Tables
-- =====================================================

-- Scan jobs table
CREATE TABLE scan_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    scan_type scan_type NOT NULL,
    status scan_job_status NOT NULL DEFAULT 'queued',
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    worker_id VARCHAR(255),  -- Celery task ID
    error_message TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scan_jobs_asset_id ON scan_jobs(asset_id);
CREATE INDEX idx_scan_jobs_status ON scan_jobs(status);
CREATE INDEX idx_scan_jobs_scheduled_at ON scan_jobs(scheduled_at);

-- Scan results table
CREATE TABLE scan_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_job_id UUID NOT NULL REFERENCES scan_jobs(id) ON DELETE CASCADE,
    raw_result_url TEXT,  -- S3/storage URL for full scan output
    score INTEGER CHECK (score >= 0 AND score <= 100),
    risk_level risk_level,
    summary TEXT,
    metadata JSONB,  -- Store scanner versions, configs, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scan_results_scan_job_id ON scan_results(scan_job_id);
CREATE INDEX idx_scan_results_risk_level ON scan_results(risk_level);

-- Findings table
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_result_id UUID NOT NULL REFERENCES scan_results(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    severity finding_severity NOT NULL,
    cvss_score DECIMAL(3,1),  -- CVSS score (0.0 - 10.0)
    category VARCHAR(100),  -- OWASP category, CWE, etc.
    description TEXT,
    evidence TEXT,
    remediation TEXT,
    status finding_status NOT NULL DEFAULT 'open',
    false_positive_reason TEXT,
    analyst_notes TEXT,
    status_updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    status_updated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_findings_scan_result_id ON findings(scan_result_id);
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_findings_status ON findings(status);

-- =====================================================
-- Public Check Tables
-- =====================================================

-- Public checks table (for normal users)
CREATE TABLE public_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- Nullable for anonymous checks
    input_type VARCHAR(50) NOT NULL,  -- 'url', 'app', 'company', 'payment_link'
    input_value TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    risk_level risk_level,
    summary TEXT,
    red_flags JSONB,  -- Array of red flag objects
    ai_explanation TEXT,
    check_data JSONB,  -- Store all check results
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_public_checks_user_id ON public_checks(user_id);
CREATE INDEX idx_public_checks_input_type ON public_checks(input_type);
CREATE INDEX idx_public_checks_created_at ON public_checks(created_at);

-- User reports (scam reports from public)
CREATE TABLE user_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    public_check_id UUID REFERENCES public_checks(id) ON DELETE SET NULL,
    target_value TEXT NOT NULL,  -- URL/app/company being reported
    reporter_contact VARCHAR(255),  -- Optional email/phone
    reason TEXT NOT NULL,
    evidence_url TEXT,  -- Optional screenshot/proof
    status report_status NOT NULL DEFAULT 'pending',
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    admin_notes TEXT,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_reports_status ON user_reports(status);
CREATE INDEX idx_user_reports_target_value ON user_reports(target_value);

-- =====================================================
-- Alerts & Notifications
-- =====================================================

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    finding_id UUID REFERENCES findings(id) ON DELETE CASCADE,
    channel alert_channel NOT NULL,
    recipient VARCHAR(255) NOT NULL,  -- Email/phone number
    subject VARCHAR(500),
    message TEXT NOT NULL,
    status alert_status NOT NULL DEFAULT 'pending',
    sent_at TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_company_id ON alerts(company_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);

-- =====================================================
-- Subscriptions & Billing
-- =====================================================

-- Subscriptions table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    plan subscription_plan NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',  -- active, cancelled, expired, suspended
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    renews_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    metadata JSONB,  -- Payment provider data, limits, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_company_id ON subscriptions(company_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- =====================================================
-- Audit & Logging
-- =====================================================

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,  -- scan_started, finding_updated, asset_verified, etc.
    entity_type VARCHAR(50),  -- assets, findings, users, etc.
    entity_id UUID,
    ip_address INET,
    user_agent TEXT,
    changes JSONB,  -- Store old/new values
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_actor_user_id ON audit_logs(actor_user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- =====================================================
-- Functions & Triggers
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Initial Data
-- =====================================================

-- Insert default platform admin user (password should be set via application)
INSERT INTO users (email, name, role, email_verified, is_active)
VALUES ('admin@africacybertrust.com', 'Platform Admin', 'platform_admin', TRUE, TRUE);

-- Insert sample subscription plans metadata (stored in company metadata or separate config)
-- Plans: free (1 asset, weekly scans), starter (5 assets, daily), business (20 assets, hourly), enterprise (unlimited, continuous)

COMMENT ON TABLE users IS 'All platform users (normal users, company members, admins)';
COMMENT ON TABLE companies IS 'Organizations subscribing for verified scanning services';
COMMENT ON TABLE assets IS 'Company-owned digital assets (domains, apps, APIs, IPs)';
COMMENT ON TABLE scan_jobs IS 'Background scanning jobs executed by Celery workers';
COMMENT ON TABLE findings IS 'Security vulnerabilities and issues discovered during scans';
COMMENT ON TABLE public_checks IS 'Public background checks run by normal users';
COMMENT ON TABLE user_reports IS 'Scam/fraud reports submitted by users';
COMMENT ON TABLE alerts IS 'Notifications sent to companies about security issues';
