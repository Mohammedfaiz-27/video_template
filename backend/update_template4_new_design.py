"""Update Template 4 Pillow renderer to match the new HTML design."""
import re

new_template4_code = '''    @staticmethod
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
            header_color = (163, 42, 13, 255)  # #a32a0d
            header_bottom_border = (92, 26, 26, 255)  # #5c1a1a

            # Load fonts
            try:
                font_headline = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 55)
                font_location = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 32)
                font_date = ImageFont.truetype("C:/Windows/Fonts/cour.ttf", 32)
            except:
                font_headline = font_location = font_date = ImageFont.load_default()

            # 1. Draw border frame (sides and bottom only)
            border_width = 20
            # Left border
            draw.rectangle([0, 0, border_width, height], fill=border_color)
            # Right border
            draw.rectangle([width-border_width, 0, width, height], fill=border_color)
            # Bottom border
            draw.rectangle([0, height-border_width, width, height], fill=border_color)

            # 2. Draw red header block at top (rounded top corners)
            header_height = 300
            header_y = 20

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

                # Rounded location box
                loc_width = 300
                loc_height = 62

                # Draw gradient background (approximation)
                loc_bg = (163, 42, 13, 255)  # #a32a0d
                draw.ellipse([loc_x, loc_y, loc_x+60, loc_y+loc_height], fill=loc_bg)
                draw.ellipse([loc_x+loc_width-60, loc_y, loc_x+loc_width, loc_y+loc_height], fill=loc_bg)
                draw.rectangle([loc_x+30, loc_y, loc_x+loc_width-30, loc_y+loc_height], fill=loc_bg)

                # White border
                draw.ellipse([loc_x-1, loc_y-1, loc_x+61, loc_y+loc_height+1], outline=(255, 255, 255, 255), width=2)
                draw.ellipse([loc_x+loc_width-61, loc_y-1, loc_x+loc_width+1, loc_y+loc_height+1], outline=(255, 255, 255, 255), width=2)

                # Location text
                loc_text = f"📍 {location}"
                draw.text((loc_x+150, loc_y+31), loc_text,
                         fill=(255, 255, 255, 255), font=font_location, anchor="mm")

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
'''

# Read the file
with open('app/services/simple_overlay_renderer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find Template 4 function
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'def create_template4_overlay(' in line:
        start_line = i - 1  # Include @staticmethod
    elif start_line is not None and ('@staticmethod' in line or 'def _wrap_text' in line):
        end_line = i
        break

if start_line is None or end_line is None:
    print("Could not find Template 4 function!")
    exit(1)

# Replace the function
new_lines = lines[:start_line] + [new_template4_code + '\n'] + lines[end_line:]

# Write back
with open('app/services/simple_overlay_renderer.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS: Template 4 updated to match new HTML design!")
print("The Pillow renderer now matches your HTML template.")
print("Try rendering again - no restart needed with --reload!")
