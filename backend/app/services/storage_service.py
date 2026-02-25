"""File storage service — supports both AWS S3 and local filesystem."""

import os
import uuid
import tempfile
import aiofiles
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException, status
from app.config import settings


def _get_s3_client():
    import boto3
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


class StorageService:
    """Service for managing video file storage (S3 or local)."""

    ALLOWED_MIME_TYPES = [
        "video/mp4",
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
    ]
    ALLOWED_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".mpeg", ".mpg"]

    # ------------------------------------------------------------------ #
    #  Validation                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_video_file(file: UploadFile) -> None:
        if not file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")
        if file.content_type not in StorageService.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(StorageService.ALLOWED_MIME_TYPES)}"
            )
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in StorageService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid extension. Allowed: {', '.join(StorageService.ALLOWED_EXTENSIONS)}"
            )

    # ------------------------------------------------------------------ #
    #  Upload                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    async def save_uploaded_file(
        file: UploadFile,
        video_id: Optional[str] = None
    ) -> Tuple[str, str, int]:
        """
        Save uploaded video.
        Returns (video_id, storage_path, file_size_bytes)
        - S3 mode:    storage_path = s3://<bucket>/<key>
        - Local mode: storage_path = absolute local path
        """
        StorageService.validate_video_file(file)

        if not video_id:
            video_id = str(uuid.uuid4())

        file_ext = Path(file.filename).suffix.lower()
        filename = f"{video_id}{file_ext}"

        # Read entire file into memory (chunked) to get size + content
        chunks = []
        file_size = 0
        while chunk := await file.read(8192):
            file_size += len(chunk)
            if file_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Max: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            chunks.append(chunk)
        data = b"".join(chunks)

        if settings.use_s3:
            s3_key = f"{settings.S3_UPLOAD_PREFIX}/{filename}"
            try:
                s3 = _get_s3_client()
                s3.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=data,
                    ContentType=file.content_type,
                )
                storage_path = f"s3://{settings.S3_BUCKET_NAME}/{s3_key}"
                print(f"   ✅ Uploaded to S3: {s3_key}")
                return video_id, storage_path, file_size
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"S3 upload failed: {e}"
                )
        else:
            upload_dir = settings.upload_path
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / filename
            try:
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(data)
                return video_id, str(file_path), file_size
            except Exception as e:
                if file_path.exists():
                    os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save file: {e}"
                )

    # ------------------------------------------------------------------ #
    #  Download to local temp (for ffmpeg / Gemini processing)            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def download_to_temp(storage_path: str) -> str:
        """
        Download a file from S3 (or copy from local) to a temp file.
        Returns the local temp file path.
        """
        if storage_path.startswith("s3://"):
            # Parse s3://bucket/key
            without_prefix = storage_path[5:]
            bucket, key = without_prefix.split("/", 1)
            suffix = Path(key).suffix
            tmp = tempfile.NamedTemporaryFile(
                suffix=suffix, dir="/tmp", delete=False
            )
            tmp.close()
            s3 = _get_s3_client()
            s3.download_file(bucket, key, tmp.name)
            print(f"   ⬇️  Downloaded from S3: {key} → {tmp.name}")
            return tmp.name
        else:
            # Already a local path
            return storage_path

    # ------------------------------------------------------------------ #
    #  Upload processed video                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def upload_processed_video(local_path: str, video_id: str) -> str:
        """
        Upload a locally-processed video to S3 (or keep it local).
        Returns the final storage_path.
        """
        if settings.use_s3:
            filename = f"{video_id}_processed.mp4"
            s3_key = f"{settings.S3_PROCESSED_PREFIX}/{filename}"
            s3 = _get_s3_client()
            s3.upload_file(local_path, settings.S3_BUCKET_NAME, s3_key)
            storage_path = f"s3://{settings.S3_BUCKET_NAME}/{s3_key}"
            print(f"   ✅ Processed video uploaded to S3: {s3_key}")
            return storage_path
        else:
            return local_path

    # ------------------------------------------------------------------ #
    #  Pre-signed download URL                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_download_url(storage_path: str, video_id: str, expires: int = 3600) -> Optional[str]:
        """
        Return a pre-signed S3 URL (valid for `expires` seconds).
        Returns None for local storage (caller should serve file directly).
        """
        if storage_path and storage_path.startswith("s3://"):
            without_prefix = storage_path[5:]
            bucket, key = without_prefix.split("/", 1)
            s3 = _get_s3_client()
            url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": bucket,
                    "Key": key,
                    "ResponseContentDisposition": f"attachment; filename={video_id}_processed.mp4"
                },
                ExpiresIn=expires,
            )
            return url
        return None

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_processed_path(video_id: str, extension: str = ".mp4") -> Path:
        """Get local path for processed video (used during rendering)."""
        return Path("/tmp") / f"{video_id}_processed{extension}"

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a local file (temp cleanup)."""
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
        """Get local file size in MB."""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except Exception:
            return 0.0
