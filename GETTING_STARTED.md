# Getting Started with Africa Cyber Trust Infrastructure

Complete guide to set up and run the platform locally.

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **Git**

## Step 1: Clone and Setup

The project is already initialized at `C:/Users/Admin/africa-cyber-trust/`

```bash
cd C:/Users/Admin/africa-cyber-trust
```

## Step 2: Start Infrastructure Services

Start PostgreSQL and Redis using Docker Compose:

```bash
cd docker
docker-compose up -d
```

This will:
- Start PostgreSQL on port 5432
- Start Redis on port 6379
- Automatically create the database schema from `database/schema.sql`

Verify services are running:
```bash
docker-compose ps
```

## Step 3: Setup Backend (FastAPI)

### 3.1 Create Python Virtual Environment

```bash
cd ../backend
python -m venv venv
```

### 3.2 Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate
```

**On Windows (Git Bash):**
```bash
source venv/Scripts/activate
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

### 3.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.4 Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and update these essential values:
```env
DATABASE_URL=postgresql://acti_user:acti_dev_password_change_in_production@localhost:5432/africa_cyber_trust
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3.5 Run Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Step 4: Setup Frontend (Next.js)

### 4.1 Install Dependencies

Open a new terminal window:

```bash
cd C:/Users/Admin/africa-cyber-trust/frontend
npm install
```

### 4.2 Configure Environment

Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4.3 Run Development Server

```bash
npm run dev
```

The frontend will be available at: http://localhost:3000

## Step 5: Verify Installation

### Check Database

Connect to PostgreSQL to verify schema:
```bash
docker exec -it acti_postgres psql -U acti_user -d africa_cyber_trust
```

List tables:
```sql
\dt
```

You should see tables like: users, companies, assets, scan_jobs, findings, etc.

### Test Backend API

Visit http://localhost:8000/docs and test the endpoints:
- GET `/` - Health check
- POST `/api/public-check/url` - Test URL checking (placeholder)

### Test Frontend

Visit http://localhost:3000 - You should see the landing page with:
- Hero section
- URL check input
- Feature cards
- Business CTA

## Development Workflow

### Backend Development

1. **Code Structure:**
   - `app/api/` - API endpoints (routers)
   - `app/services/` - Business logic
   - `app/models/` - SQLAlchemy models (to be created)
   - `app/schemas/` - Pydantic schemas
   - `app/scanners/` - Security scanner implementations

2. **Adding New Endpoints:**
   - Create router in `app/api/`
   - Define schemas in `app/schemas/`
   - Implement service in `app/services/`
   - Register router in `app/main.py`

3. **Testing:**
   ```bash
   pytest
   ```

### Frontend Development

1. **Code Structure:**
   - `app/` - Next.js app directory
   - `app/page.tsx` - Home page
   - `components/` - Reusable components (to be created)
   - `lib/` - Utilities and API clients (to be created)

2. **Adding Pages:**
   ```bash
   # Create new page
   mkdir app/check
   touch app/check/page.tsx
   ```

3. **Build for Production:**
   ```bash
   npm run build
   npm start
   ```

## Common Tasks

### View Logs

**Docker services:**
```bash
cd docker
docker-compose logs -f
```

**Specific service:**
```bash
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Reset Database

```bash
docker-compose down -v
docker-compose up -d
```

### Stop All Services

```bash
# Stop Docker services
cd docker
docker-compose down

# Stop backend (Ctrl+C in terminal)
# Stop frontend (Ctrl+C in terminal)
```

### Access Redis CLI

```bash
docker exec -it acti_redis redis-cli
```

## Next Steps

### Phase 2: Public Checker Implementation (Weeks 5-8)

1. **Implement Background Checker Service:**
   - Complete `background_checker.py` methods
   - Add DNS/WHOIS lookups
   - SSL certificate validation
   - Blacklist integration (Google Safe Browsing, VirusTotal)

2. **Create Check Results Page:**
   - Frontend: `app/check/[id]/page.tsx`
   - Display trust score with visual indicators
   - Show red flags and AI explanation
   - Add "Report Scam" button

3. **Add Rate Limiting:**
   - Implement IP-based rate limiting
   - Store check history

### Phase 3: Company Verification (Weeks 9-10)

1. **Implement Verification Methods:**
   - DNS TXT record verification
   - HTML file upload verification
   - Admin email verification

2. **Create Company Dashboard:**
   - Asset management
   - Verification status
   - Scan scheduling

### Phase 4: Verified Scanner (Weeks 11-16)

1. **Integrate Security Tools:**
   - Nuclei templates
   - OWASP ZAP scanning
   - SSLyze checks

2. **Implement Celery Workers:**
   - Background scan jobs
   - Result storage
   - Alert generation

## Troubleshooting

### Port Already in Use

**Backend (8000):**
```bash
# Find process
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

**Frontend (3000):**
```bash
# Same as above, but for port 3000
```

### Database Connection Issues

1. Check Docker containers are running:
   ```bash
   docker ps
   ```

2. Test PostgreSQL connection:
   ```bash
   docker exec -it acti_postgres pg_isready -U acti_user
   ```

3. Check credentials in `.env` match `docker-compose.yml`

### Module Import Errors

Make sure virtual environment is activated:
```bash
which python  # Should show path in venv
pip list  # Should show installed packages
```

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Next.js Docs:** https://nextjs.org/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Tailwind CSS:** https://tailwindcss.com/docs

## Support

For issues or questions:
1. Check logs for error messages
2. Verify all services are running
3. Review configuration files
4. Consult the spec document: `Africa_Cyber_Trust_Infrastructure_Spec.pdf`

---

**Happy Building! 🚀**
