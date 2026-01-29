# Development Guide

Quick reference for developers working on Character Replacement MVP.

## Project Architecture

```
┌─────────────────────────────────────────────────┐
│           Frontend (Vanilla JS)                 │
│  ├─ Upload (file/URL modes)                     │
│  ├─ Presets (TikTok, Instagram, YouTube, Pro)   │
│  ├─ Settings (ratio, intensity, body control)   │
│  ├─ Gallery (localStorage, max 20 items)        │
│  ├─ Comparison (draggable slider, sync videos)  │
│  └─ Download                                    │
├─────────────────────────────────────────────────┤
│           FastAPI Backend (Python)              │
│  ├─ /api/upload (multipart file upload)         │
│  ├─ /api/generate (create generation task)      │
│  ├─ /api/status/{task_id} (check progress)      │
│  ├─ Cloudinary Service (file storage)           │
│  └─ Freepik Service (API integration)           │
├─────────────────────────────────────────────────┤
│           External Services                     │
│  ├─ Cloudinary (image/video storage)            │
│  └─ Freepik Runway Act Two API (generation)     │
└─────────────────────────────────────────────────┘
```

## Key Files

### Frontend
| File | Lines | Purpose |
|------|-------|---------|
| `app.js` | ~950 | Main application logic, all features |
| `index.html` | ~275 | UI structure and modals |
| `styles.css` | ~560 | Responsive styling + animations |

### Backend
| File | Purpose |
|------|---------|
| `main.py` | FastAPI routes and server |
| `models.py` | Pydantic request/response schemas |
| `config.py` | Environment variable loading |
| `services/cloudinary_service.py` | File upload/storage |
| `services/freepik_service.py` | API client and polling logic |

## Feature Breakdown

### 1. Presets (app.js: ~50 lines)
```javascript
// Location: lines 5-39
const PRESETS = {
    tiktok: { ratio: '720:1280', expression_intensity: 5, ... },
    instagram: { ratio: '960:960', expression_intensity: 4, ... },
    youtube: { ratio: '1280:720', expression_intensity: 3, ... },
    professional: { ratio: '1280:720', expression_intensity: 2, ... }
};

// Function: applyPreset(presetKey)
// Updates form values and applies visual feedback
```

### 2. Gallery (app.js: ~300 lines)
```javascript
// Location: lines 550-850
// localStorage schema:
{
    generations: [
        {
            id: "uuid",
            timestamp: "ISO8601",
            character_url: "https://...",
            reference_url: "https://...",
            result_url: "https://...",
            settings: { ratio, expression_intensity, body_control },
            thumbnail: "data:image/jpeg;base64,..."
        }
    ]
}

// Main functions:
- saveToGallery(videoUrl)
- generateThumbnail(videoUrl)
- loadGallery()
- renderGallery(generations)
- showGalleryItem(id)
- deleteFromGallery(id)
```

### 3. Before/After Comparison (app.js: ~150 lines)
```javascript
// Location: lines 820-970
// Main functions:
- initComparisonSlider()      // Draggable slider logic
- syncVideos()                 // Keep videos in sync
- toggleView(view)             // Toggle between views
- toggleComparisonPlayback()   // Play/pause control

// HTML structure:
.comparison-wrapper
  ├─ .video-side-left (50% width)
  │  ├─ video#reference-comparison-video
  │  └─ .video-label ("Reference")
  ├─ .video-side-right (flex: 1)
  │  ├─ video#result-comparison-video
  │  └─ .video-label ("Generated")
  └─ #comparison-slider (draggable divider)
```

## Common Tasks

### Adding a New Setting
1. Add form input to `index.html` settings section
2. Update `app.js` state variables
3. Pass to `/api/generate` endpoint
4. Handle in backend `models.py`
5. Implement in `freepik_service.py`

### Modifying Presets
1. Edit `PRESETS` object in `app.js` (line 6-39)
2. Add/remove preset properties as needed
3. Update `applyPreset()` if new fields needed
4. Add/remove buttons from `index.html` presets-grid

### Styling Changes
1. Edit `styles.css`
2. Use existing color variables: `#667eea` (primary), `#764ba2` (secondary)
3. Maintain mobile responsiveness (@media max-width: 768px)
4. Test on mobile viewport (DevTools)

## API Flow

```
User Action              Frontend              Backend              External
─────────────────────────────────────────────────────────────────────────────

[Upload files] ──POST /api/upload──> main.py ──────> Cloudinary
                                    └─ cloudinary_service.py
                        ←── upload_id, URLs ──────────┘

[Click Generate] ──POST /api/generate─> main.py
                  (settings)          └─ models.py (validate)
                  ←── task_id, status ──┘

[Poll status]    ──GET /api/status/{task_id}──> freepik_service.py
(3s interval)                      └─ Freepik API ──────> Freepik
                                    ←─ status, progress ──┘
                  ←── status, progress ──────────┘

[Generate complete] ←── result_url ─────────────────────┘
[Show in comparison] ←── Display in app
[Save to gallery] ──> browser localStorage
```

## Performance Tips

### Frontend Optimization
- **Gallery thumbnail generation**: Use canvas at 0.5 seconds into video
- **Comparison slider**: Use 60fps with requestAnimationFrame
- **Video sync**: Re-sync every 5 seconds to prevent drift
- **Storage**: Keep only last 20 generations, compress to JPEG quality 0.7

### Backend Optimization
- **Polling interval**: 3 seconds is good balance between responsiveness and load
- **Timeout**: Set 30-minute timeout for long generations
- **Error handling**: Return meaningful error messages

### API Optimization
- **Cloudinary**: Use folders for organization, set auto-delete for cleanup
- **Freepik**: Respect rate limits, implement exponential backoff

## Debugging

### Browser Console
```javascript
// Check localStorage
JSON.parse(localStorage.getItem('generations'))

// Check current state
console.log({ characterUrl, referenceUrl, taskId })

// Test API
fetch('http://localhost:8000/api/status/your-task-id')
  .then(r => r.json())
  .then(console.log)
```

### Backend Logging
```python
# In main.py or services
import logging
logging.info(f"Generation started: {task_id}")
logging.error(f"Upload failed: {error}")
```

### Network Debugging
1. Open DevTools > Network tab
2. Filter by XHR
3. Check request/response for API calls
4. Look for CORS issues if requests fail

## Testing Checklist

### Before Committing
- [ ] No console errors (`console.log()` removed)
- [ ] localStorage doesn't exceed 5-10MB
- [ ] All event listeners properly cleaned up
- [ ] Mobile responsive (test at 375px width)
- [ ] No hardcoded values (use variables)
- [ ] Commit messages follow convention

### Before Release
- [ ] All 3 features work independently
- [ ] Features work together seamlessly
- [ ] Error handling for edge cases
- [ ] Performance tested with large files
- [ ] Security review (no XSS vulnerabilities)
- [ ] Documentation updated

## Environment Variables

**Required:**
- `FREEPIK_API_KEY` - Freepik API credentials
- `CLOUDINARY_CLOUD_NAME` - Cloudinary account
- `CLOUDINARY_API_KEY` - Cloudinary credentials
- `CLOUDINARY_API_SECRET` - Cloudinary credentials

**Optional:**
- `PORT` - Backend port (default: 8000)
- `FRONTEND_URL` - Frontend URL for CORS (default: http://localhost:3000)

## File Size Limits

- **Images**: Recommended max 5MB (Cloudinary)
- **Videos**: Recommended max 100MB (depends on API)
- **Gallery storage**: Max 10-20 items (~50-100MB total)

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile: iOS Safari 14+, Chrome Mobile

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Cloudinary Docs](https://cloudinary.com/documentation)
- [Freepik API Docs](https://developers.freepik.com/)
- [MDN Web Docs](https://developer.mozilla.org/)

---

**Need help?** Check CONTRIBUTING.md or open an issue!
