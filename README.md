# 🎬 Character Replacement MVP

Transform characters in videos using AI-powered face replacement technology. Upload a character image and a reference video, and let the Runway Act Two API do the magic.

<div align="center">
  <strong>Presets • Gallery • Before/After Comparison</strong>
</div>

---

## Features

### Core Functionality
- **Face Replacement** - Transform faces in videos with precision
- **Dual Upload Modes** - Upload files or paste URLs directly
- **Real-time Progress** - Live status updates with visual feedback
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
- Cloudinary for reliable file storage
- Freepik Runway Act Two API for video generation

**Frontend:**
- Vanilla JavaScript (no dependencies)
- CSS3 with animations and responsive design
- localStorage for gallery persistence
- HTML5 with semantic markup

---

## Quick Start

### Prerequisites
- Python 3.8+ with pip
- Modern web browser
- Cloudinary account (free tier available)
- Freepik API key

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
2. Upload character image (JPG, PNG, WebP) or paste URL
3. Upload reference video (MP4, MOV) or paste URL
4. *(Optional)* Apply a preset or customize settings
5. Click "🚀 Generate Video"
6. Wait for generation to complete
7. Preview using the interactive comparison slider
8. Download or save to gallery

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
  "settings": {
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
  "progress_stage": "Ready"
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
│   │   └── freepik_service.py     # Runway API client
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
