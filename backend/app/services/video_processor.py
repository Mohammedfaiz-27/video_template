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
        Add text overlays (headline and location) to video with golden borders and backgrounds.

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
            print(f"✏️  Adding text overlays with golden borders")
            print(f"   Headline: {headline}")
            if show_location and location:
                print(f"   Location: {location}")

            # Get Tamil font path
            tamil_font_path = str(Path(__file__).parent.parent.parent / 'fonts' / 'TAMIL-UNI004.ttf')
            # Escape backslashes for FFmpeg (Windows path)
            tamil_font_escaped = tamil_font_path.replace('\\', '/')

            # Escape headline and location text
            headline_escaped = VideoProcessor._escape_text(headline)
            location_escaped = VideoProcessor._escape_text(location) if location else ""

            # Build FFmpeg command
            stream = ffmpeg.input(input_path)

            # Add border to entire video frame (10px golden border)
            stream = ffmpeg.filter(stream, 'pad',
                width='iw+20',
                height='ih+20',
                x=10,
                y=10,
                color='#fda085'
            )

            # HEADLINE OVERLAY - Top center with golden background and border
            # Positioned safely inside video frame with proper margins
            stream = ffmpeg.filter(stream, 'drawtext', None, **{
                'text': headline_escaped,
                'fontfile': tamil_font_escaped,  # Tamil font for proper Tamil support
                'fontcolor': '#1a2b47',  # Dark blue text (matching HTML template)
                'fontsize': 42,  # Optimized size for Tamil text
                'box': 1,
                'boxcolor': '#f6d365@0.95',  # Golden color with 95% opacity
                'boxborderw': 35,  # Extra padding to keep text inside box
                'borderw': 6,  # Thick border for visibility
                'bordercolor': '#fda085',  # Coral/peach border color
                'x': '(w-text_w)/2',  # Center horizontally
                'y': 170,  # Positioned from top
                'shadowcolor': 'black@0.5',
                'shadowx': 5,
                'shadowy': 5
            })

            # LOCATION OVERLAY - Bottom left with golden background and border
            if show_location and location:
                # Use simple location marker that renders properly
                location_with_marker = f"▸ {location_escaped}"  # Triangle marker instead of emoji
                stream = ffmpeg.filter(stream, 'drawtext', None, **{
                    'text': location_with_marker,
                    'fontfile': tamil_font_escaped,  # Tamil font for consistent styling
                    'fontcolor': '#1a2b47',  # Dark blue text
                    'fontsize': 36,  # Font size for location
                    'box': 1,
                    'boxcolor': '#f6d365@0.95',  # Golden color with 95% opacity
                    'boxborderw': 28,  # Extra padding
                    'borderw': 5,  # Thicker border matching headline
                    'bordercolor': '#fda085',  # Coral/peach border color
                    'x': 110,  # Position from left (accounting for video border)
                    'y': 'h-200',  # Position from bottom
                    'shadowcolor': 'black@0.4',
                    'shadowx': 4,
                    'shadowy': 4
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

            print(f"   ✓ Text overlays with golden borders added")
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
    def _wrap_text(text: str, max_chars_per_line: int = 30) -> str:
        """
        Wrap text to multiple lines based on character limit.

        Args:
            text: Text to wrap
            max_chars_per_line: Maximum characters per line

        Returns:
            Text with line breaks inserted
        """
        if not text or len(text) <= max_chars_per_line:
            return text

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)
            # Check if adding this word would exceed the limit
            if current_length + word_length + len(current_line) > max_chars_per_line:
                if current_line:  # Save current line and start new one
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:  # Single word is too long, add it anyway
                    lines.append(word)
                    current_line = []
                    current_length = 0
            else:
                current_line.append(word)
                current_length += word_length

        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))

        # Use actual newline character for FFmpeg
        return '\n'.join(lines)

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
