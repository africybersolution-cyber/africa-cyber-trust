"""Main FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import public_check, auth, company, assets, scans, ai_verify, payments, company_verification, admin, email_verification, alerts, team

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Powered Cybersecurity Trust, Background Check, and Monitoring Platform",
    docs_url="/docs",
    redoc_url="/redoc",
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
app.include_router(public_check.router, prefix="/api/public-check", tags=["Public Checks"])
app.include_router(ai_verify.router, prefix="/api/ai-verify", tags=["AI Verification"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments & Subscriptions"])
app.include_router(company_verification.router, prefix="/api/company", tags=["Company Verification"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])  # Asset management
app.include_router(scans.router, prefix="/api/scans", tags=["Scans"])
app.include_router(email_verification.router, prefix="/api/email-verification", tags=["Email Verification"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(team.router, prefix="/api/team", tags=["Team Management"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
