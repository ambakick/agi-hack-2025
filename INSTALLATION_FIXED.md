# Installation Issues Fixed ✅

## Problems Encountered

### 1. Zsh `deactivate` Alias Conflict
**Error:** `defining function based on alias 'deactivate'`

**Cause:** Conda/Anaconda defines `deactivate` as an alias in zsh, conflicts with Python venv's `deactivate()` function

**Fix:** Run before activating venv:
```bash
unalias deactivate 2>/dev/null
source venv/bin/activate
```

### 2. Dependency Resolution Backtracking
**Error:** `pip is looking at multiple versions of grpcio-status...`

**Cause:** Old `google-generativeai==0.3.2` had tight version constraints causing pip to test ~30 versions

**Fix:** Updated `requirements.txt` with:
- Newer Google packages (`google-generativeai>=0.8.0`)
- Pinned `grpcio>=1.62.0` and `grpcio-status>=1.62.0`
- Changed from exact versions (`==`) to minimum versions (`>=`)

### 3. Network Timeouts
**Error:** `ReadTimeoutError: ... Read timed out`

**Cause:** Slow Wi-Fi connection, default pip timeout too short

**Fix:** 
- Increased timeout: `--timeout 180`
- Added retries: `--retries 10`
- Recreated venv with system Python (not Anaconda)

### 4. Anaconda Python Conflicts
**Issue:** venv created with Anaconda's Python caused import issues

**Fix:** Recreated venv using system Python:
```bash
rm -rf venv
/usr/bin/python3 -m venv venv
```

## Final Working Installation

```bash
cd backend

# Remove old venv
rm -rf venv

# Create clean venv with system Python
/usr/bin/python3 -m venv venv

# Upgrade pip
./venv/bin/pip install --upgrade pip

# Install with extended timeout
./venv/bin/pip install --timeout 180 --retries 10 -r requirements.txt

# Activate (workaround for zsh)
unalias deactivate 2>/dev/null
source venv/bin/activate

# Verify
python -c "from app.main import app; print('✓ Backend ready!')"
```

## Backend Status

✅ **All dependencies installed successfully**
✅ **FastAPI app loads without errors**
✅ **YouTube service imports correctly**
✅ **Ready to run with `uvicorn app.main:app --reload`**

## Warnings (Non-Critical)

- Python 3.9.6 end-of-life warning (Google APIs)
- LibreSSL vs OpenSSL warning (urllib3)

These warnings don't prevent the app from running. For production, consider upgrading to Python 3.11+.

## Next Steps

1. **Copy `.env.example` to `.env`**:
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`**:
   - YOUTUBE_API_KEY
   - GEMINI_API_KEY
   - ELEVENLABS_API_KEY

3. **Start the backend**:
   ```bash
   ./venv/bin/uvicorn app.main:app --reload
   ```

4. **Visit**: http://localhost:8000/docs

## Updated Files

- `backend/requirements.txt` - Fixed dependency versions
- `backend/app/services/elevenlabs.py` - Updated for ElevenLabs v2.x API

## Time Saved

The fixes reduced:
- Dependency resolution from 3+ minutes to <1 minute
- Installation failures from network timeouts
- Shell activation conflicts with Conda

