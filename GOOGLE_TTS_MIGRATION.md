# Google Cloud Text-to-Speech Migration - Complete

## Summary

Successfully migrated from ElevenLabs to Google Cloud Text-to-Speech API with Neural2 voices.

## Changes Made

### 1. Dependencies
- ✅ Updated `backend/requirements.txt` - replaced `elevenlabs>=1.0.0` with `google-cloud-texttospeech>=2.14.0`
- ✅ Updated `video-api/requirements.txt` - same dependency change

### 2. Service Layer
- ✅ Created `backend/app/services/google_tts.py` - new GoogleTTSService class
- ✅ Updated `video-api/app/services/audio_service.py` - migrated to Google TTS
- ✅ Removed `backend/app/services/elevenlabs.py` - old service deleted

### 3. Configuration
- ✅ Updated `backend/app/core/config.py` - changed `elevenlabs_api_key` to `google_tts_api_key`
- ✅ Updated `video-api/app/core/config.py` - same configuration change

### 4. API Layer
- ✅ Updated `backend/app/api/v1/deps.py` - new dependency injection for GoogleTTSService
- ✅ Updated `backend/app/api/v1/tts.py` - migrated endpoints to use Google TTS
- ✅ Updated `backend/app/services/__init__.py` - updated exports

### 5. Environment Configuration
- ✅ Updated `backend/env.example` - changed `ELEVENLABS_API_KEY` to `GOOGLE_TTS_API_KEY`
- ✅ Updated `video-api/.env.example` - same change

### 6. Documentation
- ✅ Updated `README.md` - all references to ElevenLabs changed to Google Cloud TTS
- ✅ Updated `QUICKSTART.md` - environment variable name updated
- ✅ Updated `.cursor/rules/01-project-overview.mdc` - technology stack updated
- ✅ Updated `.cursor/rules/04-current-focus.mdc` - API keys and tech stack updated
- ✅ Updated `docs/API_INTEGRATIONS.md` - complete section rewritten for Google TTS

### 7. Testing
- ✅ Created `backend/test_google_tts.py` - comprehensive test script

## Voice Configuration

### Default Voices (Neural2)
- **HOST_1**: `en-US-Neural2-F` (Female, warm and professional)
- **HOST_2**: `en-US-Neural2-J` (Male, conversational and friendly)

### Alternative Voices
- Female: `en-US-Neural2-C`, `en-US-Neural2-E`, `en-US-Neural2-G`
- Male: `en-US-Neural2-A`, `en-US-Neural2-D`, `en-US-Neural2-I`

## Next Steps

### 1. Update Your Environment File

**IMPORTANT**: You need to update your `.env` file before the server will start.

```bash
cd backend
```

Edit your `.env` file and change:
```bash
ELEVENLABS_API_KEY=your_key_here
```

To:
```bash
GOOGLE_TTS_API_KEY=your_key_here
```

### 2. Install New Dependencies

```bash
cd backend
pip install -r requirements.txt
```

```bash
cd video-api
pip install -r requirements.txt
```

### 3. Get Google Cloud TTS API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Cloud Text-to-Speech API"
4. Go to "APIs & Services" > "Credentials"
5. Create an API key
6. Copy the API key and update your `.env` file

### 4. Test the Integration

Run the test script to verify everything works:

```bash
cd backend
python test_google_tts.py
```

This will:
- List available Neural2 voices
- Generate a single-host audio sample
- Generate a multi-host audio sample
- Save test files: `test_single_host.mp3` and `test_multi_host.mp3`

### 5. Start the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The server should now start without errors.

## API Compatibility

The API endpoints remain unchanged:
- `POST /api/v1/tts` - Convert script to audio
- `GET /api/v1/voices` - List available voices

The request/response format is identical, so your frontend code doesn't need any changes.

## Benefits of Google Cloud TTS

✅ **Cost-effective**: $16 per million characters (Neural2)  
✅ **High quality**: Natural-sounding Neural2 voices  
✅ **Integrated ecosystem**: Already using Google Gemini and Veo  
✅ **Reliable**: Enterprise-grade SLA and uptime  
✅ **Scalable**: No strict rate limits with proper API key  

## Pricing Comparison

| Provider | Model | Price per 1M chars |
|----------|-------|-------------------|
| Google TTS | Neural2 | $16 |
| ElevenLabs | Turbo v2.5 | ~$30 (Pro tier) |

## Audio Quality

Google Neural2 voices provide:
- Natural prosody and intonation
- Clear pronunciation
- Good emotion and emphasis
- Suitable for podcast production

## Troubleshooting

### Server Won't Start
- Check that `.env` file has `GOOGLE_TTS_API_KEY` (not `ELEVENLABS_API_KEY`)
- Verify API key is valid
- Run `pip install -r requirements.txt` to install new dependencies

### API Errors
- Enable "Cloud Text-to-Speech API" in Google Cloud Console
- Check API key permissions
- Verify quota limits haven't been exceeded

### Audio Quality Issues
- Try different Neural2 voices (see alternatives above)
- Adjust speaking_rate (0.8-1.2 recommended for podcasts)
- Adjust pitch if needed (-2.0 to 2.0)

## Migration Complete ✅

All code has been successfully migrated from ElevenLabs to Google Cloud Text-to-Speech API. The system maintains the same functionality while benefiting from Google's ecosystem integration.
