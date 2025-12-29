"""Utility helper functions."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration (e.g., "2:34" or "1:23:45")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size (e.g., "10.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove unsafe characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators and other unsafe characters
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')

    return filename


def ensure_dir(directory: str) -> Path:
    """
    Ensure directory exists, create if not.

    Args:
        directory: Directory path

    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.

    Args:
        filename: Filename

    Returns:
        Extension (e.g., ".mp4")
    """
    return Path(filename).suffix.lower()


def is_video_file(filename: str) -> bool:
    """
    Check if filename is a video file based on extension.

    Args:
        filename: Filename to check

    Returns:
        True if video file, False otherwise
    """
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.mpeg', '.mpg', '.webm', '.flv']
    return get_file_extension(filename) in video_extensions


def timestamp_to_iso(timestamp: datetime) -> str:
    """
    Convert datetime to ISO format string.

    Args:
        timestamp: Datetime object

    Returns:
        ISO format string
    """
    return timestamp.isoformat()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_aspect_ratio(width: int, height: int) -> str:
    """
    Parse aspect ratio from width and height.

    Args:
        width: Video width
        height: Video height

    Returns:
        Aspect ratio string (e.g., "16:9")
    """
    from math import gcd

    divisor = gcd(width, height)
    w = width // divisor
    h = height // divisor

    # Common aspect ratios
    common_ratios = {
        (16, 9): "16:9",
        (4, 3): "4:3",
        (1, 1): "1:1",
        (9, 16): "9:16",
        (21, 9): "21:9"
    }

    return common_ratios.get((w, h), f"{w}:{h}")


def validate_api_key(api_key: Optional[str], service_name: str) -> bool:
    """
    Validate API key is present and not empty.

    Args:
        api_key: API key to validate
        service_name: Name of service for error message

    Returns:
        True if valid, False otherwise
    """
    if not api_key or api_key.strip() == "":
        print(f"⚠️  {service_name} API key not configured")
        return False
    return True


def log_task_start(task_name: str, video_id: str) -> None:
    """Log task start."""
    print(f"\n{'='*60}")
    print(f"🚀 Starting: {task_name}")
    print(f"   Video ID: {video_id}")
    print(f"   Time: {datetime.utcnow().isoformat()}")
    print(f"{'='*60}\n")


def log_task_complete(task_name: str, video_id: str, success: bool = True) -> None:
    """Log task completion."""
    icon = "✅" if success else "❌"
    status = "SUCCESS" if success else "FAILED"

    print(f"\n{'='*60}")
    print(f"{icon} {status}: {task_name}")
    print(f"   Video ID: {video_id}")
    print(f"   Time: {datetime.utcnow().isoformat()}")
    print(f"{'='*60}\n")


def log_error(context: str, error: Exception) -> None:
    """Log error with context."""
    print(f"\n❌ ERROR in {context}:")
    print(f"   {type(error).__name__}: {str(error)}")
    print(f"   Time: {datetime.utcnow().isoformat()}\n")
