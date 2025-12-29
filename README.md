# Video Headline & Template Generator

AI-powered video processing system that generates engaging headlines, detects locations, and transforms videos to 9:16 aspect ratio with text overlays.

## Features

- **AI-Powered Analysis**: Uses Gemini API for video transcript, visual analysis, and headline generation
- **Automatic Headline Generation**: Creates engaging, click-worthy headlines based on video content
- **Location Detection**: Extracts location information from video content
- **9:16 Format Conversion**: Transforms videos to vertical format (1080x1920) for social media
- **Text Overlays**: Adds headline and location overlays to processed videos
- **RESTful API**: Complete backend API built with FastAPI
- **React Frontend**: Modern web interface for video upload and editing (coming soon)

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: Database with Motor async driver
- **Gemini API**: Google's generative AI for video analysis
- **FFmpeg**: Video processing and transformation
- **Pydantic**: Data validation and settings management

### Frontend (Planned)
- **React 18**: UI library
- **Vite**: Build tool
- **React Router**: Navigation
- **Axios**: HTTP client

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **MongoDB** (local or cloud)
- **FFmpeg** (installed and in PATH)
- **Gemini API Key** (from Google AI Studio)

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd "video template"
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=video_generator
```

#### Start MongoDB

**Option A: Docker**
```bash
docker run -d -p 27017:27017 --name video-gen-mongodb mongo:7.0
```

**Option B: Local MongoDB**
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

#### Run Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### 3. Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5173

## Project Structure

```
video template/
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # MongoDB connection
│   │   ├── models/
│   │   │   └── video.py         # Data models
│   │   ├── schemas/
│   │   │   └── video.py         # API schemas
│   │   ├── services/
│   │   │   └── storage_service.py  # File handling
│   │   └── routes/
│   │       └── video.py         # API endpoints
│   ├── storage/
│   │   ├── uploads/             # Original videos
│   │   └── processed/           # Processed videos
│   ├── requirements.txt
│   └── .env
│
├── frontend/                     # React frontend (coming soon)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
└── README.md
```

## API Endpoints

### Upload Video
```
POST /api/videos/upload
Content-Type: multipart/form-data

Body: file (video file)
```

### Get Video Status
```
GET /api/videos/{video_id}/status
```

### Trigger Analysis
```
POST /api/videos/{video_id}/analyze
```

### Get Analysis Results
```
GET /api/videos/{video_id}/analysis
```

### Update Metadata
```
PATCH /api/videos/{video_id}/metadata
Content-Type: application/json

Body:
{
  "headline": "New headline here",
  "location": "New location",
  "show_location": true
}
```

### Trigger Rendering
```
POST /api/videos/{video_id}/render
Content-Type: application/json

Body:
{
  "headline": "Override headline",
  "location": "Override location",
  "show_location": true
}
```

### Get Output Info
```
GET /api/videos/{video_id}/output
```

### Download Processed Video
```
GET /api/videos/{video_id}/download
```

## Workflow

1. **Upload Video**: POST video file to `/api/videos/upload`
2. **Trigger Analysis**: POST to `/api/videos/{id}/analyze` to start AI processing
3. **Poll Status**: GET `/api/videos/{id}/status` to monitor progress
4. **Get Analysis**: GET `/api/videos/{id}/analysis` to see results
5. **Edit Metadata** (Optional): PATCH `/api/videos/{id}/metadata` to customize headline/location
6. **Trigger Render**: POST `/api/videos/{id}/render` to create final video
7. **Download**: GET `/api/videos/{id}/download` to get processed video

## Development Status

### ✅ Completed (Phase 1)
- [x] Project structure setup
- [x] Backend core framework (FastAPI)
- [x] MongoDB integration
- [x] Video upload endpoint
- [x] Storage service
- [x] API routes and schemas
- [x] Configuration management

### 🚧 In Progress
- [ ] Gemini AI integration
- [ ] FFmpeg video processing
- [ ] Background task workers

### 📋 Planned
- [ ] Perplexity API integration (optional)
- [ ] React frontend
- [ ] End-to-end testing
- [ ] Deployment configuration
- [ ] Advanced error handling
- [ ] WebSocket status updates
- [ ] Cloud storage (S3) support

## Configuration

All configuration is managed through environment variables in `backend/.env`:

```env
# API Keys
GEMINI_API_KEY=your_key
PERPLEXITY_API_KEY=your_key  # optional

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=video_generator

# Storage
UPLOAD_DIR=./storage/uploads
PROCESSED_DIR=./storage/processed
MAX_FILE_SIZE=524288000  # 500MB

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Troubleshooting

### MongoDB Connection Error
```
pymongo.errors.ServerSelectionTimeoutError
```
**Solution**: Ensure MongoDB is running and accessible at the configured URL.

### FFmpeg Not Found
```
FileNotFoundError: ffmpeg not found
```
**Solution**: Install FFmpeg and ensure it's in your system PATH.

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Activate virtual environment and install dependencies:
```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue on GitHub.

## Acknowledgments

- Google Gemini API for AI-powered video analysis
- FastAPI framework
- MongoDB for database
- FFmpeg for video processing
