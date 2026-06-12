"""
Migration: Create scanning system tables
Creates scans and findings tables for security scanning
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings


def run_migration():
    """Create scans and findings tables."""
    print("=" * 70)
    print("MIGRATION: Scanning System")
    print("=" * 70)
    print()

    engine = create_engine(settings.DATABASE_URL)

    with engine.begin() as conn:
        # Create scans table
        print("1. Creating scans table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS scans (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                score INTEGER,
                started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE,
                scan_type VARCHAR(50) NOT NULL DEFAULT 'full',
                findings_count INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0,
                high_count INTEGER DEFAULT 0,
                medium_count INTEGER DEFAULT 0,
                low_count INTEGER DEFAULT 0,
                scan_data JSONB,

                CONSTRAINT scans_status_check
                    CHECK (status IN ('pending', 'running', 'completed', 'failed')),
                CONSTRAINT scans_score_check
                    CHECK (score >= 0 AND score <= 100)
            );

            CREATE INDEX IF NOT EXISTS idx_scans_asset_id ON scans(asset_id);
            CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);
            CREATE INDEX IF NOT EXISTS idx_scans_started_at ON scans(started_at DESC);

            COMMENT ON TABLE scans IS 'Security scans performed on assets';
        """))
        print("   [OK] Scans table created")
        print()

        # Create findings table
        print("2. Creating findings table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS findings (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
                severity VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                recommendation TEXT,
                category VARCHAR(100),
                cve_id VARCHAR(50),
                found_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMP WITH TIME ZONE,
                finding_data JSONB,

                CONSTRAINT findings_severity_check
                    CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info'))
            );

            CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON findings(scan_id);
            CREATE INDEX IF NOT EXISTS idx_findings_asset_id ON findings(asset_id);
            CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
            CREATE INDEX IF NOT EXISTS idx_findings_resolved ON findings(resolved);

            COMMENT ON TABLE findings IS 'Security issues found during scans';
        """))
        print("   [OK] Findings table created")
        print()

        # Add last_scan_at column to assets
        print("3. Updating assets table...")
        conn.execute(text("""
            ALTER TABLE assets
            ADD COLUMN IF NOT EXISTS last_scan_at TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS security_score INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS findings_count INTEGER DEFAULT 0;

            ALTER TABLE assets
            ADD CONSTRAINT assets_security_score_check
            CHECK (security_score >= 0 AND security_score <= 100);
        """))
        print("   [OK] Assets table updated with scan fields")
        print()

    print("=" * 70)
    print("MIGRATION COMPLETE!")
    print("=" * 70)
    print()
    print("Created:")
    print("  - scans table (12 columns, 3 indexes)")
    print("  - findings table (13 columns, 4 indexes)")
    print("  - Updated assets table (3 new columns)")
    return True


if __name__ == "__main__":
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
