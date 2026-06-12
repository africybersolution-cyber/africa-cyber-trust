# Africa Cyber Trust Infrastructure - Project Structure

## Directory Overview

```
africa-cyber-trust/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── public_check.py  # Public background check endpoints
│   │   │   ├── auth.py          # Authentication (placeholder)
│   │   │   ├── company.py       # Company management (placeholder)
│   │   │   ├── assets.py        # Asset management (placeholder)
│   │   │   └── scans.py         # Scanning endpoints (placeholder)
│   │   ├── core/              # Core configuration
│   │   │   └── config.py        # Settings with Pydantic
│   │   ├── db/                # Database setup
│   │   │   └── database.py      # SQLAlchemy engine & session
│   │   ├── models/            # SQLAlchemy models (to be created)
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   │   └── public_check.py
│   │   ├── services/          # Business logic layer
│   │   │   ├── background_checker.py  # Passive security checks
│   │   │   └── trust_scorer.py        # Risk scoring algorithm
│   │   ├── scanners/          # Security scanner integrations (to be created)
│   │   ├── utils/             # Utility functions (to be created)
│   │   └── main.py            # FastAPI app entry point
│   ├── .env                   # Environment variables (configured)
│   ├── .env.example           # Environment template
│   ├── Dockerfile             # Container image definition
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Next.js 15 frontend
│   ├── app/                   # Next.js app directory
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Landing page (implemented)
│   ├── components/            # React components (to be created)
│   ├── lib/                   # Utilities & API clients (to be created)
│   ├── public/                # Static assets
│   ├── .env.local             # Frontend environment (to be created)
│   ├── package.json           # Node dependencies
│   └── tailwind.config.ts     # Tailwind CSS configuration
│
├── database/                   # Database files
│   └── schema.sql             # Complete PostgreSQL schema
│
├── docker/                     # Docker configuration
│   └── docker-compose.yml     # PostgreSQL + Redis services
│
├── docs/                       # Documentation
│   └── PROJECT_STRUCTURE.md   # This file
│
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
├── GETTING_STARTED.md          # Setup guide
└── PROJECT_STATUS.md           # Current status & roadmap
```

## Key Files Explained

### Backend Files

**`backend/app/main.py`**
- FastAPI application entry point
- Registers all API routers
- Configures CORS middleware
- Health check endpoints

**`backend/app/core/config.py`**
- Loads environment variables using Pydantic Settings
- Database, Redis, AI API keys, email/SMS config
- Security settings and rate limits

**`backend/app/db/database.py`**
- SQLAlchemy engine and session management
- `get_db()` dependency for database access

**`backend/app/api/public_check.py`**
- POST `/api/public-check/url` - Check website
- POST `/api/public-check/app` - Check mobile app (placeholder)
- POST `/api/public-check/company` - Check company (placeholder)
- POST `/api/public-check/report-scam` - Report scam (placeholder)

**`backend/app/services/background_checker.py`**
- `BackgroundCheckerService` class
- Methods for DNS, SSL, headers, redirects, blacklists
- AI explanation generation (to be implemented)
- Database persistence

**`backend/app/services/trust_scorer.py`**
- `TrustScorerService` class
- `calculate_url_score()` - Scoring algorithm (implemented)
- Risk level determination (low/medium/high/critical)
- Red flags generation
- Safety advice generation

**`backend/app/schemas/public_check.py`**
- Pydantic models for requests/responses
- `PublicCheckURLRequest`, `PublicCheckResponse`
- Input validation and serialization

### Frontend Files

**`frontend/app/page.tsx`**
- Landing page component
- Hero section with value proposition
- URL check input field
- Feature cards
- Business CTA
- Footer

**`frontend/app/layout.tsx`**
- Root layout component
- Includes HTML structure and metadata

### Database Files

**`database/schema.sql`**
- Complete PostgreSQL schema (3,500+ lines)
- Tables: users, companies, assets, scan_jobs, findings, etc.
- Enums: user_role, asset_type, risk_level, finding_severity
- Indexes for performance
- Triggers for updated_at timestamps
- Initial admin user seed

### Docker Files

**`docker/docker-compose.yml`**
- PostgreSQL 15 service (port 5432)
- Redis 7 service (port 6379)
- Celery worker (optional, --profile full)
- Redis Commander (optional, --profile tools)
- Health checks and volumes

## Data Flow

### Public URL Check Flow

```
User (Frontend)
    ↓
    ├─> POST /api/public-check/url
    ↓
FastAPI Router (public_check.py)
    ↓
    ├─> BackgroundCheckerService.check_url()
    │   ├─> DNS/WHOIS check
    │   ├─> SSL certificate check
    │   ├─> Security headers check
    │   ├─> Redirect analysis
    │   ├─> Blacklist lookup
    │   └─> Similar domains check
    ↓
TrustScorerService.calculate_url_score()
    ├─> Analyze check results
    ├─> Calculate score (0-100)
    ├─> Determine risk level
    ├─> Generate red flags
    └─> Create safety advice
    ↓
BackgroundCheckerService.generate_explanation()
    └─> AI explanation (OpenAI/Anthropic)
    ↓
Save to PostgreSQL (public_checks table)
    ↓
Return PublicCheckResponse
    ↓
Display in Frontend
```

### Future: Verified Company Scan Flow

```
Company User (Dashboard)
    ↓
    ├─> POST /api/company/assets/{id}/scan
    ↓
FastAPI checks asset verification
    ├─> If not verified: HTTP 403
    └─> If verified: Create scan_job
    ↓
Celery Worker picks up job
    ├─> Run Nuclei templates
    ├─> Run OWASP ZAP
    ├─> SSL/TLS analysis
    ├─> DNS checks
    └─> Store findings
    ↓
AI analyzes findings
    ├─> Prioritize by impact
    ├─> Generate remediation steps
    └─> Create executive summary
    ↓
Trigger alerts (email/SMS/WhatsApp)
    ↓
Update dashboard with results
```

## Technology Stack Details

### Backend Technologies
- **FastAPI 0.109** - Modern Python web framework
- **SQLAlchemy 2.0** - ORM for database
- **Psycopg2** - PostgreSQL adapter
- **Alembic** - Database migrations
- **Celery** - Background task queue
- **Redis** - Queue broker and cache
- **Pydantic** - Data validation
- **HTTPX/Requests** - HTTP clients
- **python-whois** - Domain lookups
- **cryptography** - SSL/TLS analysis
- **OpenAI/Anthropic** - AI APIs
- **pytest** - Testing

### Frontend Technologies
- **Next.js 15** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **ESLint** - Code linting

### Infrastructure
- **PostgreSQL 15** - Primary database
- **Redis 7** - Queue and cache
- **Docker & Docker Compose** - Containerization

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
SMTP_HOST=...
TWILIO_ACCOUNT_SID=...
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Schema Summary

### Core Tables (11 tables)
- **users** - All platform users
- **companies** - Organizations using the platform
- **company_users** - Company membership junction table
- **assets** - Company-owned domains/apps/APIs
- **verifications** - Asset ownership verification attempts

### Scanning Tables (4 tables)
- **scan_jobs** - Background scan job queue
- **scan_results** - Scan result summaries
- **findings** - Individual security issues

### Public Tables (2 tables)
- **public_checks** - User background checks
- **user_reports** - Scam reports from public

### System Tables (4 tables)
- **alerts** - Email/SMS/WhatsApp notifications
- **subscriptions** - Company billing
- **audit_logs** - All user actions
- (Additional tables in schema.sql)

## API Endpoints

### Public (No Auth Required)
- `GET /` - Health check
- `POST /api/public-check/url` - Check website
- `POST /api/public-check/app` - Check mobile app
- `POST /api/public-check/company` - Check company
- `POST /api/reports/scam` - Submit scam report

### Authenticated (Future)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/company/dashboard` - Company overview
- `POST /api/company/assets` - Add asset
- `POST /api/company/assets/{id}/verify/start` - Start verification
- `POST /api/company/assets/{id}/scan` - Start scan
- `GET /api/company/scans` - List scans
- `GET /api/company/findings` - List vulnerabilities

## Next Implementation Steps

1. **Implement DNS/WHOIS checks** in BackgroundCheckerService
2. **Integrate Google Safe Browsing API** for blacklist checks
3. **Add AI explanation** using OpenAI/Anthropic API
4. **Create SQLAlchemy models** matching database schema
5. **Build frontend results page** to display check results
6. **Add rate limiting** using SlowAPI
7. **Implement scam reporting** flow

---

See [GETTING_STARTED.md](../GETTING_STARTED.md) for setup instructions and [PROJECT_STATUS.md](../PROJECT_STATUS.md) for current progress.
