"""Gemini AI service for video analysis, transcript, headline, and location detection."""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image
import google.generativeai as genai

from app.config import settings
from app.models.video import TranscriptData, VisualAnalysis, HeadlineData, LocationData


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize Gemini service with API key."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_video_complete(
        self,
        video_path: str
    ) -> Tuple[TranscriptData, VisualAnalysis, HeadlineData, LocationData]:
        """
        Complete video analysis pipeline.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (transcript, visual_analysis, headline, location)
        """
        print(f"🎬 Starting complete analysis for: {video_path}")

        # Upload video to Gemini
        video_file = await self._upload_video_to_gemini(video_path)

        # Extract transcript
        transcript = await self.extract_transcript(video_file)
        print(f"✓ Transcript extracted: {len(transcript.text)} chars")

        # Analyze visual content
        visual = await self.analyze_visual_content(video_file)
        print(f"✓ Visual analysis complete: {visual.scene_type}")

        # Generate headline
        headline = await self.generate_headline(transcript.text, visual)
        print(f"✓ Headline generated: {headline.primary}")

        # Detect location
        location = await self.detect_location(transcript.text, visual)
        if location.text:
            print(f"✓ Location detected: {location.text}")
        else:
            print("ℹ No location detected")

        return transcript, visual, headline, location

    async def _upload_video_to_gemini(self, video_path: str):
        """
        Upload video file to Gemini API using File API.

        Args:
            video_path: Path to video file

        Returns:
            Gemini file object
        """
        try:
            print(f"📤 Uploading video to Gemini...")

            # Use the Files API to upload
            video_file = genai.upload_file(video_path)
            print(f"✓ Uploaded file: {video_file.name}")

            # Wait for processing to complete
            while video_file.state.name == "PROCESSING":
                print("⏳ Waiting for video processing...")
                time.sleep(5)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                raise Exception(f"Video processing failed")

            print(f"✓ Video ready for analysis")
            return video_file

        except AttributeError as e:
            # Fallback: If upload_file doesn't exist, return path for direct use
            print(f"⚠️ File upload API not available, using direct video path")
            print(f"   This may work with shorter videos only")
            return video_path
        except Exception as e:
            print(f"❌ Error uploading video: {e}")
            raise

    async def extract_transcript(self, video_file) -> TranscriptData:
        """
        Extract audio transcript from video using Gemini.

        Args:
            video_file: Gemini uploaded video file

        Returns:
            TranscriptData with transcript text and metadata
        """
        try:
            prompt = """
            Analyze the audio in this video and provide a complete transcript.

            Return a JSON object with this exact structure:
            {
                "text": "Complete transcript of all spoken words",
                "language": "detected language code (e.g., 'en', 'hi', 'es')",
                "language_confidence": 0.95,
                "has_significant_audio": true
            }

            If there is no speech, set text to empty string and has_significant_audio to false.
            Be accurate with language detection.
            """

            response = self.model.generate_content(
                [video_file, prompt],
                generation_config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )

            # Parse response
            result = json.loads(response.text)

            return TranscriptData(
                text=result.get("text", ""),
                language=result.get("language", "en"),
                language_confidence=result.get("language_confidence", 0.0),
                has_significant_audio=result.get("has_significant_audio", True)
            )

        except Exception as e:
            print(f"❌ Error extracting transcript: {e}")
            # Return empty transcript on error
            return TranscriptData(
                text="",
                language="unknown",
                language_confidence=0.0,
                has_significant_audio=False
            )

    async def analyze_visual_content(self, video_file) -> VisualAnalysis:
        """
        Analyze visual content of video using Gemini.

        Args:
            video_file: Gemini uploaded video file

        Returns:
            VisualAnalysis with scene information
        """
        try:
            prompt = """
            Analyze the visual content of this video thoroughly.

            Return a JSON object with this exact structure:
            {
                "scene_type": "outdoor/indoor/mixed",
                "people_count": 2,
                "objects": ["tree", "building", "car"],
                "mood": "happy/sad/energetic/calm/professional/casual",
                "landmarks": ["Eiffel Tower", "Golden Gate Bridge"],
                "description": "Brief description of what's happening in the video"
            }

            - scene_type: Classify the primary setting
            - people_count: Estimate number of people visible
            - objects: List 3-5 prominent objects or elements
            - mood: Overall tone/atmosphere
            - landmarks: Any recognizable landmarks or famous locations (empty array if none)
            - description: 1-2 sentence summary of the visual content
            """

            response = self.vision_model.generate_content(
                [video_file, prompt],
                generation_config={
                    "temperature": 0.4,
                    "response_mime_type": "application/json"
                }
            )

            # Parse response
            result = json.loads(response.text)

            return VisualAnalysis(
                scene_type=result.get("scene_type", "unknown"),
                people_count=result.get("people_count", 0),
                objects=result.get("objects", []),
                mood=result.get("mood", "neutral"),
                landmarks=result.get("landmarks", []),
                description=result.get("description", "")
            )

        except Exception as e:
            print(f"❌ Error analyzing visual content: {e}")
            return VisualAnalysis(
                scene_type="unknown",
                people_count=0,
                objects=[],
                mood="neutral",
                landmarks=[],
                description="Visual analysis failed"
            )

    async def generate_headline(
        self,
        transcript: str,
        visual_analysis: VisualAnalysis
    ) -> HeadlineData:
        """
        Generate engaging headline based on transcript and visual analysis.

        Args:
            transcript: Video transcript text
            visual_analysis: Visual content analysis

        Returns:
            HeadlineData with primary headline and alternatives
        """
        try:
            # Build context
            context = f"""
            Video Transcript: {transcript[:500] if transcript else "No speech detected"}

            Visual Context:
            - Scene: {visual_analysis.scene_type}
            - People: {visual_analysis.people_count}
            - Objects: {', '.join(visual_analysis.objects)}
            - Mood: {visual_analysis.mood}
            - Description: {visual_analysis.description}
            """

            prompt = f"""
            Based on this video analysis, generate engaging headlines for social media.

            {context}

            Create headlines that are:
            - 5-10 words long
            - Attention-grabbing and click-worthy
            - Relevant to the content
            - Suitable for platforms like Instagram, TikTok, YouTube Shorts
            - Natural and conversational

            Return a JSON object with this exact structure:
            {{
                "primary": "Most engaging headline",
                "alternatives": ["Alternative headline 1", "Alternative headline 2", "Alternative headline 3"],
                "confidence": 0.85,
                "tone": "exciting/informative/funny/emotional/inspirational"
            }}

            Make the primary headline the absolute best option.
            """

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "response_mime_type": "application/json"
                }
            )

            # Parse response
            result = json.loads(response.text)

            return HeadlineData(
                primary=result.get("primary", "Untitled Video"),
                alternatives=result.get("alternatives", []),
                confidence=result.get("confidence", 0.5),
                tone=result.get("tone", "neutral")
            )

        except Exception as e:
            print(f"❌ Error generating headline: {e}")
            return HeadlineData(
                primary="Amazing Video",
                alternatives=["Watch This!", "You Won't Believe This"],
                confidence=0.3,
                tone="neutral"
            )

    async def detect_location(
        self,
        transcript: str,
        visual_analysis: VisualAnalysis
    ) -> LocationData:
        """
        Detect location from transcript and visual analysis.

        Args:
            transcript: Video transcript text
            visual_analysis: Visual content analysis

        Returns:
            LocationData with detected location
        """
        try:
            # Check if landmarks are detected
            has_landmarks = len(visual_analysis.landmarks) > 0

            context = f"""
            Video Transcript: {transcript[:300] if transcript else "No speech detected"}

            Visual Analysis:
            - Scene: {visual_analysis.scene_type}
            - Landmarks: {', '.join(visual_analysis.landmarks) if has_landmarks else "None detected"}
            - Description: {visual_analysis.description}
            """

            prompt = f"""
            Identify any location mentioned or visible in this video.

            {context}

            Return a JSON object with this exact structure:
            {{
                "text": "City, State/Region, Country" or null if no location detected,
                "confidence": 0.85,
                "source": "transcript/visual/landmark/none"
            }}

            Guidelines:
            - If landmarks are detected, use them to determine location
            - If location is mentioned in transcript, extract it
            - If visual clues suggest a location, identify it
            - Format: "City, Region, Country" (e.g., "Paris, Île-de-France, France")
            - If uncertain, set text to null and confidence low
            - source: where the location info came from
            """

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )

            # Parse response
            result = json.loads(response.text)

            return LocationData(
                text=result.get("text"),
                confidence=result.get("confidence", 0.0),
                source=result.get("source", "none"),
                coordinates=None  # TODO: Add geocoding if needed
            )

        except Exception as e:
            print(f"❌ Error detecting location: {e}")
            return LocationData(
                text=None,
                confidence=0.0,
                source="none",
                coordinates=None
            )

    async def refine_headline_with_context(
        self,
        headline: str,
        context: str
    ) -> str:
        """
        Refine a headline with additional context.

        Args:
            headline: Original headline
            context: Additional context or user feedback

        Returns:
            Refined headline
        """
        try:
            prompt = f"""
            Refine this headline based on the context provided.

            Original Headline: {headline}
            Context: {context}

            Return a single refined headline (5-10 words) that incorporates the context.
            Keep it engaging and click-worthy.
            """

            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.7}
            )

            return response.text.strip()

        except Exception as e:
            print(f"❌ Error refining headline: {e}")
            return headline
