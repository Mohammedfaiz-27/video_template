"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Database, create_indexes
from app.routes import video


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("\n" + "="*50)
    print("🚀 Starting Video Headline & Template Generator API")
    print("="*50)

    # Ensure storage directories exist
    settings.ensure_directories()
    print(f"✓ Storage directories configured")
    print(f"  - Uploads: {settings.upload_path}")
    print(f"  - Processed: {settings.processed_path}")

    # Connect to MongoDB
    await Database.connect_db()

    # Create database indexes
    await create_indexes()

    print("="*50)
    print(f"✓ Server ready at http://{settings.HOST}:{settings.PORT}")
    print(f"✓ API docs at http://{settings.HOST}:{settings.PORT}/docs")
    print("="*50 + "\n")

    yield

    # Shutdown
    print("\n🛑 Shutting down server...")
    await Database.close_db()
    print("✓ Server shutdown complete\n")


# Create FastAPI app
app = FastAPI(
    title="Video Headline & Template Generator API",
    description="AI-powered video processing API for generating headlines and converting videos to 9:16 format",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Video Headline & Template Generator API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /api/videos/upload",
            "status": "GET /api/videos/{video_id}/status",
            "analyze": "POST /api/videos/{video_id}/analyze",
            "analysis": "GET /api/videos/{video_id}/analysis",
            "update_metadata": "PATCH /api/videos/{video_id}/metadata",
            "render": "POST /api/videos/{video_id}/render",
            "output": "GET /api/videos/{video_id}/output",
            "download": "GET /api/videos/{video_id}/download"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected" if Database.db is not None else "disconnected"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    print(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
