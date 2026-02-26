"""Gemini AI service for video analysis, transcript, headline, and location detection."""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image
import google.genai as genai
from google.genai import types

from app.config import settings
from app.models.video import TranscriptData, VisualAnalysis, HeadlineData, LocationData


class GeminiService:
    """Service for interacting with Google Gemini API."""

    # Models to try in order — first stable, fallback to older
    MODEL_PRIORITY = [
        'models/gemini-2.0-flash',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-flash-8b',
    ]

    def __init__(self):
        """Initialize Gemini service with API key."""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = self.MODEL_PRIORITY[0]

    async def analyze_video_complete(
        self,
        video_path: str
    ) -> Tuple[TranscriptData, VisualAnalysis, HeadlineData, LocationData]:
        """
        Complete video analysis pipeline.
        NEW APPROACH: Extract transcript once, then use text-only analysis.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (transcript, visual_analysis, headline, location)
        """
        print(f"Starting complete analysis: {video_path}")

        # Upload video to Gemini
        video_file = await self._upload_video_to_gemini(video_path)

        # Extract transcript (includes speech + visible text)
        transcript = await self.extract_transcript(video_file)
        print(f"Transcript extracted: {len(transcript.text)} chars")

        # Simple visual check (optional - just for metadata)
        visual = VisualAnalysis(
            scene_type="video",
            people_count=0,
            objects=[],
            mood="neutral",
            landmarks=[],
            description="Video content"
        )

        # Generate headline FROM TRANSCRIPT ONLY (no video re-upload)
        headline = await self.generate_headline_from_text(transcript.text)
        print(f"Headline generated: {headline.primary}")

        # Detect location FROM TRANSCRIPT ONLY
        location = await self.detect_location_from_text(transcript.text)
        if location.text:
            print(f"Location detected: {location.text}")
        else:
            print("No location detected")

        return transcript, visual, headline, location

    async def _upload_video_to_gemini(self, video_path: str):
        """
        Upload video file to Gemini API using new google.genai package.

        Args:
            video_path: Path to video file

        Returns:
            Uploaded file object
        """
        print(f"Uploading video to Gemini...")
        print(f"File path: {video_path}")
        print(f"File size: {Path(video_path).stat().st_size / (1024*1024):.2f} MB")

        try:
            # Detect MIME type from file extension
            import mimetypes
            mime_type, _ = mimetypes.guess_type(video_path)
            if not mime_type:
                mime_type = 'video/mp4'  # Default to mp4

            print(f"MIME type: {mime_type}")

            # Upload file using new API
            with open(video_path, 'rb') as f:
                uploaded_file = self.client.files.upload(file=f, config={'mime_type': mime_type})

            print(f"Uploaded file: {uploaded_file.name}")
            print(f"File URI: {uploaded_file.uri}")

            # Wait for processing if needed
            max_wait = 120
            wait_time = 0
            while uploaded_file.state == "PROCESSING":
                if wait_time >= max_wait:
                    raise TimeoutError(f"Video processing timeout")

                print(f"Waiting for processing... ({wait_time}s)")
                time.sleep(5)
                wait_time += 5
                uploaded_file = self.client.files.get(name=uploaded_file.name)

            if uploaded_file.state == "FAILED":
                raise Exception(f"Video processing failed")

            print(f"Video ready (state: {uploaded_file.state})")
            return uploaded_file

        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            raise

    def _generate_with_retry(self, prompt, contents=None, temperature=0.3):
        """
        Call Gemini with automatic model fallback on 503 / quota errors.
        Tries each model in MODEL_PRIORITY before giving up.
        """
        last_error = None
        for model in self.MODEL_PRIORITY:
            try:
                call_contents = contents if contents is not None else prompt
                response = self.client.models.generate_content(
                    model=model,
                    contents=call_contents,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        response_mime_type="application/json"
                    )
                )
                if model != self.model_name:
                    print(f"   ⚠️ Used fallback model: {model}")
                return response
            except Exception as e:
                err_str = str(e)
                if '503' in err_str or 'UNAVAILABLE' in err_str or '429' in err_str or 'quota' in err_str.lower():
                    print(f"   Model {model} unavailable ({e}), trying next...")
                    last_error = e
                    time.sleep(2)
                    continue
                raise  # Non-retryable error — re-raise immediately
        raise last_error

    async def extract_transcript(self, video_file) -> TranscriptData:
        """
        Extract BOTH speech and visible text from video using Gemini.

        Args:
            video_file: Gemini uploaded video file

        Returns:
            TranscriptData with combined transcript
        """
        try:
            prompt = """
            Carefully analyze this video and extract ALL available text information:

            1. SPEECH: Transcribe every spoken word, dialogue, narration, announcements
            2. VISIBLE TEXT: Read all on-screen text — banners, signs, lower-thirds, subtitles,
               captions, news tickers, title cards, location names, any written text visible in the video
            3. AUDIO CUES: Note background audio if relevant (crowd sounds, music, etc.)

            Write a DETAILED, COMPLETE transcript combining all of the above.
            Do NOT summarize — write out the actual words spoken and text seen.
            Include as much detail as possible. Aim for at least a few sentences.

            Return a JSON object with this exact structure:
            {
                "text": "Full detailed transcript here with all speech and visible text...",
                "language": "detected language code (e.g., 'en', 'ta', 'hi', 'te', 'ml')",
                "language_confidence": 0.95,
                "has_significant_audio": true
            }

            Language detection: use 'ta' for Tamil, 'hi' for Hindi, 'te' for Telugu,
            'ml' for Malayalam, 'en' for English. Detect from both audio and on-screen text.
            """

            response = self._generate_with_retry(
                prompt=prompt,
                contents=[
                    types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type),
                    types.Part.from_text(prompt)
                ],
                temperature=0.2
            )

            response_text = response.text.strip()

            if not response_text:
                print(f"WARNING: Empty response")
                raise ValueError("Empty response from Gemini")

            print(f"Transcript response: {len(response_text)} chars")

            result = json.loads(response_text)
            transcript_text = result.get("text", "")

            return TranscriptData(
                text=transcript_text,
                language=result.get("language", "en"),
                language_confidence=result.get("language_confidence", 0.0),
                has_significant_audio=result.get("has_significant_audio", True)
            )

        except Exception as e:
            import traceback
            print(f"❌ Error extracting transcript: {type(e).__name__}: {e}")
            print(traceback.format_exc())
            return TranscriptData(
                text="",
                language="unknown",
                language_confidence=0.0,
                has_significant_audio=False
            )

    async def generate_headline_from_text(self, transcript: str) -> HeadlineData:
        """
        Generate engaging headline from transcript text ONLY (no video).
        EFFICIENT: Text-only analysis, no video re-upload needed.
        LANGUAGE-AWARE: Generates headlines in the same language as the transcript.

        Args:
            transcript: Combined transcript (speech + visible text)

        Returns:
            HeadlineData with primary headline and alternatives
        """
        try:
            if not transcript or len(transcript.strip()) < 5:
                return HeadlineData(
                    primary="செய்தி வீடியோ",
                    alternatives=[],
                    confidence=0.2,
                    tone="neutral"
                )

            prompt = f"""
            Based on this video transcript, generate a short and engaging news headline.

            Transcript:
            {transcript[:2000]}

            CRITICAL LANGUAGE INSTRUCTION:
            - Detect the language of the transcript carefully
            - Generate ALL headlines in the EXACT SAME LANGUAGE as the transcript
            - If transcript is in Tamil (தமிழ்), ALL headlines MUST be in Tamil script only
            - If transcript is in Hindi (हिंदी), ALL headlines MUST be in Hindi script only
            - If transcript is in English, ALL headlines MUST be in English only
            - Do NOT translate or mix languages — use only the native script
            - Preserve the native script and writing system exactly

            Create a news-style headline that is:
            - 5-12 words (or equivalent in the detected language)
            - Factual and descriptive — based strictly on what the transcript says
            - Suitable for a news broadcast overlay
            - Do NOT invent content not present in the transcript

            Return a JSON object with this exact structure:
            {{
                "primary": "Main news headline in the detected language",
                "alternatives": ["Alt 1 in same language", "Alt 2 in same language"],
                "confidence": 0.85,
                "tone": "informative"
            }}
            """

            response = self._generate_with_retry(prompt=prompt, temperature=0.4)
            result = json.loads(response.text.strip())

            primary = result.get("primary", "").strip()
            if not primary:
                # Use first 80 chars of transcript as last resort
                primary = transcript.strip()[:80]

            return HeadlineData(
                primary=primary,
                alternatives=result.get("alternatives", []),
                confidence=result.get("confidence", 0.5),
                tone=result.get("tone", "informative")
            )

        except Exception as e:
            print(f"Error generating headline: {e}")
            # Use transcript itself as fallback instead of generic text
            fallback = transcript.strip()[:80] if transcript and transcript.strip() else "செய்தி வீடியோ"
            return HeadlineData(
                primary=fallback,
                alternatives=[],
                confidence=0.2,
                tone="neutral"
            )

    async def detect_location_from_text(self, transcript: str) -> LocationData:
        """
        Detect location from transcript text ONLY (no video).
        EFFICIENT: Text-only analysis, no video re-upload needed.
        LANGUAGE-AWARE: Returns location in the same language as the transcript.

        Args:
            transcript: Combined transcript (speech + visible text)

        Returns:
            LocationData with detected location
        """
        try:
            if not transcript or len(transcript.strip()) < 10:
                return LocationData(
                    text=None,
                    confidence=0.0,
                    source="none",
                    coordinates=None
                )

            prompt = f"""
            Identify any location mentioned in this video transcript.

            Transcript:
            {transcript[:1000]}

            CRITICAL LANGUAGE INSTRUCTION:
            - Detect the language of the transcript carefully
            - Return the location name in the EXACT SAME LANGUAGE as the transcript
            - If transcript is in Tamil (தமிழ்), return location in Tamil ONLY (e.g., "திருவாரூர், தமிழ்நாடு, இந்தியா")
            - If transcript is in Hindi (हिंदी), return location in Hindi ONLY (e.g., "दिल्ली, भारत")
            - If transcript is in English, return location in English ONLY (e.g., "Paris, France")
            - Do NOT mix languages - use only the native script of the detected language

            Return a JSON object with this exact structure:
            {{
                "text": "City, Region, Country in the detected language" or null if no location detected,
                "confidence": 0.85,
                "source": "transcript"
            }}

            Guidelines:
            - Look for place names, landmarks, cities, regions mentioned
            - Return location in the same language and script as the transcript
            - If uncertain, set text to null and confidence low

            IMPORTANT: The location text MUST be in the same language as the transcript.
            """

            response = self._generate_with_retry(prompt=prompt, temperature=0.3)
            result = json.loads(response.text.strip())

            return LocationData(
                text=result.get("text"),
                confidence=result.get("confidence", 0.0),
                source=result.get("source", "transcript"),
                coordinates=None
            )

        except Exception as e:
            print(f"Error detecting location: {e}")
            return LocationData(
                text=None,
                confidence=0.0,
                source="none",
                coordinates=None
            )
