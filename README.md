# 🎬 Character Replacement MVP

Transform characters in videos using AI-powered face replacement. Use Runway Act Two directly, or a 3-step pipeline (Seedream 4 Edit → Runway Act Two) for stronger identity transfer.

<div align="center">
  <strong>Presets • Gallery • Before/After Comparison</strong>
</div>

---

## Features

### Core Functionality
- **Face Replacement** - Transform faces in videos with precision
- **URL Inputs** - Paste image/video URLs (file upload UI is currently disabled)
- **Model Selection** - Runway Act Two (single step) or Seedream 4 Edit + Runway Act Two (3 steps)
- **Real-time Progress** - Live status updates with pipeline stages
- **Download Results** - Export generated videos in MP4 format

### Polish & UX Features
- **Smart Presets** - One-click configuration for TikTok, Instagram, YouTube, and Professional formats
- **Generation Gallery** - Browse and manage your last 20 generations with local storage
- **Before/After Comparison** - Interactive slider to compare reference vs generated videos with synchronized playback
- **Customizable Settings** - Fine-tune expression intensity (1-5) and body control options

### Advanced Options
- **Multiple Aspect Ratios** - Support for 16:9, 9:16, 1:1, 4:3, 3:4, 21:9
- **Body Motion Control** - Toggle between full body motion or face-only
- **Expression Intensity** - Scale emotional expressions from subtle to dramatic

---

## Architecture

**Backend:**
- Python 3.8+
- FastAPI with async support
- Freepik Runway Act Two for video generation
- Seedream 4 Edit for identity replacement in frame (pipeline mode)
- Cloudinary upload endpoint (optional; UI currently uses URLs)

**Frontend:**
- Vanilla JavaScript (no dependencies)
- CSS3 with animations and responsive design
- localStorage for gallery persistence
- HTML5 with semantic markup
- Client-side frame extraction for pipeline mode

---

## Quick Start

### Prerequisites
- Python 3.8+ with pip
- Modern web browser
- Freepik API key
- Cloudinary account (required by backend validation even if you use URL-only mode)

### 1. Get Cloudinary Credentials

1. Sign up at [cloudinary.com](https://cloudinary.com) (free tier)
2. Copy from Dashboard:
   - Cloud name
   - API Key
   - API Secret

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

**backend/.env:**
```env
MOCK_MODE=false
FREEPIK_API_KEY=your_api_key_here
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Backend: [http://localhost:8000](http://localhost:8000)

### 4. Start Frontend

In another terminal:

```bash
cd frontend
python3 -m http.server 3000
```

Frontend: [http://localhost:3000](http://localhost:3000)

### 5. Use the App

1. Open [http://localhost:3000](http://localhost:3000)
2. Paste character image URL (JPG, PNG, WebP)
3. Paste reference video URL (MP4, MOV)
4. Select model: **Runway Act Two** or **Seedream 4 Edit + Runway Act Two**
5. *(Optional)* Apply a preset or customize settings
6. Click "🚀 Generate Video"
7. Wait for generation to complete
8. Preview using the interactive comparison slider
9. Download or save to gallery

---

## API Endpoints

### POST /api/upload
Upload files to Cloudinary

**Request:**
```json
{
  "character": "<image_file>",
  "reference": "<video_file>"
}
```

**Response:**
```json
{
  "upload_id": "uuid",
  "character_url": "https://...",
  "reference_url": "https://..."
}
```

### POST /api/generate
Create generation task

**Request:**
```json
{
  "upload_id": "uuid",
  "direct_urls": {
    "character_url": "https://...",
    "reference_url": "https://..."
  },
  "frame_url": "data:image/jpeg;base64,...",
  "settings": {
    "model": "runway_act_two",
    "ratio": "720:1280",
    "expression_intensity": 3,
    "body_control": true
  }
}
```

**Response:**
```json
{
  "task_id": "uuid",
  "status": "CREATED"
}
```

### GET /api/status/{task_id}
Check task status

**Response:**
```json
{
  "task_id": "uuid",
  "status": "READY",
  "result_urls": ["https://..."],
  "progress_stage": "Ready",
  "pipeline_stage": "VIDEO_STARTED",
  "intermediate_url": "https://...",
  "model_used": "seedream_runway"
}
```

---

## Project Structure

```
character-replacement-mvp/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── models.py                  # Pydantic request/response models
│   ├── config.py                  # Environment configuration
│   ├── services/
│   │   ├── cloudinary_service.py  # Cloudinary upload/storage
│   │   └── freepik_service.py     # Runway + Seedream API client
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Environment template
│
├── frontend/
│   ├── index.html                 # User interface
│   ├── app.js                     # Application logic + features
│   └── styles.css                 # Styling & animations
│
├── .gitignore
└── README.md
```

---

## Feature Highlights

### Smart Presets
Pre-configured settings for popular platforms:
- **TikTok**: 9:16 portrait, high energy (intensity 5)
- **Instagram**: 1:1 square, engaging (intensity 4)
- **YouTube**: 16:9 widescreen, natural (intensity 3)
- **Professional**: 16:9 widescreen, subtle (intensity 2)

### Gallery & History
- Automatic saving to browser storage
- Thumbnail previews of generated videos
- View generation settings used
- Download from history
- Maximum 20 recent generations

### Before/After Comparison
- Split-screen interactive comparison
- Draggable slider for side-by-side viewing
- Synchronized playback of both videos
- Mobile-friendly touch controls
- Toggle between comparison and single view

---

## Configuration

### Video Settings
| Option | Range | Description |
|--------|-------|-------------|
| **Aspect Ratio** | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 | Output video format |
| **Expression Intensity** | 1-5 | How pronounced the expressions are |
| **Body Control** | On/Off | Include body motion from reference |

### Supported Formats
| Type | Formats |
|------|---------|
| **Images** | JPG, PNG, WebP |
| **Videos** | MP4, MOV |

---

## Troubleshooting

### Backend Issues
```
Backend won't start?
- Check Python version: python3 --version (need 3.8+)
- Activate venv: source venv/bin/activate
- Verify .env file has all variables
```

### Upload Errors
```
Upload fails?
- Check Cloudinary credentials in .env
- Verify file formats (jpg/png/webp for images, mp4/mov for videos)
- Ensure files aren't corrupted
```

### Generation Issues
```
Generation fails?
- Check Freepik API key in .env
- Verify face is clearly visible in character image
- Try a different reference video
- Check internet connection
```

### CORS Problems
```
CORS error in browser console?
- Confirm backend runs on port 8000
- Verify frontend calls http://localhost:8000
- Check browser developer tools > Network tab
```

---

## Technical Specifications

### Performance
- Frontend bundle size: ~50KB (HTML + CSS + JS)
- Generation time: 2-5 minutes (depends on video length)
- localStorage limit: ~5-10MB per domain
- Max gallery items: 20 (configurable)

### Browser Support
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## 🛣️ Roadmap

Post-MVP enhancements:
- [ ] SQLite persistence for unlimited history
- [ ] Webhook support for background processing
- [ ] Batch video processing
- [ ] User feedback system (👍👎)
- [ ] Advanced settings (lighting, detail level)
- [ ] Cloud deployment (Railway/Render)
- [ ] Video timeline editor
- [ ] API rate limiting & authentication

---

## 📝 License

MIT License - feel free to use for personal and commercial projects.

---

## 🤝 Contributing

Found a bug or have an idea? Create an issue or submit a pull request.

---

## ❓ FAQ

**Q: Can I process multiple videos at once?**
A: Currently processes one video at a time. Batch processing is on the roadmap.

**Q: How long do generations take?**
A: Typically 2-5 minutes depending on video length and API load.

**Q: Is my data stored?**
A: Videos are stored temporarily in Cloudinary. Gallery is stored in browser localStorage.

**Q: Can I use commercial videos?**
A: Check Freepik's terms. The feature is designed for personal use.

**Q: What's the quality like?**
A: Results depend on source material quality. Ensure good lighting and clear face visibility.

---

<div align="center">
  <strong>Made with ❤️ using FastAPI & Vanilla JS</strong>
</div>
