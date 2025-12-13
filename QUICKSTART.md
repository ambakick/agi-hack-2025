# Quick Start Guide

Get your AI Podcast Generator running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- API keys (see [SETUP.md](SETUP.md) for details)

## 1. Clone & Install Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp backend/env.example backend/.env
# Edit .env with your API keys:
# - YOUTUBE_API_KEY
# - GEMINI_API_KEY
# - ELEVENLABS_API_KEY

# Start server
uvicorn app.main:app --reload
```

Backend will run at: **http://localhost:8000**

## 2. Install Frontend (2 minutes)

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start frontend
npm run dev
```

Frontend will run at: **http://localhost:3000**

## 3. Generate Your First Podcast! (1 minute)

1. Open http://localhost:3000
2. Enter a topic (e.g., "The Future of AI")
3. Choose format (single or two hosts)
4. Select 2-3 reference videos
5. Review the auto-generated outline
6. Wait for script generation
7. Listen to your podcast!

## Verify Installation

### Backend Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### API Documentation
Visit: http://localhost:8000/docs

### Frontend
Visit: http://localhost:3000

## Example Test Run

**Topic:** "Climate Change Solutions"
**Format:** Two hosts
**References:** Select 3 videos about climate tech
**Expected:** ~5-7 minute generation time

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Verify all API keys are set in `.env`
- Check port 8000 is available

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Run `rm -rf node_modules && npm install`
- Verify NEXT_PUBLIC_API_URL is set

### "Cannot connect to backend"
- Ensure backend is running on port 8000
- Check CORS_ORIGINS in backend `.env` includes `http://localhost:3000`

### API errors
- Verify API keys are valid
- Check API quotas haven't been exceeded
- Review backend logs for specific errors

## What's Next?

- Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for full feature overview
- See [TESTING.md](TESTING.md) for comprehensive testing guide
- Check [SETUP.md](SETUP.md) for deployment instructions

## Need Help?

1. Check API documentation: http://localhost:8000/docs
2. Review backend logs in terminal
3. Check browser console for frontend errors
4. Verify all environment variables are set correctly

---

**Enjoy creating AI-powered podcasts! 🎙️**

