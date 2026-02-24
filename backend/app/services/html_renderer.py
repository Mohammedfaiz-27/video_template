"""HTML Template Renderer Service using html2image."""

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import tempfile
import os
import base64


class HTMLRenderer:
    """Render HTML templates to images for video overlays."""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent.parent / 'templates'

    def render_template_to_image(
        self,
        template_name: str,
        output_path: str,
        data: Dict[str, str],
        width: int = 1080,
        height: int = 1920
    ) -> bool:
        """
        Render HTML template to PNG image.

        Args:
            template_name: Name of template file (e.g., 'template1.html')
            output_path: Where to save the PNG
            data: Template data (headline, location, date, etc.)
            width: Output image width
            height: Output image height

        Returns:
            True if successful
        """
        try:
            from html2image import Html2Image

            # Load template file
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                print(f"❌ Template not found: {template_path}")
                return False

            # Read template HTML
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Replace placeholders with actual data
            html_content = self._inject_data(html_content, data)

            # Initialize html2image with font rendering support
            hti = Html2Image(
                output_path=str(Path(output_path).parent),
                size=(width, height),
                custom_flags=[
                    '--font-render-hinting=none',
                    '--disable-font-subpixel-positioning',
                    '--force-device-scale-factor=1',
                    '--hide-scrollbars',
                    '--allow-file-access-from-files',  # Allow loading local fonts
                    '--disable-web-security'  # Allow cross-origin font loading
                ]
            )

            # Render HTML to image
            output_file = Path(output_path).name
            hti.screenshot(
                html_str=html_content,
                save_as=output_file,
                size=(width, height)
            )

            print(f"✅ Rendered template to: {output_file}")
            return True

        except ImportError:
            print("❌ html2image not installed. Install with: pip install html2image")
            return False
        except Exception as e:
            print(f"❌ HTML rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _inject_data(self, html_content: str, data: Dict[str, str]) -> str:
        """
        Replace placeholders in HTML with actual data.

        Placeholders:
            {{headline}} - News headline
            {{location}} - Location text
            {{date}} - Current date
            {{video_placeholder}} - Video area marker
        """
        # Get current date
        current_date = datetime.now().strftime("%d %B %Y")

        # Replace all placeholders
        replacements = {
            '{{headline}}': data.get('headline', 'Breaking News'),
            '{{location}}': data.get('location', ''),
            '{{date}}': current_date,
            '{{show_location}}': 'block' if data.get('show_location', True) else 'none'
        }

        for placeholder, value in replacements.items():
            html_content = html_content.replace(placeholder, str(value))

        # Embed fonts as base64 data URIs so Chrome headless can load them
        fonts_dir = self.templates_dir.parent / 'assets' / 'fonts'
        for font_file in fonts_dir.glob('*.ttf'):
            relative_url = f"url('../assets/fonts/{font_file.name}')"
            try:
                font_data = font_file.read_bytes()
                b64 = base64.b64encode(font_data).decode('ascii')
                data_uri = f"url('data:font/truetype;base64,{b64}')"
                html_content = html_content.replace(relative_url, data_uri)
                print(f"   ✓ Embedded font: {font_file.name}")
            except Exception as e:
                print(f"   ⚠️ Could not embed font {font_file.name}: {e}")

        # Also embed logo as base64
        assets_dir = self.templates_dir.parent / 'assets'
        for img_ext in ['png', 'jpg', 'jpeg']:
            for img_file in assets_dir.glob(f'*.{img_ext}'):
                relative_src = f'../assets/{img_file.name}'
                try:
                    img_data = img_file.read_bytes()
                    b64 = base64.b64encode(img_data).decode('ascii')
                    mime = 'image/png' if img_ext == 'png' else 'image/jpeg'
                    data_uri = f'data:{mime};base64,{b64}'
                    html_content = html_content.replace(relative_src, data_uri)
                    print(f"   ✓ Embedded image: {img_file.name}")
                except Exception:
                    pass

        return html_content


# Synchronous wrapper (html2image is already synchronous, but keeping for compatibility)
class HTMLRendererSync:
    """Synchronous wrapper for HTMLRenderer."""

    @staticmethod
    def render_template(
        template_name: str,
        output_path: str,
        data: Dict[str, str],
        width: int = 1080,
        height: int = 1920
    ) -> bool:
        """Render template synchronously."""
        renderer = HTMLRenderer()
        return renderer.render_template_to_image(
            template_name, output_path, data, width, height
        )
