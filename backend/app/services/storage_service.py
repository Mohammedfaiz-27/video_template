"""File storage service for handling video uploads and storage."""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException, status
from app.config import settings


class StorageService:
    """Service for managing video file storage."""

    # Allowed video MIME types
    ALLOWED_MIME_TYPES = [
        "video/mp4",
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
    ]

    # Allowed file extensions
    ALLOWED_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".mpeg", ".mpg"]

    @staticmethod
    def validate_video_file(file: UploadFile) -> None:
        """
        Validate uploaded video file.

        Args:
            file: Uploaded file from FastAPI

        Raises:
            HTTPException: If file is invalid
        """
        # Check if file exists
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )

        # Check MIME type
        if file.content_type not in StorageService.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(StorageService.ALLOWED_MIME_TYPES)}"
            )

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in StorageService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension. Allowed extensions: {', '.join(StorageService.ALLOWED_EXTENSIONS)}"
            )

    @staticmethod
    async def save_uploaded_file(
        file: UploadFile,
        video_id: Optional[str] = None
    ) -> Tuple[str, str, int]:
        """
        Save uploaded video file to storage.

        Args:
            file: Uploaded file from FastAPI
            video_id: Optional video ID, will be generated if not provided

        Returns:
            Tuple of (video_id, file_path, file_size)

        Raises:
            HTTPException: If file save fails
        """
        # Validate file first
        StorageService.validate_video_file(file)

        # Generate video ID if not provided
        if not video_id:
            video_id = str(uuid.uuid4())

        # Get file extension
        file_ext = Path(file.filename).suffix.lower()

        # Create filename: video_id + extension
        filename = f"{video_id}{file_ext}"

        # Get upload directory
        upload_dir = settings.upload_path
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Full file path
        file_path = upload_dir / filename

        # Save file
        try:
            file_size = 0
            async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(8192):  # Read in 8KB chunks
                    file_size += len(chunk)

                    # Check file size limit
                    if file_size > settings.MAX_FILE_SIZE:
                        # Delete partial file
                        await f.close()
                        os.remove(file_path)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
                        )

                    await f.write(chunk)

            return video_id, str(file_path), file_size

        except HTTPException:
            raise
        except Exception as e:
            # Clean up on error
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )

    @staticmethod
    def get_upload_path(video_id: str, extension: str = ".mp4") -> Path:
        """Get path to uploaded video file."""
        return settings.upload_path / f"{video_id}{extension}"

    @staticmethod
    def get_processed_path(video_id: str, extension: str = ".mp4") -> Path:
        """Get path to processed video file."""
        return settings.processed_path / f"{video_id}_processed{extension}"

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file.

        Args:
            file_path: Path to file to delete

        Returns:
            True if deleted, False if file doesn't exist
        """
        try:
            path = Path(file_path)
            if path.exists():
                os.remove(path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in megabytes."""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
