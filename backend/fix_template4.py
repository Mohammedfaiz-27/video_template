"""Fix Template 4 with logo support and new design."""
import re

# Read the file
with open('app/services/simple_overlay_renderer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# New Template 4 implementation
new_template4 = '''    @staticmethod
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
'''

# Find and replace the template4 function
# Pattern: from "def create_template4_overlay" to the next "@staticmethod"
pattern = r'(@staticmethod\s+def create_template4_overlay.*?)(\s+@staticmethod\s+def _wrap_text)'

content = re.sub(pattern, new_template4 + r'\2', content, flags=re.DOTALL)

# Write back
with open('app/services/simple_overlay_renderer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Template 4 updated successfully!")
print("Logo should now appear at: backend/assets/tiruvarur_logo.png")
