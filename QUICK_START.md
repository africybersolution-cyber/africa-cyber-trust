# ⚡ Quick Start Guide

Get the Africa Cyber Trust Infrastructure running in 5 minutes!

## Prerequisites Check

✅ **Docker Desktop** - Must be running  
✅ **Node.js 18+** - `node --version`  
✅ **Python 3.11+** - `python3 --version` or `python --version`  
✅ **Git** - Already cloned at `C:/Users/Admin/africa-cyber-trust`

## 🚀 Three-Step Launch

### Step 1: Start Infrastructure (1 minute)

```bash
cd C:/Users/Admin/africa-cyber-trust/docker
docker-compose up -d
```

This starts:
- PostgreSQL database on port 5432
- Redis on port 6379
- Auto-creates database schema

Verify it's running:
```bash
docker-compose ps
```

You should see both services "Up" and "healthy".

### Step 2: Start Backend (2 minutes)

**Open a new terminal:**

```bash
cd C:/Users/Admin/africa-cyber-trust/backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate it
source venv/bin/activate  # Git Bash
# OR
venv\Scripts\activate  # PowerShell

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at: **http://localhost:8000**  
📚 API Docs at: **http://localhost:8000/docs**

### Step 3: Start Frontend (2 minutes)

**Open another new terminal:**

```bash
cd C:/Users/Admin/africa-cyber-trust/frontend

# Install dependencies (first time only)
npm install

# Run dev server
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

## 🎉 You're Ready!

Open your browser to **http://localhost:3000** and you should see the landing page!

## 🧪 Test It Works

### Test the Backend API

Visit http://localhost:8000/docs and try:

1. Click on `GET /` endpoint
2. Click "Try it out"
3. Click "Execute"
4. You should see a 200 response with app info

### Test the Frontend

Visit http://localhost:3000:

- You should see "Africa Cyber Trust Infrastructure" heading
- URL input field (not functional yet)
- Three feature cards
- Blue CTA button

## 🛑 Stop Everything

**Stop backend:** Press `Ctrl+C` in backend terminal  
**Stop frontend:** Press `Ctrl+C` in frontend terminal  
**Stop Docker:**
```bash
cd C:/Users/Admin/africa-cyber-trust/docker
docker-compose down
```

## 🔧 Troubleshooting

### "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Git Bash
lsof -ti:8000 | xargs kill -9
```

### "Port 3000 already in use"
Same as above, but use port 3000

### "Cannot connect to database"
Make sure Docker is running:
```bash
docker ps
```

Check PostgreSQL logs:
```bash
cd docker
docker-compose logs postgres
```

### "Module not found" errors in backend
Make sure virtual environment is activated:
```bash
# You should see (venv) in your prompt
which python  # Should show path inside venv folder
```

If not activated:
```bash
cd backend
source venv/bin/activate
```

### "npm: command not found"
Install Node.js from https://nodejs.org/

### Docker services won't start
```bash
# Nuclear option - clean restart
cd docker
docker-compose down -v
docker-compose up -d
```

## 📖 What Next?

- Read [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup
- Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for current progress
- See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for architecture
- Review `Africa_Cyber_Trust_Infrastructure_Spec.pdf` for full requirements

## 🏗️ Start Building

The MVP is scaffolded and ready for Phase 2 implementation:

1. **Implement background checkers** - Add real DNS, SSL, blacklist checks
2. **Connect AI** - Add OpenAI/Anthropic API keys and implement explanation
3. **Build results page** - Create frontend to display check results
4. **Add database models** - Create SQLAlchemy models
5. **Implement rate limiting** - Protect against abuse

See `backend/app/services/background_checker.py` for TODOs.

---

**Need help?** Check the troubleshooting section above or review the full setup guide.

**Ready to code?** Jump into Phase 2 implementation! 🚀
