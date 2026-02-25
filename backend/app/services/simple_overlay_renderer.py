"""Simple overlay renderer using Pillow (no Chrome needed)."""

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os


class SimpleOverlayRenderer:
    """Create video overlays using Pillow instead of html2image."""

    # Get the project's font directory
    FONTS_DIR = Path(__file__).parent.parent.parent / 'assets' / 'fonts'

    @staticmethod
    def _has_tamil(text: str) -> bool:
        """Return True if text contains any Tamil Unicode characters."""
        return any('\u0B80' <= ch <= '\u0BFF' for ch in text)

    @staticmethod
    def _load_font(size: int, bold: bool = True, text: str = "") -> ImageFont.FreeTypeFont:
        """
        Load the best font for the given text (Tamil or Latin).
        - Tamil text  → NotoSansTamil (project asset, always present)
        - Latin text  → Arial Bold / Arial (system fonts)
        - Fallback    → Nirmala.ttc (supports both scripts)
        """
        fonts_dir = SimpleOverlayRenderer.FONTS_DIR

        if SimpleOverlayRenderer._has_tamil(text):
            # Tamil script: prefer NotoSansTamil, fall back to Nirmala
            candidates = [
                str(fonts_dir / ("NotoSansTamil-Bold.ttf" if bold else "NotoSansTamil-Regular.ttf")),
                str(fonts_dir / "NotoSansTamil-Regular.ttf"),
                str(fonts_dir / "NotoSansTamil-Bold.ttf"),
                "C:/Windows/Fonts/Nirmala.ttc",
            ]
        else:
            # Latin / English: prefer Arial, fall back to Nirmala
            candidates = [
                "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/Nirmala.ttc",
            ]

        for font_path in candidates:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, size)
                    print(f"   ✓ Loaded font: {os.path.basename(font_path)}")
                    return font
            except Exception:
                continue

        print("⚠️ Warning: No suitable font found, using default")
        return ImageFont.load_default()

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

            loc_text_for_font = location or ""
            font_headline = SimpleOverlayRenderer._load_font(52, bold=True, text=headline)
            font_date = SimpleOverlayRenderer._load_font(36, bold=True, text="")
            font_location = SimpleOverlayRenderer._load_font(38, bold=True, text=loc_text_for_font)
            font_logo = SimpleOverlayRenderer._load_font(32, bold=True, text="")

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

            loc_text_for_font = location or ""
            font_headline = SimpleOverlayRenderer._load_font(48, bold=True, text=headline)
            font_logo = SimpleOverlayRenderer._load_font(48, bold=True, text="")
            font_date = SimpleOverlayRenderer._load_font(32, bold=True, text="")
            font_location = SimpleOverlayRenderer._load_font(36, bold=True, text=loc_text_for_font)

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

            loc_text_for_font = location or ""
            font_headline = SimpleOverlayRenderer._load_font(50, bold=False, text=headline)
            font_date = SimpleOverlayRenderer._load_font(26, bold=False, text="")
            font_location = SimpleOverlayRenderer._load_font(30, bold=False, text=loc_text_for_font)

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
        """Template 4: Tiruvarur Updates - NEW DESIGN matching HTML."""
        try:
            # Create transparent image
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Colors from new HTML design
            border_color = (122, 32, 13, 255)  # #7a200d
            header_color = (122, 32, 13, 255)  # #7a200d (same as border)
            header_bottom_border = (92, 26, 26, 255)  # #5c1a1a

            loc_text_for_font = location or ""
            font_headline = SimpleOverlayRenderer._load_font(55, bold=True, text=headline)
            font_location = SimpleOverlayRenderer._load_font(32, bold=True, text=loc_text_for_font)
            font_date = SimpleOverlayRenderer._load_font(32, bold=True, text="")

            # 1. Draw border frame (sides and bottom only)
            border_width = 20
            # Left border
            draw.rectangle([0, 0, border_width, height], fill=border_color)
            # Right border
            draw.rectangle([width-border_width, 0, width, height], fill=border_color)
            # Bottom border
            draw.rectangle([0, height-border_width, width, height], fill=border_color)

            # 2. Draw red header block at top (starts from very top)
            header_height = 300
            header_y = 0

            # Draw rounded rectangle for header
            draw.rectangle([border_width, header_y, width-border_width, header_y+header_height],
                          fill=header_color)

            # Add bottom border to header
            draw.rectangle([border_width, header_y+header_height-4, width-border_width, header_y+header_height],
                          fill=header_bottom_border)

            # 3. Draw headline text in header (centered, white text)
            headline_wrapped = SimpleOverlayRenderer._wrap_text(headline, font_headline, width-100)

            # Calculate text position (centered in header)
            text_y = header_y + header_height//2

            draw.multiline_text((width//2, text_y), headline_wrapped,
                               fill=(255, 255, 255, 255), font=font_headline,
                               anchor="mm", align="center")

            # 4. Load and place logo (top right, below header)
            logo_path = Path(__file__).parent.parent.parent / 'assets' / 'tiruvarur_logo.png'
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    logo = logo.resize((130, 130), Image.Resampling.LANCZOS)

                    # Create circular mask
                    mask = Image.new('L', (130, 130), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse([0, 0, 130, 130], fill=255)

                    # Position: below header, top right
                    logo_x = width - 40 - 130  # 40px from right
                    logo_y = header_y + header_height + 30  # 30px below header

                    # Paste with circular mask
                    img.paste(logo, (logo_x, logo_y), mask)

                    # Draw white border around logo
                    mask_draw2 = ImageDraw.Draw(img)
                    mask_draw2.ellipse([logo_x-2, logo_y-2, logo_x+132, logo_y+132],
                                      outline=(255, 255, 255, 255), width=4)

                    print(f"   Logo added at ({logo_x}, {logo_y})")
                except Exception as e:
                    print(f"   Logo error: {e}")

            # 5. Location box (bottom left)
            if show_location and location:
                loc_y = height - 100
                loc_x = 40

                # Load smaller font for location (match language of location text)
                font_location_small = SimpleOverlayRenderer._load_font(28, bold=True, text=location)

                # Calculate text width with smaller font
                loc_text = f"📍 {location}"
                test_img = Image.new('RGB', (1, 1))
                test_draw = ImageDraw.Draw(test_img)
                bbox = test_draw.textbbox((0, 0), loc_text, font=font_location_small)
                text_width = bbox[2] - bbox[0]

                # Dynamic box width (minimum 300px, maximum 600px to match HTML)
                loc_width = min(max(text_width + 80, 300), 600)
                loc_height = 62

                # Draw background with rounded left side, straight right side
                loc_bg = (163, 42, 13, 255)  # #a32a0d
                draw.ellipse([loc_x, loc_y, loc_x+60, loc_y+loc_height], fill=loc_bg)
                draw.rectangle([loc_x+30, loc_y, loc_x+loc_width, loc_y+loc_height], fill=loc_bg)

                # White border on left rounded side
                draw.ellipse([loc_x-1, loc_y-1, loc_x+61, loc_y+loc_height+1], outline=(255, 255, 255, 255), width=2)
                # White border on top, right, bottom edges
                draw.line([loc_x+30, loc_y, loc_x+loc_width, loc_y], fill=(255, 255, 255, 255), width=2)
                draw.line([loc_x+loc_width, loc_y, loc_x+loc_width, loc_y+loc_height], fill=(255, 255, 255, 255), width=2)
                draw.line([loc_x+30, loc_y+loc_height, loc_x+loc_width, loc_y+loc_height], fill=(255, 255, 255, 255), width=2)

                # Location text (using smaller font to match HTML 28px)
                draw.text((loc_x+loc_width//2, loc_y+31), loc_text,
                         fill=(255, 255, 255, 255), font=font_location_small, anchor="mm")

            # 6. Date box (bottom right)
            from datetime import datetime
            current_date = datetime.now().strftime("%d-%m-%Y")

            date_y = height - 100
            date_x = width - 240
            date_width = 200
            date_height = 62

            # Semi-transparent black background
            date_bg = (0, 0, 0, 153)  # 0.6 opacity
            draw.rectangle([date_x, date_y, date_x+date_width, date_y+date_height],
                          fill=date_bg)

            # Red left border accent
            draw.rectangle([date_x, date_y, date_x+5, date_y+date_height],
                          fill=(163, 42, 13, 255))

            # Date text
            draw.text((date_x+date_width//2, date_y+date_height//2), current_date,
                     fill=(255, 255, 255, 255), font=font_date, anchor="mm")

            # Save
            img.save(output_path, 'PNG')
            print(f"Created Template 4 (Tiruvarur Updates - New Design)")
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
