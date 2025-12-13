# Testing Guide

Comprehensive testing guide for the AI Podcast Generator.

## Manual Testing Checklist

### Backend API Tests

#### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

#### 2. Discovery Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/discover \
  -H "Content-Type: application/json" \
  -d '{"topic": "artificial intelligence", "max_results": 5}'
```
**Expected:** JSON with list of YouTube videos

#### 3. Transcripts Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/transcripts \
  -H "Content-Type: application/json" \
  -d '{"video_ids": ["VIDEO_ID_HERE"]}'
```
**Expected:** JSON with video transcripts

#### 4. Analysis Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transcripts": [{
      "video_id": "test",
      "title": "Test",
      "transcript": "Sample transcript text...",
      "language": "en",
      "duration_seconds": 600
    }],
    "topic": "AI"
  }'
```
**Expected:** JSON with themes and analysis

#### 5. Get Available Voices
```bash
curl http://localhost:8000/api/v1/voices
```
**Expected:** JSON with list of ElevenLabs voices

### Frontend Tests

#### 1. Home Page
- [ ] Navigate to http://localhost:3000
- [ ] Verify landing page loads correctly
- [ ] Enter a topic and click "Generate"
- [ ] Verify redirect to /generate?topic=...

#### 2. Topic Step
- [ ] Topic input is pre-filled from URL
- [ ] Can switch between single/multi-host formats
- [ ] Visual indicators show selected format
- [ ] "Continue" button works

#### 3. References Step
- [ ] YouTube videos load automatically
- [ ] Video thumbnails display correctly
- [ ] Can select/deselect videos (max 5)
- [ ] Selection counter updates
- [ ] "Back" and "Continue" buttons work

#### 4. Outline Step
- [ ] Shows loading state during processing
- [ ] Displays content analysis summary
- [ ] Shows generated outline with sections
- [ ] Each section shows duration and key points
- [ ] Can proceed to script generation

#### 5. Script Step
- [ ] Shows loading state during generation
- [ ] Single-host: displays full script text
- [ ] Multi-host: displays alternating dialogue
- [ ] Script is readable and properly formatted
- [ ] Can proceed to audio generation

#### 6. Audio Step
- [ ] Shows loading state during TTS
- [ ] Audio player appears when ready
- [ ] Play/Pause button works
- [ ] Download button downloads MP3
- [ ] Can return to previous steps

## Integration Testing Scenarios

### Scenario 1: Single Host Podcast

1. **Start:** Home page with topic "Climate Change"
2. **Format:** Single host
3. **References:** Select 2-3 videos about climate change
4. **Expected Results:**
   - Outline with 4-6 sections
   - Single narrator script (~15 minutes)
   - Clear, professional audio output

### Scenario 2: Multi-Host Podcast

1. **Start:** Home page with topic "Space Exploration"
2. **Format:** Two hosts
3. **References:** Select 3-4 space podcasts
4. **Expected Results:**
   - Conversational outline
   - Dialogue script with HOST_1 and HOST_2
   - Audio with two distinct voices alternating

### Scenario 3: Short Podcast

1. **Topic:** "Quick Coffee Facts"
2. **References:** 1 short video
3. **Expected Results:**
   - Concise outline
   - ~5 minute script
   - Quick audio generation

## Error Handling Tests

### Test Invalid API Keys
1. Set invalid API key in `.env`
2. Try to discover videos
3. **Expected:** Error message displayed to user

### Test No Transcripts Available
1. Select videos without captions
2. **Expected:** Error message or skip to manual input

### Test Network Failures
1. Stop backend server
2. Try to use frontend
3. **Expected:** Graceful error handling, not crashes

### Test Empty Topic
1. Leave topic field empty
2. Try to continue
3. **Expected:** Button disabled or validation message

## Performance Tests

### Response Times (Expected)

| Step | Expected Time |
|------|--------------|
| Discovery | 2-5 seconds |
| Transcripts | 5-10 seconds |
| Analysis | 10-20 seconds |
| Outline | 15-30 seconds |
| Script | 30-90 seconds |
| TTS | 60-180 seconds |

### Load Testing
```bash
# Install Apache Bench
# Test discovery endpoint
ab -n 100 -c 10 -p post_data.json -T application/json \
  http://localhost:8000/api/v1/discover
```

## Automated Testing

### Backend Unit Tests
```bash
cd backend
pytest tests/
```

### Frontend Type Checking
```bash
cd frontend
npm run build  # Runs TypeScript check
```

## API Documentation Testing

1. Visit http://localhost:8000/docs
2. Test each endpoint using Swagger UI:
   - Try "Try it out" for each endpoint
   - Verify responses match schemas
   - Check error responses (400, 500)

## Browser Compatibility

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Mobile Responsive Testing

Test on:
- [ ] iPhone (iOS Safari)
- [ ] Android phone (Chrome)
- [ ] Tablet (iPad/Android)

Expected: UI should be usable on all devices

## Common Issues & Solutions

### Issue: Very slow response times
**Solution:** Check API quotas, use smaller video selections

### Issue: Audio quality poor
**Solution:** Check ElevenLabs voice settings, ensure good script quality

### Issue: Scripts are repetitive
**Solution:** Use more diverse reference videos, adjust prompts

### Issue: Outline doesn't match topic
**Solution:** Improve reference video selection, ensure relevant content

## Success Criteria

A successful test run should:
- ✅ Complete full pipeline in < 10 minutes
- ✅ Generate coherent, on-topic content
- ✅ Produce high-quality audio
- ✅ Handle errors gracefully
- ✅ Work across different topics
- ✅ Support both single and multi-host formats

