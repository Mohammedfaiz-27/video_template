"""Test video upload to Gemini."""
import google.generativeai as genai
from app.config import settings
from pathlib import Path

# Configure API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Test file
test_file = r"F:\newsit\video template\backend\storage\uploads\be7033a6-22c4-4e91-9192-2e78ee743678.mp4"

if not Path(test_file).exists():
    print(f"ERROR: Test file not found: {test_file}")
    print("Please update the path to an existing video file")
else:
    print(f"Testing upload of: {test_file}")
    print(f"File size: {Path(test_file).stat().st_size / (1024*1024):.2f} MB")

    try:
        # Test if upload_file exists
        print(f"\nChecking if upload_file exists...")
        print(f"Type: {type(genai.upload_file)}")
        print(f"Callable: {callable(genai.upload_file)}")

        # Try to upload
        print(f"\nAttempting upload...")
        video_file = genai.upload_file(path=test_file)
        print(f"SUCCESS! Uploaded: {video_file.name}")
        print(f"State: {video_file.state.name}")

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
