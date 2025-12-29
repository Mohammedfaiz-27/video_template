"""FFmpeg video processing service for format conversion and text overlays."""

import os
import json
import subprocess
import ffmpeg
from pathlib import Path
from typing import Dict, Optional, Tuple

from app.config import settings


class VideoProcessor:
    """Service for video processing using FFmpeg."""

    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, any]:
        """
        Extract video metadata using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )

            if not video_stream:
                raise ValueError("No video stream found")

            width = int(video_stream['width'])
            height = int(video_stream['height'])
            duration = float(probe['format']['duration'])
            fps = eval(video_stream['r_frame_rate'])  # e.g., "30/1"
            codec = video_stream['codec_name']
            bitrate = int(probe['format'].get('bit_rate', 0))

            # Calculate aspect ratio
            aspect_ratio = f"{width}:{height}"
            aspect_decimal = width / height

            # Categorize aspect ratio
            if aspect_decimal > 1.7:
                aspect_category = "16:9"
            elif aspect_decimal > 1.2:
                aspect_category = "4:3"
            elif 0.9 <= aspect_decimal <= 1.1:
                aspect_category = "1:1"
            elif aspect_decimal < 0.6:
                aspect_category = "9:16"
            else:
                aspect_category = "custom"

            return {
                "width": width,
                "height": height,
                "duration": duration,
                "fps": fps,
                "codec": codec,
                "bitrate": bitrate,
                "aspect_ratio": aspect_ratio,
                "aspect_decimal": aspect_decimal,
                "aspect_category": aspect_category,
                "resolution": f"{width}x{height}"
            }

        except Exception as e:
            print(f"❌ Error getting video info: {e}")
            raise

    @staticmethod
    def convert_to_9_16(
        input_path: str,
        output_path: str,
        strategy: str = "crop"
    ) -> bool:
        """
        Convert video to 9:16 aspect ratio (1080x1920).

        Args:
            input_path: Input video path
            output_path: Output video path
            strategy: Conversion strategy ("crop", "pad", "scale")

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🎬 Converting to 9:16: {Path(input_path).name}")

            # Get video info
            info = VideoProcessor.get_video_info(input_path)
            current_width = info['width']
            current_height = info['height']
            aspect = info['aspect_decimal']

            print(f"   Original: {current_width}x{current_height} ({info['aspect_category']})")

            # Target dimensions
            target_width = 1080
            target_height = 1920
            target_aspect = target_width / target_height  # 0.5625

            # Choose conversion strategy based on current aspect ratio
            if info['aspect_category'] == "9:16":
                # Already 9:16, just scale
                print("   Strategy: Scale (already 9:16)")
                stream = ffmpeg.input(input_path)
                stream = ffmpeg.filter(stream, 'scale', target_width, target_height)

            elif aspect > target_aspect:
                # Wider than 9:16 (e.g., 16:9, 4:3) - crop sides
                print("   Strategy: Crop center (wider than 9:16)")

                # Calculate crop dimensions
                # First scale height to 1920, then crop width
                scale_height = target_height
                scale_width = int(current_width * (scale_height / current_height))

                stream = ffmpeg.input(input_path)
                # Scale to target height
                stream = ffmpeg.filter(stream, 'scale', scale_width, scale_height)
                # Crop to target width (center crop)
                stream = ffmpeg.filter(
                    stream,
                    'crop',
                    target_width,
                    target_height,
                    f'(in_w-{target_width})/2',  # x position (center)
                    0  # y position (top)
                )

            else:
                # Narrower than 9:16 or square - pad top/bottom
                print("   Strategy: Pad (narrower than 9:16)")

                # Calculate scaled dimensions
                scale_width = target_width
                scale_height = int(current_height * (scale_width / current_width))

                stream = ffmpeg.input(input_path)
                # Scale to target width
                stream = ffmpeg.filter(stream, 'scale', scale_width, scale_height)
                # Pad to target height with black bars
                stream = ffmpeg.filter(
                    stream,
                    'pad',
                    target_width,
                    target_height,
                    0,  # x position
                    f'(oh-ih)/2',  # y position (center)
                    'black'
                )

            # Output with audio copy (no re-encoding audio)
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                acodec='aac',
                preset='medium',
                crf=23,
                **{'b:a': '128k'}
            )

            # Run FFmpeg
            ffmpeg.run(stream, overwrite_output=True, quiet=False)

            print(f"   ✓ Converted to 9:16: {target_width}x{target_height}")
            return True

        except Exception as e:
            print(f"   ❌ Error converting to 9:16: {e}")
            return False

    @staticmethod
    def add_text_overlays(
        input_path: str,
        output_path: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True
    ) -> bool:
        """
        Add text overlays (headline and location) to video.

        Args:
            input_path: Input video path (should be 9:16)
            output_path: Output video path
            headline: Headline text to overlay
            location: Optional location text
            show_location: Whether to show location

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"✏️  Adding text overlays")
            print(f"   Headline: {headline}")
            if show_location and location:
                print(f"   Location: {location}")

            # Escape special characters for FFmpeg drawtext
            headline_escaped = VideoProcessor._escape_text(headline)
            location_escaped = VideoProcessor._escape_text(location) if location else ""

            # Build filter complex
            filters = []

            # Headline overlay (top center)
            headline_filter = (
                f"drawtext="
                f"fontfile=C\\\\:/Windows/Fonts/arialbd.ttf:"  # Windows Arial Bold
                f"text='{headline_escaped}':"
                f"fontcolor=white:"
                f"fontsize=64:"
                f"borderw=3:"
                f"bordercolor=black:"
                f"x=(w-text_w)/2:"  # Center horizontally
                f"y=120:"  # 120px from top
                f"shadowcolor=black@0.8:"
                f"shadowx=2:"
                f"shadowy=2"
            )
            filters.append(headline_filter)

            # Location overlay (bottom left) with emoji
            if show_location and location:
                location_text = f"📍 {location_escaped}"
                location_filter = (
                    f"drawtext="
                    f"fontfile=C\\\\:/Windows/Fonts/arial.ttf:"
                    f"text='{location_text}':"
                    f"fontcolor=white:"
                    f"fontsize=36:"
                    f"box=1:"
                    f"boxcolor=black@0.7:"
                    f"boxborderw=10:"
                    f"x=50:"  # 50px from left
                    f"y=h-100:"  # 100px from bottom
                    f"shadowcolor=black@0.5:"
                    f"shadowx=1:"
                    f"shadowy=1"
                )
                filters.append(location_filter)

            # Combine filters
            filter_complex = ",".join(filters)

            # Build FFmpeg command
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'drawtext', None, **{
                'text': headline_escaped,
                'fontfile': 'C:/Windows/Fonts/arialbd.ttf',
                'fontcolor': 'white',
                'fontsize': 64,
                'borderw': 3,
                'bordercolor': 'black',
                'x': '(w-text_w)/2',
                'y': 120,
                'shadowcolor': 'black@0.8',
                'shadowx': 2,
                'shadowy': 2
            })

            # Add location overlay if needed
            if show_location and location:
                location_text = f"📍 {location}"
                stream = ffmpeg.filter(stream, 'drawtext', None, **{
                    'text': location_escaped,
                    'fontfile': 'C:/Windows/Fonts/arial.ttf',
                    'fontcolor': 'white',
                    'fontsize': 36,
                    'box': 1,
                    'boxcolor': 'black@0.7',
                    'boxborderw': 10,
                    'x': 50,
                    'y': 'h-100',
                    'shadowcolor': 'black@0.5',
                    'shadowx': 1,
                    'shadowy': 1
                })

            # Output with audio copy
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                acodec='copy',
                preset='medium',
                crf=23
            )

            # Run FFmpeg
            ffmpeg.run(stream, overwrite_output=True, quiet=False)

            print(f"   ✓ Text overlays added")
            return True

        except Exception as e:
            print(f"   ❌ Error adding text overlays: {e}")
            return False

    @staticmethod
    def process_video_complete(
        input_path: str,
        output_path: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True
    ) -> bool:
        """
        Complete video processing: convert to 9:16 + add text overlays in one pass.

        Args:
            input_path: Input video path
            output_path: Output video path
            headline: Headline text
            location: Optional location text
            show_location: Whether to show location

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🎬 Processing video: {Path(input_path).name}")

            # Get video info
            info = VideoProcessor.get_video_info(input_path)
            print(f"   Input: {info['resolution']} ({info['aspect_category']})")

            # Create temporary file for 9:16 conversion
            temp_path = output_path.replace('.mp4', '_temp.mp4')

            # Step 1: Convert to 9:16
            success = VideoProcessor.convert_to_9_16(input_path, temp_path)
            if not success:
                return False

            # Step 2: Add text overlays
            success = VideoProcessor.add_text_overlays(
                temp_path,
                output_path,
                headline,
                location,
                show_location
            )

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            if success:
                print(f"✅ Video processing complete: {Path(output_path).name}")

            return success

        except Exception as e:
            print(f"❌ Error processing video: {e}")
            return False

    @staticmethod
    def _escape_text(text: str) -> str:
        """
        Escape special characters for FFmpeg drawtext filter.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        if not text:
            return ""

        # Escape special characters for drawtext
        replacements = {
            "'": "\\'",
            ":": "\\:",
            "\\": "\\\\",
            "[": "\\[",
            "]": "\\]",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    @staticmethod
    def extract_thumbnail(video_path: str, output_path: str, timestamp: float = 1.0) -> bool:
        """
        Extract a thumbnail from video.

        Args:
            video_path: Input video path
            output_path: Output image path
            timestamp: Timestamp in seconds

        Returns:
            True if successful
        """
        try:
            stream = ffmpeg.input(video_path, ss=timestamp)
            stream = ffmpeg.output(stream, output_path, vframes=1)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            return True
        except Exception as e:
            print(f"❌ Error extracting thumbnail: {e}")
            return False
