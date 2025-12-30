"""Test script for Template 4 HTML rendering."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.video_processor import VideoProcessor

def test_template4():
    """Test Template 4 with HTML rendering."""

    print("=" * 60)
    print("Testing Template 4 (Tiruvarur Updates) with HTML")
    print("=" * 60)

    # Paths
    input_path = "F:/newsit/video template/backend/storage/uploads/bca54bc3-710c-43fc-b8b1-a5475b82b142.mp4"
    output_path = "F:/newsit/video template/backend/storage/test_template4_output.mp4"

    # Test data
    headline = "Thick Smoke Spreads as Fire Breaks Out"
    location = "Tiruvarur, Tamil Nadu"
    show_location = True

    print(f"\n📹 Input: {Path(input_path).name}")
    print(f"📝 Headline: {headline}")
    print(f"📍 Location: {location}")
    print(f"🎨 Template: template4 (HTML-based)")
    print("\n" + "-" * 60)

    # Test HTML template rendering
    print("\n🎬 Processing video with HTML Template 4...")
    success = VideoProcessor.process_with_html_template(
        input_path=input_path,
        output_path=output_path,
        template_name="template4.html",
        headline=headline,
        location=location,
        show_location=show_location
    )

    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Template 4 rendering completed!")
        print("=" * 60)
        print(f"\n📦 Output file: {output_path}")

        # Check file size
        if Path(output_path).exists():
            size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"📊 File size: {size_mb:.2f} MB")
            print("\n🎥 You can now play the video to see the result!")

        return True
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED! Template 4 rendering failed!")
        print("=" * 60)
        print("\n⚠️  Check the error messages above for details.")
        return False

if __name__ == "__main__":
    test_template4()
