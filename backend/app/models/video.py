"""Video data models for MongoDB documents."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from bson import ObjectId


class VideoStatus(str, Enum):
    """Video processing status states."""
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    RENDERING = "rendering"
    COMPLETED = "completed"
    ERROR = "error"


class TranscriptData(BaseModel):
    """Video transcript data."""
    text: str
    language: str = "en"
    language_confidence: float = 0.0
    has_significant_audio: bool = True


class VisualAnalysis(BaseModel):
    """Visual content analysis data."""
    scene_type: str = ""
    people_count: int = 0
    objects: List[str] = []
    mood: str = ""
    landmarks: List[str] = []
    description: str = ""


class HeadlineData(BaseModel):
    """Generated headline data."""
    primary: str
    alternatives: List[str] = []
    confidence: float = 0.0
    tone: str = "neutral"


class LocationData(BaseModel):
    """Location detection data."""
    text: Optional[str] = None
    confidence: float = 0.0
    source: str = "none"  # gps, transcript, visual, user_input, none
    coordinates: Optional[Dict[str, float]] = None


class VideoDocument(BaseModel):
    """MongoDB video document structure."""

    # Identity
    id: Optional[str] = Field(default=None, alias="_id")
    filename: str
    original_filename: str

    # Status
    status: VideoStatus = VideoStatus.UPLOADED
    error_message: Optional[str] = None

    # File info
    original_path: str
    processed_path: Optional[str] = None
    file_size: int = 0
    duration: float = 0.0
    resolution: str = ""

    # Analysis
    transcript: Optional[TranscriptData] = None
    visual_analysis: Optional[VisualAnalysis] = None
    headline: Optional[HeadlineData] = None
    location: Optional[LocationData] = None

    # User overrides
    user_headline: Optional[str] = None
    user_location: Optional[str] = None
    show_location: bool = True

    # Metadata
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

    def get_final_headline(self) -> str:
        """Get the final headline (user override or generated)."""
        if self.user_headline:
            return self.user_headline
        if self.headline:
            return self.headline.primary
        return "Untitled Video"

    def get_final_location(self) -> Optional[str]:
        """Get the final location (user override or detected)."""
        if self.user_location:
            return self.user_location
        if self.location and self.location.text:
            return self.location.text
        return None
