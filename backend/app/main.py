"""Main FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import public_check, auth, company, assets, scans, ai_verify, payments, company_verification, admin, email_verification, alerts, team, admin_fix_users, breaches, trust_badge, remediation, cve_enrichment, free_trust_score, admin_users, admin_analytics, admin_audit, admin_assets, admin_payments, admin_setup, run_migration

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Powered Cybersecurity Trust, Background Check, and Monitoring Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    # Do NOT 307-redirect a trailing-slash mismatch. A cross-origin redirect
    # strips the CORS headers and the browser aborts with "Failed to fetch".
    # With this off + the strip_trailing_slash middleware below, "/api/assets/"
    # is served by the "/api/assets" route directly, no redirect.
    redirect_slashes=False,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to handle trailing slashes without redirecting
@app.middleware("http")
async def strip_trailing_slash(request: Request, call_next):
    """Strip trailing slashes from URLs to avoid redirects."""
    if request.url.path != "/" and request.url.path.endswith("/"):
        # Remove trailing slash
        new_path = request.url.path.rstrip("/")
        request.scope["path"] = new_path
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    print("=" * 60)
    print("STARTING AFRICA CYBER TRUST INFRASTRUCTURE")
    print("=" * 60)

    # Debug: Print CORS origins
    print(f"[DEBUG] CORS Origins: {settings.cors_origins}")
    print(f"[DEBUG] Raw ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")

    # Initialize database tables
    from app.db.database import Base, get_engine
    # Import all models to register them with Base.metadata
    from app.models import user, company, asset, scan, subscription, public_check, alert, verification

    engine = get_engine()
    if engine:
        print("[DB] Creating database tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables ready")

        # Add password reset columns if they don't exist (migration)
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                # Check if reset_token column exists
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='users' AND column_name='reset_token'
                """))

                if not result.fetchone():
                    print("[DB] Adding password reset columns to users table...")
                    conn.execute(text("""
                        ALTER TABLE users
                        ADD COLUMN reset_token VARCHAR(255),
                        ADD COLUMN reset_token_expires TIMESTAMP WITH TIME ZONE
                    """))
                    conn.commit()
                    print("[OK] Password reset columns added")
                else:
                    print("[OK] Password reset columns already exist")
        except Exception as e:
            print(f"[WARNING] Could not add password reset columns: {e}")

    # Start background scheduler for automated tasks
    from app.services.scheduler_service import scheduler_service
    scheduler_service.schedule_jobs()

    print("[OK] Background scheduler started")
    print("[OK] Token cleanup job scheduled (every 1 hour)")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("Shutting down gracefully...")

    # Stop scheduler
    from app.services.scheduler_service import scheduler_service
    scheduler_service.shutdown()

    print("[OK] Background scheduler stopped")
    print("Shutdown complete")


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/scheduler/status")
async def scheduler_status():
    """Get status of background scheduler and jobs."""
    from app.services.scheduler_service import scheduler_service
    return scheduler_service.get_job_status()


# Include API routers
app.include_router(free_trust_score.router, tags=["Free Trust Score"])  # Public - no auth required
app.include_router(public_check.router, prefix="/api/public-check", tags=["Public Checks"])
app.include_router(ai_verify.router, prefix="/api/ai-verify", tags=["AI Verification"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments & Subscriptions"])
app.include_router(company_verification.router, prefix="/api/company", tags=["Company Verification"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(admin_users.router, tags=["Admin - Users"])  # Super admin user management
app.include_router(admin_analytics.router, tags=["Admin - Analytics"])  # Revenue & metrics
app.include_router(admin_audit.router, tags=["Admin - Audit"])  # Audit log viewer
app.include_router(admin_assets.router, tags=["Admin - Assets"])  # Asset override (bypass verification, manual scans)
app.include_router(admin_payments.router, tags=["Admin - Payments"])  # Payment management & refunds
app.include_router(admin_fix_users.router, prefix="/api", tags=["Admin Setup"])  # One-time user fix
app.include_router(admin_setup.router, prefix="/api", tags=["Admin Setup"])  # One-time super admin setup
app.include_router(run_migration.router, prefix="/api", tags=["Admin Setup"])  # One-time migration runner
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])  # Asset management
app.include_router(scans.router, prefix="/api/scans", tags=["Scans"])
app.include_router(email_verification.router, prefix="/api/email-verification", tags=["Email Verification"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(team.router, prefix="/api/team", tags=["Team Management"])
app.include_router(breaches.router, tags=["Breach Monitoring"])  # Breach monitoring (HaveIBeenPwned)
app.include_router(trust_badge.router, tags=["Trust Badge"])  # Embeddable trust badges
app.include_router(remediation.router, tags=["Remediation"])  # Finding remediation tracking
app.include_router(cve_enrichment.router, tags=["CVE Intelligence"])  # CVE/NVD vulnerability intelligence


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
