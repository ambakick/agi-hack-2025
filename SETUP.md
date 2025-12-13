# Setup Guide

Complete setup instructions for the AI Podcast Generator.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **API Keys:**
  - YouTube Data API key
  - Google Gemini API key
  - ElevenLabs API key

## Getting Your API Keys

### 1. YouTube Data API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "YouTube Data API v3"
4. Go to "Credentials" → Create credentials → API key
5. Copy your API key

### 2. Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create or select a project
4. Copy your API key

### 3. ElevenLabs API Key
1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Go to Profile Settings → API Keys
3. Generate new API key
4. Copy your API key

## Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp env.example .env
   ```

5. **Add your API keys to `.env`:**
   ```env
   YOUTUBE_API_KEY=your_youtube_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   DEBUG=true
   CORS_ORIGINS=http://localhost:3000
   ```

6. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will be available at: http://localhost:8000
   API documentation: http://localhost:8000/docs

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env.local` file:**
   ```bash
   cp .env.local.example .env.local
   ```

4. **Update `.env.local`:**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

5. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at: http://localhost:3000

## Testing the Application

1. **Open browser:** Navigate to http://localhost:3000

2. **Generate a podcast:**
   - Enter a topic (e.g., "The Future of AI")
   - Choose format (single host or two hosts)
   - Select 1-5 reference videos
   - Review auto-generated outline
   - Review generated script
   - Wait for audio generation
   - Play and download your podcast!

## Troubleshooting

### Backend Issues

**Import errors:**
```bash
pip install --upgrade -r requirements.txt
```

**API key errors:**
- Verify your API keys are correct in `.env`
- Check API quotas haven't been exceeded

**Port already in use:**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

**Module not found:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Cannot connect to backend:**
- Verify backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in `.env.local`

**Build errors:**
```bash
npm run build
# Check for TypeScript errors
```

## Production Deployment

### Backend (Railway/Render/AWS)

1. Set environment variables in your hosting platform
2. Install dependencies: `pip install -r requirements.txt`
3. Start with: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify)

1. Connect your Git repository
2. Set `NEXT_PUBLIC_API_URL` environment variable
3. Build command: `npm run build`
4. Deploy!

## API Rate Limits

- **YouTube API:** 10,000 units/day (free tier)
- **Gemini API:** Check your quota in Google Cloud Console
- **ElevenLabs:** Character limits vary by plan

## Support

For issues or questions, refer to:
- [README.md](README.md) for project overview
- API documentation at http://localhost:8000/docs

