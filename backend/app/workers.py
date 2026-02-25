"""Background task workers for video processing."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from app.database import get_videos_collection
from app.models.video import VideoStatus
from app.services.gemini_service import GeminiService
from app.services.video_processor import VideoProcessor
from app.services.storage_service import StorageService
from app.utils.helpers import log_task_start, log_task_complete, log_error


async def analyze_video_task(video_id: str) -> bool:
    """
    Background task for video analysis using Gemini AI.

    Workflow:
    1. Extract transcript from video
    2. Analyze visual content
    3. Generate headline
    4. Detect location
    5. (Optional) Refine headline with Perplexity
    6. Update database with results

    Args:
        video_id: Video ID to analyze

    Returns:
        True if successful, False otherwise
    """
    log_task_start("Video Analysis", video_id)

    try:
        collection = get_videos_collection()

        # Get video document
        video = await collection.find_one({"_id": video_id})
        if not video:
            print(f"❌ Video not found: {video_id}")
            return False

        # Update status to analyzing
        await collection.update_one(
            {"_id": video_id},
            {
                "$set": {
                    "status": VideoStatus.ANALYZING,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Get video path (may be s3:// or local)
        video_path = video.get("original_path")
        if not video_path:
            raise FileNotFoundError("No video path stored in database")

        # Download to local temp if stored in S3
        local_video_path = StorageService.download_to_temp(video_path)
        temp_downloaded = local_video_path != video_path  # True if we made a temp copy

        try:
            # Initialize services
            gemini = GeminiService()

            # Run complete analysis
            transcript, visual, headline, location = await gemini.analyze_video_complete(local_video_path)
        finally:
            # Clean up temp file
            if temp_downloaded:
                StorageService.delete_file(local_video_path)

        # Update database with analysis results
        await collection.update_one(
            {"_id": video_id},
            {
                "$set": {
                    "status": VideoStatus.ANALYZED,
                    "transcript": transcript.model_dump(),
                    "visual_analysis": visual.model_dump(),
                    "headline": headline.model_dump(),
                    "location": location.model_dump() if location.text else None,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        log_task_complete("Video Analysis", video_id, success=True)
        return True

    except Exception as e:
        log_error("Video Analysis", e)

        # Update database with error
        collection = get_videos_collection()
        await collection.update_one(
            {"_id": video_id},
            {
                "$set": {
                    "status": VideoStatus.ERROR,
                    "error_message": f"Analysis failed: {str(e)}",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        log_task_complete("Video Analysis", video_id, success=False)
        return False


async def regenerate_ai_suggestions_task(video_id: str) -> bool:
    """
    Background task for regenerating AI headline and location suggestions.
    Uses existing transcript and visual analysis to generate fresh suggestions.

    Args:
        video_id: Video ID

    Returns:
        True if successful, False otherwise
    """
    log_task_start("AI Suggestion Regeneration", video_id)

    try:
        collection = get_videos_collection()

        # Get video document
        video = await collection.find_one({"_id": video_id})
        if not video:
            print(f"❌ Video not found: {video_id}")
            return False

        # Check if transcript and visual analysis exist
        transcript_data = video.get("transcript")
        visual_data = video.get("visual_analysis")

        if not transcript_data or not visual_data:
            raise ValueError("Video must be analyzed first (missing transcript or visual analysis)")

        # Initialize services
        gemini = GeminiService()

        # Reconstruct objects from stored data
        from app.models.video import TranscriptData, VisualAnalysis

        transcript = TranscriptData(**transcript_data)
        visual = VisualAnalysis(**visual_data)

        # Regenerate headline FROM TEXT ONLY (efficient!)
        print("Regenerating headline from transcript...")
        headline = await gemini.generate_headline_from_text(transcript.text)
        print(f"New headline: {headline.primary}")

        # Regenerate location FROM TEXT ONLY (efficient!)
        print("Regenerating location from transcript...")
        location = await gemini.detect_location_from_text(transcript.text)
        if location.text:
            print(f"New location: {location.text}")
        else:
            print("No location detected")

        # Update database with new suggestions (keeping transcript and visual unchanged)
        await collection.update_one(
            {"_id": video_id},
            {
                "$set": {
                    "headline": headline.model_dump(),
                    "location": location.model_dump() if location.text else None,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        log_task_complete("AI Suggestion Regeneration", video_id, success=True)
        return True

    except Exception as e:
        log_error("AI Suggestion Regeneration", e)
        log_task_complete("AI Suggestion Regeneration", video_id, success=False)
        return False


async def render_video_task(video_id: str) -> bool:
    """
    Background task for video rendering with text overlays.

    Workflow:
    1. Get video metadata and settings
    2. Convert video to 9:16 aspect ratio
    3. Add text overlays (headline + location)
    4. Save processed video
    5. Update database with output info

    Args:
        video_id: Video ID to render

    Returns:
        True if successful, False otherwise
    """
    log_task_start("Video Rendering", video_id)

    try:
        collection = get_videos_collection()

        # Get video document
        video = await collection.find_one({"_id": video_id})
        if not video:
            print(f"❌ Video not found: {video_id}")
            return False

        # Validate video is analyzed
        if video.get("status") not in [VideoStatus.ANALYZED, VideoStatus.RENDERING]:
            raise ValueError(f"Video must be analyzed before rendering. Current status: {video.get('status')}")

        # Update status to rendering
        await collection.update_one(
            {"_id": video_id},
            {
                "$set": {
                    "status": VideoStatus.RENDERING,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Get paths (original_path may be s3:// or local)
        input_path = video.get("original_path")
        if not input_path:
            raise FileNotFoundError("No video path stored in database")

        # Download original from S3 to local temp for ffmpeg
        local_input = StorageService.download_to_temp(input_path)
        temp_input = local_input != input_path

        # Local temp path for rendered output
        output_path = str(StorageService.get_processed_path(video_id, ".mp4"))

        # Get headline and location
        final_headline = video.get("user_headline") or \
                        (video.get("headline", {}).get("primary") if video.get("headline") else "Untitled")

        final_location = video.get("user_location") or \
                        (video.get("location", {}).get("text") if video.get("location") else None)

        show_location = video.get("show_location", True)
        template_id = video.get("template_id", "template1")

        print(f"📝 Rendering with:")
        print(f"   Headline: {final_headline}")
        if show_location and final_location:
            print(f"   Location: {final_location}")
        print(f"   Template: {template_id}")

        # Process video using local temp paths
        processor = VideoProcessor()
        success = processor.process_video_complete(
            local_input,
            output_path,
            final_headline,
            final_location,
            show_location,
            template_id
        )

        # Clean up temp input
        if temp_input:
            StorageService.delete_file(local_input)

        if not success:
            raise Exception("Video processing failed")

        # Upload processed video to S3 (or keep local)
        final_storage_path = StorageService.upload_processed_video(output_path, video_id)

        # Clean up local rendered file if it was uploaded to S3
        if final_storage_path != output_path:
            StorageService.delete_file(output_path)

        file_size_mb = StorageService.get_file_size_mb(output_path) if final_storage_path == output_path else 0.0

        # Update database with completed status
        await collection.update_one(
            {"_id": video_id},
            {
                "$set": {
                    "status": VideoStatus.COMPLETED,
                    "processed_path": final_storage_path,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        log_task_complete("Video Rendering", video_id, success=True)
        print(f"📦 Output stored: {final_storage_path}")

        return True

    except Exception as e:
        log_error("Video Rendering", e)

        # Update database with error
        collection = get_videos_collection()
        await collection.update_one(
            {"_id": video_id},
            {
                "$set": {
                    "status": VideoStatus.ERROR,
                    "error_message": f"Rendering failed: {str(e)}",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        log_task_complete("Video Rendering", video_id, success=False)
        return False


async def cleanup_old_videos(days: int = 7) -> int:
    """
    Background task to clean up old processed videos.

    Args:
        days: Delete videos older than this many days

    Returns:
        Number of videos cleaned up
    """
    log_task_start("Video Cleanup", "system")

    try:
        collection = get_videos_collection()
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Find old completed videos
        old_videos = await collection.find({
            "status": VideoStatus.COMPLETED,
            "upload_timestamp": {"$lt": cutoff_date}
        }).to_list(length=None)

        cleaned = 0
        for video in old_videos:
            video_id = video["_id"]

            # Delete processed file
            processed_path = video.get("processed_path")
            if processed_path:
                if StorageService.delete_file(processed_path):
                    print(f"🗑️  Deleted: {Path(processed_path).name}")
                    cleaned += 1

            # Delete original file
            original_path = video.get("original_path")
            if original_path:
                StorageService.delete_file(original_path)

            # Delete database entry
            await collection.delete_one({"_id": video_id})

        log_task_complete("Video Cleanup", "system", success=True)
        print(f"Cleaned up {cleaned} old videos")

        return cleaned

    except Exception as e:
        log_error("Video Cleanup", e)
        log_task_complete("Video Cleanup", "system", success=False)
        return 0
