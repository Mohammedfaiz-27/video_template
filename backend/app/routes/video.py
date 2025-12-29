"""Video API endpoints."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from bson import ObjectId

from app.database import get_videos_collection
from app.models.video import VideoDocument, VideoStatus
from app.schemas.video import (
    VideoUploadResponse,
    VideoStatusResponse,
    VideoAnalysisResponse,
    MetadataUpdateRequest,
    MetadataUpdateResponse,
    RenderRequest,
    RenderResponse,
    VideoOutputResponse,
    ErrorResponse
)
from app.services.storage_service import StorageService
from app.workers import analyze_video_task, render_video_task

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("/upload", response_model=VideoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a video file for processing.

    Args:
        file: Video file (mp4, mov, avi, mkv)
        background_tasks: FastAPI background tasks

    Returns:
        VideoUploadResponse with video_id and status
    """
    try:
        # Save file to storage
        video_id, file_path, file_size = await StorageService.save_uploaded_file(file)

        # Create MongoDB document
        video_doc = VideoDocument(
            id=video_id,
            filename=f"{video_id}{Path(file.filename).suffix}",
            original_filename=file.filename,
            status=VideoStatus.UPLOADED,
            original_path=file_path,
            file_size=file_size,
            upload_timestamp=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Insert into database
        collection = get_videos_collection()
        doc_dict = video_doc.model_dump(by_alias=True, exclude={"id"})
        doc_dict["_id"] = video_id
        await collection.insert_one(doc_dict)

        # TODO: Trigger analysis in background
        # background_tasks.add_task(analyze_video_task, video_id)

        return VideoUploadResponse(
            video_id=video_id,
            status=VideoStatus.UPLOADED,
            message="Video uploaded successfully. Call /analyze endpoint to start processing."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(video_id: str):
    """
    Get current processing status of a video.

    Args:
        video_id: Video ID

    Returns:
        VideoStatusResponse with current status
    """
    collection = get_videos_collection()
    video = await collection.find_one({"_id": video_id})

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Calculate progress based on status
    progress_map = {
        VideoStatus.UPLOADED: 10,
        VideoStatus.ANALYZING: 40,
        VideoStatus.ANALYZED: 70,
        VideoStatus.RENDERING: 90,
        VideoStatus.COMPLETED: 100,
        VideoStatus.ERROR: 0
    }

    # Determine stage
    stage_map = {
        VideoStatus.UPLOADED: "upload",
        VideoStatus.ANALYZING: "analysis",
        VideoStatus.ANALYZED: "analysis",
        VideoStatus.RENDERING: "render",
        VideoStatus.COMPLETED: "finalizing",
        VideoStatus.ERROR: "error"
    }

    return VideoStatusResponse(
        video_id=video_id,
        status=video["status"],
        progress_percent=progress_map.get(video["status"], 0),
        stage=stage_map.get(video["status"], "unknown"),
        error=video.get("error_message")
    )


@router.post("/{video_id}/analyze", response_model=dict)
async def analyze_video(video_id: str, background_tasks: BackgroundTasks):
    """
    Trigger video analysis (transcript, visual analysis, headline, location).

    Args:
        video_id: Video ID
        background_tasks: FastAPI background tasks

    Returns:
        Message confirming analysis started
    """
    collection = get_videos_collection()
    video = await collection.find_one({"_id": video_id})

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    if video["status"] != VideoStatus.UPLOADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Video must be in 'uploaded' status. Current status: {video['status']}"
        )

    # Trigger analysis in background
    background_tasks.add_task(analyze_video_task, video_id)

    return {
        "video_id": video_id,
        "message": "Analysis started. Check /status for progress.",
        "status": VideoStatus.ANALYZING
    }


@router.get("/{video_id}/analysis", response_model=VideoAnalysisResponse)
async def get_video_analysis(video_id: str):
    """
    Get video analysis results.

    Args:
        video_id: Video ID

    Returns:
        VideoAnalysisResponse with transcript, visual analysis, headline, location
    """
    collection = get_videos_collection()
    video = await collection.find_one({"_id": video_id})

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    if video["status"] in [VideoStatus.UPLOADED, VideoStatus.ANALYZING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis not yet complete. Check /status endpoint."
        )

    return VideoAnalysisResponse(
        video_id=video_id,
        transcript=video.get("transcript"),
        visual_analysis=video.get("visual_analysis"),
        headline=video.get("headline"),
        location=video.get("location")
    )


@router.patch("/{video_id}/metadata", response_model=MetadataUpdateResponse)
async def update_metadata(video_id: str, request: MetadataUpdateRequest):
    """
    Update video headline and location metadata.

    Args:
        video_id: Video ID
        request: Metadata update request

    Returns:
        Updated metadata
    """
    collection = get_videos_collection()
    video = await collection.find_one({"_id": video_id})

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Build update dict
    update_data = {"updated_at": datetime.utcnow()}

    if request.headline is not None:
        update_data["user_headline"] = request.headline

    if request.location is not None:
        update_data["user_location"] = request.location

    if request.show_location is not None:
        update_data["show_location"] = request.show_location

    # Update database
    await collection.update_one(
        {"_id": video_id},
        {"$set": update_data}
    )

    # Get updated video
    updated_video = await collection.find_one({"_id": video_id})

    # Determine final headline and location
    final_headline = updated_video.get("user_headline") or \
                     (updated_video.get("headline", {}).get("primary") if updated_video.get("headline") else "Untitled")

    final_location = updated_video.get("user_location") or \
                     (updated_video.get("location", {}).get("text") if updated_video.get("location") else None)

    return MetadataUpdateResponse(
        video_id=video_id,
        headline=final_headline,
        location=final_location,
        show_location=updated_video.get("show_location", True)
    )


@router.post("/{video_id}/render", response_model=RenderResponse)
async def render_video(video_id: str, request: RenderRequest, background_tasks: BackgroundTasks):
    """
    Trigger video rendering with overlays.

    Args:
        video_id: Video ID
        request: Render request with optional overrides
        background_tasks: FastAPI background tasks

    Returns:
        Render status
    """
    collection = get_videos_collection()
    video = await collection.find_one({"_id": video_id})

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    if video["status"] not in [VideoStatus.ANALYZED, VideoStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video must be analyzed before rendering"
        )

    # Apply overrides if provided
    update_data = {"status": VideoStatus.RENDERING, "updated_at": datetime.utcnow()}

    if request.headline:
        update_data["user_headline"] = request.headline

    if request.location:
        update_data["user_location"] = request.location

    update_data["show_location"] = request.show_location

    await collection.update_one(
        {"_id": video_id},
        {"$set": update_data}
    )

    # Trigger rendering in background
    background_tasks.add_task(render_video_task, video_id)

    return RenderResponse(
        video_id=video_id,
        status=VideoStatus.RENDERING,
        message="Video rendering started. Check /status for progress."
    )


@router.get("/{video_id}/output", response_model=VideoOutputResponse)
async def get_video_output(video_id: str):
    """
    Get final processed video information.

    Args:
        video_id: Video ID

    Returns:
        VideoOutputResponse with download URL and metadata
    """
    collection = get_videos_collection()
    video = await collection.find_one({"_id": video_id})

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    if video["status"] != VideoStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Video not yet completed. Current status: {video['status']}"
        )

    processed_path = video.get("processed_path")
    if not processed_path or not Path(processed_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed video file not found"
        )

    file_size_mb = StorageService.get_file_size_mb(processed_path)

    # Determine final headline and location
    final_headline = video.get("user_headline") or \
                     (video.get("headline", {}).get("primary") if video.get("headline") else "Untitled")

    final_location = video.get("user_location") or \
                     (video.get("location", {}).get("text") if video.get("location") else None)

    return VideoOutputResponse(
        video_id=video_id,
        final_resolution="1080x1920",
        aspect_ratio="9:16",
        file_size_mb=round(file_size_mb, 2),
        download_url=f"/api/videos/{video_id}/download",
        preview_url=None,
        headline=final_headline,
        location=final_location,
        show_location=video.get("show_location", True),
        created_at=video.get("upload_timestamp")
    )


@router.get("/{video_id}/download")
async def download_video(video_id: str):
    """
    Download processed video file.

    Args:
        video_id: Video ID

    Returns:
        Video file stream
    """
    collection = get_videos_collection()
    video = await collection.find_one({"_id": video_id})

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    processed_path = video.get("processed_path")
    if not processed_path or not Path(processed_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed video file not found"
        )

    # Return file
    return FileResponse(
        path=processed_path,
        media_type="video/mp4",
        filename=f"{video_id}_processed.mp4",
        headers={"Content-Disposition": f"attachment; filename={video_id}_processed.mp4"}
    )
