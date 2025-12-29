"""API request and response schemas."""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from app.models.video import VideoStatus, TranscriptData, VisualAnalysis, HeadlineData, LocationData


# Upload Schemas
class VideoUploadResponse(BaseModel):
    """Response after video upload."""
    video_id: str
    status: VideoStatus
    message: str = "Video uploaded successfully. Processing will begin shortly."


# Status Schemas
class VideoStatusResponse(BaseModel):
    """Video processing status response."""
    video_id: str
    status: VideoStatus
    progress_percent: int = 0
    stage: str = "upload"  # upload, analysis, render, finalizing
    error: Optional[str] = None


# Analysis Schemas
class VideoAnalysisResponse(BaseModel):
    """Video analysis results response."""
    video_id: str
    transcript: Optional[TranscriptData] = None
    visual_analysis: Optional[VisualAnalysis] = None
    headline: Optional[HeadlineData] = None
    location: Optional[LocationData] = None


# Metadata Update Schemas
class MetadataUpdateRequest(BaseModel):
    """Request to update video metadata."""
    headline: Optional[str] = Field(None, min_length=5, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=50)
    show_location: Optional[bool] = None


class MetadataUpdateResponse(BaseModel):
    """Response after metadata update."""
    video_id: str
    headline: str
    location: Optional[str] = None
    show_location: bool


# Render Schemas
class RenderRequest(BaseModel):
    """Request to render video."""
    headline: Optional[str] = Field(None, min_length=5, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=50)
    show_location: bool = True


class RenderResponse(BaseModel):
    """Response after render initiation."""
    video_id: str
    status: VideoStatus
    message: str = "Video rendering started"


# Output/Download Schemas
class VideoOutputResponse(BaseModel):
    """Final video output information."""
    video_id: str
    final_resolution: str
    aspect_ratio: str = "9:16"
    file_size_mb: float
    download_url: str
    preview_url: Optional[str] = None
    headline: str
    location: Optional[str] = None
    show_location: bool
    created_at: datetime


# Error Schema
class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    video_id: Optional[str] = None
