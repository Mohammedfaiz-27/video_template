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

            # Get input stream
            input_stream = ffmpeg.input(input_path)

            # Choose conversion strategy based on current aspect ratio
            if info['aspect_category'] == "9:16":
                # Already 9:16, just scale
                print("   Strategy: Scale (already 9:16)")
                video = input_stream.video
                video = ffmpeg.filter(video, 'scale', target_width, target_height)

            elif aspect > target_aspect:
                # Wider than 9:16 (e.g., 16:9, 4:3) - crop sides
                print("   Strategy: Crop center (wider than 9:16)")

                # Calculate crop dimensions
                # First scale height to 1920, then crop width
                scale_height = target_height
                scale_width = int(current_width * (scale_height / current_height))

                video = input_stream.video
                # Scale to target height
                video = ffmpeg.filter(video, 'scale', scale_width, scale_height)
                # Crop to target width (center crop)
                video = ffmpeg.filter(
                    video,
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

                video = input_stream.video
                # Scale to target width
                video = ffmpeg.filter(video, 'scale', scale_width, scale_height)
                # Pad to target height with black bars
                video = ffmpeg.filter(
                    video,
                    'pad',
                    target_width,
                    target_height,
                    0,  # x position
                    f'(oh-ih)/2',  # y position (center)
                    'black'
                )

            # Check if input has audio stream
            has_audio = any(
                s for s in ffmpeg.probe(input_path)['streams']
                if s['codec_type'] == 'audio'
            )

            if has_audio:
                audio = input_stream.audio
                print("   🔊 Preserving audio in 9:16 conversion...")
                stream = ffmpeg.output(
                    video,
                    audio,
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    preset='medium',
                    crf=23,
                    **{'b:a': '192k'}
                )
            else:
                print("   ℹ️  No audio stream found, processing video only...")
                stream = ffmpeg.output(
                    video,
                    output_path,
                    vcodec='libx264',
                    preset='medium',
                    crf=23,
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
        show_location: bool = True,
        template_id: str = "template1"
    ) -> bool:
        """
        Apply selected template with video, headline, location, and date.

        Uses HTML templates for easy customization.
        All templates are defined in backend/templates/ as HTML files.

        Args:
            input_path: Input video path (should be 9:16)
            output_path: Output video path
            headline: Headline text to overlay
            location: Optional location text
            show_location: Whether to show location
            template_id: Template to use (template1, template2, template3, template4)

        Returns:
            True if successful, False otherwise
        """
        # Use HTML template system
        html_template_name = f"{template_id}.html"

        print(f"🎨 Using HTML template: {html_template_name}")
        return VideoProcessor.process_with_html_template(
            input_path=input_path,
            output_path=output_path,
            template_name=html_template_name,
            headline=headline,
            location=location,
            show_location=show_location
        )

    @staticmethod
    def process_video_complete(
        input_path: str,
        output_path: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True,
        template_id: str = "template1"
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

            # Step 2: Add text overlays with selected template
            success = VideoProcessor.add_text_overlays(
                temp_path,
                output_path,
                headline,
                location,
                show_location,
                template_id
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

    @staticmethod
    def process_with_html_template(
        input_path: str,
        output_path: str,
        template_name: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True
    ) -> bool:
        """
        Process video using HTML template overlay (with Pillow fallback).

        This method:
        1. Tries to render HTML template to PNG overlay (requires html2image + Chrome)
        2. Falls back to Pillow-based overlay if HTML fails
        3. Converts video to 9:16 format
        4. Composites overlay on top of video

        Args:
            input_path: Input video path
            output_path: Output video path
            template_name: HTML template filename (e.g., 'template1.html')
            headline: News headline text
            location: Location text
            show_location: Whether to show location

        Returns:
            True if successful
        """
        try:
            import tempfile

            print(f"🎨 Processing video with template: {template_name}")

            # Step 1: Create overlay PNG
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                overlay_path = tmp.name

            # Use Pillow renderer (reliable font loading from disk)
            print(f"   🎨 Rendering overlay with Pillow...")
            from app.services.simple_overlay_renderer import SimpleOverlayRenderer

            success = SimpleOverlayRenderer.create_overlay(
                template_name=template_name,
                output_path=overlay_path,
                headline=headline,
                location=location,
                show_location=show_location
            )
            if not success:
                print(f"   ❌ Overlay rendering failed")
                return False

            # Step 2: Convert video to 9:16 and composite with overlay using direct FFmpeg
            print(f"   🎬 Converting video to 9:16 format and compositing overlay...")
            print(f"   🔊 Preserving original audio...")

            # Use subprocess to run FFmpeg directly for better audio handling
            import subprocess

            # First, check if input has audio
            probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                        'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', input_path]

            try:
                audio_codec = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
                has_audio = bool(audio_codec.stdout.strip())
                if has_audio:
                    print(f"   🎵 Input audio codec: {audio_codec.stdout.strip()}")
                else:
                    print(f"   ℹ️  Input video has no audio stream")
            except:
                has_audio = False
                print(f"   ℹ️  Could not detect audio stream")

            # Build FFmpeg command with audio copying (not re-encoding)
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', input_path,           # Input video
                '-i', overlay_path,          # Input overlay
                '-filter_complex',
                '[0:v]scale=1080:-2,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2[scaled];'
                '[scaled][1:v]overlay=0:0[outv]',
                '-map', '[outv]',            # Map processed video
                '-map', '0:a?',              # Map audio from input (? means optional)
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'copy',              # COPY audio (don't re-encode)
                '-y',                        # Overwrite output
                output_path
            ]

            print(f"   🔧 FFmpeg command: {' '.join(ffmpeg_cmd)}")

            try:
                result = subprocess.run(
                    ffmpeg_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                if has_audio:
                    print(f"   ✅ Video processed successfully WITH original audio")
                else:
                    print(f"   ✅ Video processed successfully (no audio in source)")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ FFmpeg error:")
                print(f"   {e.stderr[-500:]}")  # Last 500 chars of error

                # Try with AAC encoding instead of copy
                if has_audio:
                    print(f"   🔄 Retrying with AAC audio encoding...")
                    ffmpeg_cmd[ffmpeg_cmd.index('-c:a') + 1] = 'aac'
                    ffmpeg_cmd.insert(ffmpeg_cmd.index('-c:a') + 2, '-b:a')
                    ffmpeg_cmd.insert(ffmpeg_cmd.index('-c:a') + 3, '192k')

                    try:
                        subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
                        print(f"   ✅ Video processed with AAC audio")
                    except:
                        # Last resort: no audio
                        print(f"   ⚠️  Rendering without audio...")
                        ffmpeg_cmd_no_audio = [
                            'ffmpeg', '-i', input_path, '-i', overlay_path,
                            '-filter_complex',
                            '[0:v]scale=1080:-2,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2[scaled];'
                            '[scaled][1:v]overlay=0:0',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                            '-y', output_path
                        ]
                        subprocess.run(ffmpeg_cmd_no_audio, check=True)
                        print(f"   ⚠️  Video rendered without audio")

            # Cleanup temporary overlay file
            try:
                os.unlink(overlay_path)
            except:
                pass

            return True

        except Exception as e:
            print(f"❌ HTML template processing failed: {e}")
            import traceback
            traceback.print_exc()
            return False
