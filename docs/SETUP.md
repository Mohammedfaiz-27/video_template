# Setup Guide - Video Headline & Template Generator

Complete setup instructions for the Video Headline & Template Generator system.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Python 3.10 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify: `python --version`

2. **Node.js 18 or higher** (for frontend)
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version`

3. **MongoDB**
   - **Option A - Docker (Recommended)**:
     ```bash
     docker run -d -p 27017:27017 --name video-gen-mongodb mongo:7.0
     ```
   - **Option B - Local Installation**:
     - Download from [mongodb.com](https://www.mongodb.com/try/download/community)
     - Start service: `net start MongoDB` (Windows) or `sudo systemctl start mongod` (Linux)
   - **Option C - MongoDB Atlas** (Cloud):
     - Create free account at [mongodb.com/atlas](https://www.mongodb.com/atlas)
     - Get connection string

4. **FFmpeg**
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or install via Chocolatey:
     ```bash
     choco install ffmpeg
     ```
   - **Linux**:
     ```bash
     sudo apt-get install ffmpeg  # Ubuntu/Debian
     ```
   - **Mac**:
     ```bash
     brew install ffmpeg
     ```
   - Verify: `ffmpeg -version`

### API Keys Required

1. **Gemini API Key** (Required)
   - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Free tier available

2. **Perplexity API Key** (Optional)
   - Get from [Perplexity AI](https://www.perplexity.ai/)
   - Used for headline refinement

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd "F:\newsit\video template\backend"
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (web framework)
- Motor & PyMongo (MongoDB async driver)
- Pydantic (data validation)
- Google Generative AI (Gemini)
- FFmpeg-python (video processing)
- And other required packages

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit `.env` file and add your API keys:

```env
# API Keys
GEMINI_API_KEY=AIza...your_key_here
PERPLEXITY_API_KEY=pplx-...your_key_here  # optional

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

### Step 5: Start MongoDB

Choose one option:

**Docker (Recommended)**:
```bash
docker run -d -p 27017:27017 --name video-gen-mongodb mongo:7.0

# Check status
docker ps

# Stop (when needed)
docker stop video-gen-mongodb

# Start again
docker start video-gen-mongodb
```

**Local MongoDB**:
```bash
# Windows
net start MongoDB

# Linux
sudo systemctl start mongod

# Mac
brew services start mongodb-community
```

**MongoDB Atlas (Cloud)**:
- Update MONGODB_URL in .env with your Atlas connection string:
  ```
  MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
  ```

### Step 6: Start Backend Server

**Windows**:
```bash
start.bat
```

**Linux/Mac**:
```bash
./start.sh
```

**Manual Start**:
```bash
# Activate venv first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

### Step 7: Verify Backend is Running

Open browser and navigate to:
- **API Root**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

You should see:
```json
{
  "name": "Video Headline & Template Generator API",
  "version": "1.0.0",
  "status": "running"
}
```

---

## Frontend Setup (Coming Soon)

### Step 1: Navigate to Frontend Directory

```bash
cd "F:\newsit\video template\frontend"
```

### Step 2: Install Node Dependencies

```bash
npm install
```

### Step 3: Configure Environment Variables

```bash
# Create .env file
echo VITE_API_URL=http://localhost:8000/api > .env
```

### Step 4: Start Development Server

```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## Testing the System

### 1. Upload a Video

Using curl:
```bash
curl -X POST "http://localhost:8000/api/videos/upload" \
  -F "file=@path/to/your/video.mp4"
```

Response:
```json
{
  "video_id": "uuid-here",
  "status": "uploaded",
  "message": "Video uploaded successfully..."
}
```

### 2. Trigger Analysis

```bash
curl -X POST "http://localhost:8000/api/videos/{video_id}/analyze"
```

### 3. Check Status

```bash
curl "http://localhost:8000/api/videos/{video_id}/status"
```

### 4. Get Analysis Results

```bash
curl "http://localhost:8000/api/videos/{video_id}/analysis"
```

### 5. Trigger Rendering

```bash
curl -X POST "http://localhost:8000/api/videos/{video_id}/render" \
  -H "Content-Type: application/json" \
  -d '{"show_location": true}'
```

### 6. Download Processed Video

```bash
curl "http://localhost:8000/api/videos/{video_id}/download" -o processed.mp4
```

---

## Troubleshooting

### MongoDB Connection Error

**Error**: `pymongo.errors.ServerSelectionTimeoutError`

**Solutions**:
1. Ensure MongoDB is running:
   ```bash
   # Docker
   docker ps | grep mongo

   # Windows service
   sc query MongoDB

   # Linux
   sudo systemctl status mongod
   ```

2. Check MONGODB_URL in .env
3. Try connecting manually:
   ```bash
   mongosh mongodb://localhost:27017
   ```

### FFmpeg Not Found

**Error**: `FileNotFoundError: ffmpeg not found`

**Solutions**:
1. Verify FFmpeg is installed: `ffmpeg -version`
2. Add FFmpeg to system PATH
3. Restart terminal/command prompt after installation

### Virtual Environment Issues

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:
1. Ensure venv is activated:
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```
2. Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

**Error**: `Address already in use`

**Solutions**:
1. Change PORT in .env to a different value (e.g., 8001)
2. Kill process using port 8000:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F

   # Linux/Mac
   lsof -i :8000
   kill -9 <PID>
   ```

### Gemini API Errors

**Error**: `google.api_core.exceptions.PermissionDenied`

**Solutions**:
1. Verify API key is correct in .env
2. Check API quota at [Google AI Studio](https://makersuite.google.com/)
3. Ensure Gemini API is enabled

---

## Development Tips

### Viewing Logs

Backend logs are printed to console. Look for:
- `✓` Green checkmarks for successful operations
- `❌` Red X for errors
- `⚠️` Warnings

### Accessing MongoDB

```bash
# Connect with mongosh
mongosh mongodb://localhost:27017

# Use database
use video_generator

# View videos
db.videos.find().pretty()

# View specific video
db.videos.findOne({_id: "video_id_here"})
```

### Storage Directories

- Uploaded videos: `backend/storage/uploads/`
- Processed videos: `backend/storage/processed/`

These directories are gitignored and safe to delete for testing.

### Running Tests

```bash
# Activate venv
venv\Scripts\activate

# Run tests (when implemented)
pytest
```

---

## Production Deployment

For production deployment, see:
- `docs/DEPLOYMENT.md` (coming soon)

Quick checklist:
- Set `DEBUG=False` in .env
- Use production MongoDB (Atlas or dedicated server)
- Set up proper CORS origins
- Use environment secrets for API keys
- Configure reverse proxy (nginx/Apache)
- Set up SSL certificates
- Enable logging to files
- Set up monitoring

---

## Next Steps

After successful setup:

1. **Test Video Upload**: Try uploading a video via API docs
2. **Review Analysis Results**: Check headline and location detection
3. **Test Rendering**: Generate a 9:16 video with overlays
4. **Explore API Docs**: http://localhost:8000/docs
5. **Build Frontend**: Start developing the React interface

---

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check README.md and API docs
- **Logs**: Review console output for error details

## Useful Commands

```bash
# Backend commands
cd backend
venv\Scripts\activate          # Activate venv (Windows)
source venv/bin/activate       # Activate venv (Linux/Mac)
pip install -r requirements.txt  # Install dependencies
python -m uvicorn app.main:app --reload  # Start server

# MongoDB commands (Docker)
docker start video-gen-mongodb    # Start
docker stop video-gen-mongodb     # Stop
docker logs video-gen-mongodb     # View logs

# FFmpeg test
ffmpeg -i input.mp4 -t 5 test.mp4  # Convert first 5 seconds
```

---

**You're all set!** Start the backend server and begin processing videos.
