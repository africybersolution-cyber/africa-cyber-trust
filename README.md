# Africa Cyber Trust Infrastructure

AI-Powered Cybersecurity Trust, Background Check, and Monitoring Platform for Africa

## Project Overview

A platform that helps ordinary users perform safe background checks on websites, apps, fintechs, and companies, while verified businesses subscribe for deeper vulnerability scanning, monitoring, alerts, and AI-assisted remediation.

## Core Features

### For Normal Users
- Website legitimacy checker (passive, safe background checks)
- App security scanner (Play Store/APK analysis)
- Company/fintech background checks
- Trust scoring with AI explanations

### For Businesses
- Domain/asset ownership verification
- Deep vulnerability scanning (after verification)
- Continuous monitoring dashboard
- Email/SMS/WhatsApp alerts
- Executive and technical reports
- AI-assisted remediation guidance

## Tech Stack

- **Frontend**: Next.js (React, TypeScript)
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **Queue**: Redis + Celery
- **Scanners**: Nuclei, OWASP ZAP, SSLyze, Nmap
- **AI**: GPT-5 class models
- **Storage**: S3-compatible (reports, evidence)
- **Containerization**: Docker

## Project Structure

```
africa-cyber-trust/
├── frontend/          # Next.js web application
├── backend/           # FastAPI server
├── database/          # PostgreSQL schemas and migrations
├── docker/            # Docker Compose and container configs
├── docs/              # Documentation
└── README.md
```

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose

### Development Setup

1. **Start infrastructure services**
   ```bash
   cd docker
   docker-compose up -d
   ```

2. **Setup backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Setup frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development Phases

- **Phase 1**: Foundation (Weeks 1-4) - Auth, database, user roles
- **Phase 2**: Public checker (Weeks 5-8) - URL checker, trust scoring
- **Phase 3**: Company verification (Weeks 9-10) - Domain verification
- **Phase 4**: Verified scanner (Weeks 11-16) - Vulnerability scanning
- **Phase 5**: Dashboard and alerts (Weeks 17-20) - Analytics, reports

## Legal & Compliance

- Public checks are **passive only** (no aggressive scanning)
- Deep scans require **verified ownership** or written authorization
- Scanning government/military/banks requires manual approval
- All scans are logged with audit trails

## License

Proprietary - Africa Cyber Trust Infrastructure

## Contact

For questions or support, contact the development team.
