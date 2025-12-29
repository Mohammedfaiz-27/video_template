"""Perplexity AI service for headline refinement (optional)."""

from typing import List, Optional
from openai import OpenAI

from app.config import settings


class PerplexityService:
    """Service for interacting with Perplexity API (OpenAI-compatible)."""

    def __init__(self):
        """Initialize Perplexity service with API key."""
        if not settings.PERPLEXITY_API_KEY:
            print("⚠️  Perplexity API key not configured (optional)")
            self.client = None
            return

        self.client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )

    def is_available(self) -> bool:
        """Check if Perplexity service is available."""
        return self.client is not None

    async def refine_headline(
        self,
        headline: str,
        context: str,
        alternatives: List[str] = None
    ) -> str:
        """
        Refine headline using Perplexity for better engagement.

        Args:
            headline: Original headline
            context: Video context (transcript, visual analysis)
            alternatives: Alternative headlines to consider

        Returns:
            Refined headline
        """
        if not self.is_available():
            print("⚠️  Perplexity not available, returning original headline")
            return headline

        try:
            # Build prompt
            alternatives_text = ""
            if alternatives:
                alternatives_text = "\n".join([f"- {alt}" for alt in alternatives])
                alternatives_text = f"\n\nAlternative headlines:\n{alternatives_text}"

            prompt = f"""
            You are an expert social media content creator specializing in viral video headlines.

            Original headline: {headline}
            {alternatives_text}

            Video context: {context[:300]}

            Task: Refine or improve this headline to maximize engagement on platforms like TikTok, Instagram Reels, and YouTube Shorts.

            Requirements:
            - 5-10 words maximum
            - Click-worthy and attention-grabbing
            - Authentic and not clickbait
            - Match the video's actual content
            - Use emotional triggers when appropriate

            Return ONLY the refined headline, nothing else.
            """

            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media headline expert. Return only the headline, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=50
            )

            refined = response.choices[0].message.content.strip()

            # Remove quotes if present
            refined = refined.strip('"\'')

            print(f"✨ Perplexity refined headline: {refined}")
            return refined

        except Exception as e:
            print(f"❌ Error refining headline with Perplexity: {e}")
            return headline

    async def generate_alternative_headlines(
        self,
        context: str,
        count: int = 3
    ) -> List[str]:
        """
        Generate alternative headlines using Perplexity.

        Args:
            context: Video context
            count: Number of alternatives to generate

        Returns:
            List of alternative headlines
        """
        if not self.is_available():
            return []

        try:
            prompt = f"""
            Generate {count} engaging headlines for a video based on this context:

            {context[:400]}

            Requirements:
            - 5-10 words each
            - Diverse in tone and style
            - Optimized for social media engagement
            - No numbering or bullets

            Return only the headlines, one per line.
            """

            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media headline expert."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=150
            )

            headlines_text = response.choices[0].message.content.strip()
            headlines = [h.strip().strip('"\'') for h in headlines_text.split('\n') if h.strip()]

            return headlines[:count]

        except Exception as e:
            print(f"❌ Error generating alternatives with Perplexity: {e}")
            return []

    async def compare_headlines(
        self,
        headlines: List[str],
        context: str
    ) -> str:
        """
        Compare multiple headlines and return the best one.

        Args:
            headlines: List of headlines to compare
            context: Video context

        Returns:
            Best headline
        """
        if not self.is_available() or not headlines:
            return headlines[0] if headlines else "Untitled"

        try:
            headlines_list = "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])

            prompt = f"""
            Compare these headlines for a video and select the BEST one for maximum engagement:

            {headlines_list}

            Video context: {context[:300]}

            Evaluate based on:
            - Engagement potential
            - Authenticity
            - Relevance to content
            - Emotional impact
            - Social media optimization

            Return ONLY the number of the best headline (1, 2, 3, etc.), nothing else.
            """

            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media expert. Return only a number."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=10
            )

            # Get the selected number
            selection = response.choices[0].message.content.strip()
            try:
                index = int(selection) - 1
                if 0 <= index < len(headlines):
                    return headlines[index]
            except ValueError:
                pass

            # Fallback to first headline
            return headlines[0]

        except Exception as e:
            print(f"❌ Error comparing headlines with Perplexity: {e}")
            return headlines[0] if headlines else "Untitled"
