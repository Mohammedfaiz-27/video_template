"""Simple overlay renderer using Pillow (no Chrome needed)."""

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os


class SimpleOverlayRenderer:
    """Create video overlays using Pillow instead of html2image."""

    @staticmethod
    def create_overlay(
        template_name: str,
        output_path: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True,
        width: int = 1080,
        height: int = 1920
    ) -> bool:
        """
        Create overlay for any template.

        Args:
            template_name: Template name (template1, template2, template3, template4)
            output_path: Where to save PNG
            headline: Headline text
            location: Location text
            show_location: Whether to show location
            width: Image width
            height: Image height

        Returns:
            True if successful
        """
        # Extract template number
        template_num = template_name.replace('.html', '').replace('template', '')

        if template_num == '1':
            return SimpleOverlayRenderer.create_template1_overlay(
                output_path, headline, location, show_location, width, height
            )
        elif template_num == '2':
            return SimpleOverlayRenderer.create_template2_overlay(
                output_path, headline, location, show_location, width, height
            )
        elif template_num == '3':
            return SimpleOverlayRenderer.create_template3_overlay(
                output_path, headline, location, show_location, width, height
            )
        elif template_num == '4':
            return SimpleOverlayRenderer.create_template4_overlay(
                output_path, headline, location, show_location, width, height
            )
        else:
            print(f"❌ Unknown template: {template_name}")
            return False

    @staticmethod
    def create_template1_overlay(
        output_path: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True,
        width: int = 1080,
        height: int = 1920
    ) -> bool:
        """Template 1: Full Frame Golden."""
        try:
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Load fonts
            try:
                font_headline = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 52)
                font_date = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
                font_location = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 38)
                font_logo = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 32)
            except:
                font_headline = font_date = font_location = font_logo = ImageFont.load_default()

            # Golden gradient top bar (approximation)
            gold_color = (255, 215, 0, 230)  # Golden
            draw.rectangle([0, 0, width, 280], fill=gold_color)

            # Logo box (top right)
            logo_x, logo_y = width - 230, 40
            draw.rectangle([logo_x, logo_y, logo_x+180, logo_y+70],
                          fill=(255, 255, 255, 255), outline=gold_color, width=3)
            draw.text((logo_x+90, logo_y+35), "NEWS", fill=gold_color,
                     font=font_logo, anchor="mm")

            # Date
            current_date = datetime.now().strftime("%d %B %Y")
            draw.text((60, 180), current_date, fill=(255, 255, 255, 255), font=font_date)

            # Headline box (bottom)
            headline_y = height - 450
            headline_bg = (255, 255, 255, 242)
            draw.rectangle([60, headline_y, width-60, headline_y+180],
                          fill=headline_bg)
            # Golden left border
            draw.rectangle([60, headline_y, 70, headline_y+180], fill=gold_color)

            # Headline text
            headline_wrapped = SimpleOverlayRenderer._wrap_text(headline, font_headline, width-180)
            draw.multiline_text((width//2, headline_y+90), headline_wrapped,
                               fill=(44, 44, 44, 255), font=font_headline,
                               anchor="mm", align="center")

            # Location
            if show_location and location:
                loc_y = height - 180
                loc_bg = (255, 215, 0, 242)
                draw.ellipse([60, loc_y, 110, loc_y+50], fill=loc_bg)
                draw.ellipse([width-110, loc_y, width-60, loc_y+50], fill=loc_bg)
                draw.rectangle([85, loc_y, width-85, loc_y+50], fill=loc_bg)

                loc_text = f"📍 {location}"
                draw.text((width//2, loc_y+25), loc_text,
                         fill=(44, 44, 44, 255), font=font_location, anchor="mm")

            img.save(output_path, 'PNG')
            print(f"✅ Created Template 1 overlay")
            return True
        except Exception as e:
            print(f"❌ Error creating Template 1: {e}")
            return False

    @staticmethod
    def create_template2_overlay(
        output_path: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True,
        width: int = 1080,
        height: int = 1920
    ) -> bool:
        """Template 2: Split Video Orange."""
        try:
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Load fonts
            try:
                font_headline = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
                font_logo = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
                font_date = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 32)
                font_location = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
            except:
                font_headline = font_logo = font_date = font_location = ImageFont.load_default()

            # Orange top bar
            orange_color = (255, 107, 53, 240)
            draw.rectangle([0, 0, width, 180], fill=orange_color)

            # Logo text
            draw.text((80, 50), "NEWS BROADCAST", fill=(255, 255, 255, 255),
                     font=font_logo)

            # LIVE indicator
            live_bg = (255, 0, 0, 255)
            draw.ellipse([width-180, 35, width-80, 75], fill=live_bg)
            draw.text((width-130, 55), "● LIVE", fill=(255, 255, 255, 255),
                     font=font_date, anchor="mm")

            # Headline box (below video area)
            headline_y = height - 520
            headline_bg = (255, 107, 53, 242)
            draw.rectangle([80, headline_y, width-80, headline_y+170],
                          fill=headline_bg)

            # Headline text
            headline_wrapped = SimpleOverlayRenderer._wrap_text(headline, font_headline, width-200)
            draw.multiline_text((width//2, headline_y+85), headline_wrapped,
                               fill=(255, 255, 255, 255), font=font_headline,
                               anchor="mm", align="center")

            # Bottom bar
            bottom_bg = (45, 45, 45, 240)
            draw.rectangle([0, height-150, width, height], fill=bottom_bg)
            # Orange top border
            draw.rectangle([0, height-154, width, height-150], fill=orange_color)

            # Location and date in bottom bar
            if show_location and location:
                draw.text((80, height-90), f"📍 {location}",
                         fill=orange_color, font=font_location)

            current_date = datetime.now().strftime("%d %B %Y")
            draw.text((width-80, height-90), current_date,
                     fill=(255, 255, 255, 255), font=font_date, anchor="rm")

            img.save(output_path, 'PNG')
            print(f"✅ Created Template 2 overlay")
            return True
        except Exception as e:
            print(f"❌ Error creating Template 2: {e}")
            return False

    @staticmethod
    def create_template3_overlay(
        output_path: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True,
        width: int = 1080,
        height: int = 1920
    ) -> bool:
        """Template 3: Minimal Modern."""
        try:
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Load fonts
            try:
                font_headline = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 50)
                font_date = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 26)
                font_location = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
            except:
                font_headline = font_date = font_location = ImageFont.load_default()

            # Top line
            draw.rectangle([0, 0, width, 6], fill=(0, 0, 0, 255))

            # Date badge (top right)
            date_x, date_y = width - 220, 40
            date_bg = (0, 0, 0, 217)
            draw.rectangle([date_x, date_y, date_x+180, date_y+50],
                          fill=date_bg)
            current_date = datetime.now().strftime("%d %B %Y")
            draw.text((date_x+90, date_y+25), current_date,
                     fill=(255, 255, 255, 255), font=font_date, anchor="mm")

            # Headline box
            headline_y = height - 520
            headline_bg = (255, 255, 255, 242)
            draw.rectangle([60, headline_y, width-60, headline_y+190],
                          fill=headline_bg)
            # Black left border
            draw.rectangle([60, headline_y, 68, headline_y+190], fill=(0, 0, 0, 255))

            # Headline text
            headline_wrapped = SimpleOverlayRenderer._wrap_text(headline, font_headline, width-180)
            draw.multiline_text((width//2, headline_y+95), headline_wrapped,
                               fill=(26, 26, 26, 255), font=font_headline,
                               anchor="mm", align="center")

            # Location
            if show_location and location:
                loc_y = height - 240
                loc_bg = (0, 0, 0, 217)
                draw.ellipse([60, loc_y, 110, loc_y+50], fill=loc_bg)
                draw.ellipse([width-110, loc_y, width-60, loc_y+50], fill=loc_bg)
                draw.rectangle([85, loc_y, width-85, loc_y+50], fill=loc_bg)

                loc_text = f"📍 {location}"
                draw.text((width//2, loc_y+25), loc_text,
                         fill=(255, 255, 255, 255), font=font_location, anchor="mm")

            # Bottom accent
            draw.rectangle([60, height-40, 260, height-36], fill=(0, 0, 0, 255))

            img.save(output_path, 'PNG')
            print(f"✅ Created Template 3 overlay")
            return True
        except Exception as e:
            print(f"❌ Error creating Template 3: {e}")
            return False

    @staticmethod
    def create_template4_overlay(
        output_path: str,
        headline: str,
        location: Optional[str] = None,
        show_location: bool = True,
        width: int = 1080,
        height: int = 1920
    ) -> bool:
        """Template 4: Tiruvarur Updates with rounded corners and logo."""
        try:
            # Create transparent image
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Colors
            border_color = (139, 37, 0, 255)  # #8b2500
            top_color = (196, 59, 0, 240)  # #c43b00

            # Load fonts
            try:
                font_headline = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 50)
                font_location = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
            except:
                font_headline = font_location = ImageFont.load_default()

            # 1. Draw rounded border frame
            border_width = 20
            corner_radius = 40

            # Draw rounded rectangle for border
            draw.rectangle([0, 0, width, height], fill=border_color)
            draw.rectangle([border_width, border_width,
                           width-border_width, height-border_width],
                          fill=(0, 0, 0, 0))

            # 2. Draw red/maroon top section (300px)
            top_height = 300
            draw.rectangle([border_width, border_width,
                           width-border_width, top_height],
                          fill=top_color)

            # 3. Load and place logo
            logo_path = Path(__file__).parent.parent.parent / 'assets' / 'tiruvarur_logo.png'
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    # Resize to 120x120
                    logo = logo.resize((120, 120), Image.Resampling.LANCZOS)

                    # Create circular mask
                    mask = Image.new('L', (120, 120), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse([0, 0, 120, 120], fill=255)

                    # Position: top-right of video area
                    logo_x = width - 180
                    logo_y = top_height + 20

                    # Paste logo with mask
                    img.paste(logo, (logo_x, logo_y), mask)
                    print(f"   Logo added at ({logo_x}, {logo_y})")
                except Exception as e:
                    print(f"   Logo error: {e}")
            else:
                print(f"   No logo at: {logo_path}")

            # 4. Headline box at bottom
            headline_y = height - 350
            headline_height = 200
            headline_bg = (255, 255, 255, 250)

            # Draw headline background with rounded corners
            draw.rectangle([40, headline_y, width-40, headline_y+headline_height],
                          fill=headline_bg)

            # Red left accent
            draw.rectangle([40, headline_y, 50, headline_y+headline_height],
                          fill=border_color)

            # Headline text
            headline_wrapped = SimpleOverlayRenderer._wrap_text(
                headline, font_headline, width-140
            )
            draw.multiline_text((width//2, headline_y + headline_height//2),
                               headline_wrapped,
                               fill=(40, 20, 10, 255), font=font_headline,
                               anchor="mm", align="center")

            # 5. Location at bottom
            if show_location and location:
                loc_y = height - 100
                loc_bg = border_color

                # Rounded location box
                draw.ellipse([width//2-200, loc_y, width//2-170, loc_y+60], fill=loc_bg)
                draw.ellipse([width//2+170, loc_y, width//2+200, loc_y+60], fill=loc_bg)
                draw.rectangle([width//2-170, loc_y, width//2+170, loc_y+60], fill=loc_bg)

                # Location text
                loc_text = f"📍 {location}"
                draw.text((width//2, loc_y+30), loc_text,
                         fill=(255, 255, 255, 255), font=font_location, anchor="mm")

            # Save
            img.save(output_path, 'PNG')
            print(f"Created Template 4 (Tiruvarur Updates)")
            return True

        except Exception as e:
            print(f"Error creating Template 4: {e}")
            import traceback
            traceback.print_exc()
            return False


    @staticmethod
    def _wrap_text(text: str, font, max_width: int) -> str:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            # Create a dummy draw to measure text
            test_img = Image.new('RGB', (1, 1))
            test_draw = ImageDraw.Draw(test_img)
            bbox = test_draw.textbbox((0, 0), ' '.join(current_line), font=font)
            width = bbox[2] - bbox[0]

            if width > max_width:
                if len(current_line) == 1:
                    lines.append(current_line[0])
                    current_line = []
                else:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)
