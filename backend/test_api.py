"""
API Testing Script for Video Template Generator
Run this after the server is started to test all endpoints.
"""

import requests
import time
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/videos"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def test_health_check():
    """Test health check endpoint."""
    print_header("Test 1: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()

        print_success(f"Health check passed")
        print_info(f"Status: {data.get('status')}")
        print_info(f"Database: {data.get('database')}")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint."""
    print_header("Test 2: Root Endpoint")

    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        data = response.json()

        print_success("Root endpoint working")
        print_info(f"API Name: {data.get('name')}")
        print_info(f"Version: {data.get('version')}")
        print_info(f"Status: {data.get('status')}")
        return True
    except Exception as e:
        print_error(f"Root endpoint failed: {e}")
        return False

def test_video_upload():
    """Test video upload endpoint."""
    print_header("Test 3: Video Upload")

    # Check if sample video exists
    sample_video = Path("sample_video.mp4")

    if not sample_video.exists():
        print_warning("No sample video found")
        print_info("To test upload, place a video file named 'sample_video.mp4' in the backend folder")
        return None

    try:
        print_info(f"Uploading {sample_video.name} ({sample_video.stat().st_size / (1024*1024):.1f} MB)...")

        with open(sample_video, 'rb') as f:
            files = {'file': (sample_video.name, f, 'video/mp4')}
            response = requests.post(f"{API_URL}/upload", files=files)

        response.raise_for_status()
        data = response.json()

        video_id = data.get('video_id')
        print_success(f"Video uploaded successfully")
        print_info(f"Video ID: {video_id}")
        print_info(f"Status: {data.get('status')}")

        return video_id
    except Exception as e:
        print_error(f"Upload failed: {e}")
        return None

def test_video_status(video_id):
    """Test video status endpoint."""
    print_header("Test 4: Video Status")

    if not video_id:
        print_warning("Skipping - no video ID")
        return False

    try:
        response = requests.get(f"{API_URL}/{video_id}/status")
        response.raise_for_status()
        data = response.json()

        print_success("Status check successful")
        print_info(f"Status: {data.get('status')}")
        print_info(f"Stage: {data.get('stage')}")
        print_info(f"Progress: {data.get('progress_percent')}%")
        return True
    except Exception as e:
        print_error(f"Status check failed: {e}")
        return False

def test_video_analysis(video_id):
    """Test video analysis trigger."""
    print_header("Test 5: Video Analysis")

    if not video_id:
        print_warning("Skipping - no video ID")
        return False

    try:
        # Trigger analysis
        response = requests.post(f"{API_URL}/{video_id}/analyze")
        response.raise_for_status()
        data = response.json()

        print_success("Analysis triggered")
        print_info(f"Message: {data.get('message')}")

        # Poll for completion
        print_info("Waiting for analysis to complete...")
        max_wait = 180  # 3 minutes
        start_time = time.time()

        while time.time() - start_time < max_wait:
            time.sleep(5)

            status_response = requests.get(f"{API_URL}/{video_id}/status")
            status_data = status_response.json()
            current_status = status_data.get('status')
            progress = status_data.get('progress_percent', 0)

            print_info(f"Status: {current_status} ({progress}%)")

            if current_status == 'analyzed':
                print_success("Analysis completed!")
                return True
            elif current_status == 'error':
                print_error("Analysis failed")
                print_error(f"Error: {status_data.get('error')}")
                return False

        print_warning("Analysis timed out")
        return False

    except Exception as e:
        print_error(f"Analysis failed: {e}")
        return False

def test_get_analysis(video_id):
    """Test get analysis results."""
    print_header("Test 6: Get Analysis Results")

    if not video_id:
        print_warning("Skipping - no video ID")
        return False

    try:
        response = requests.get(f"{API_URL}/{video_id}/analysis")
        response.raise_for_status()
        data = response.json()

        print_success("Analysis results retrieved")

        # Display transcript
        if data.get('transcript'):
            transcript = data['transcript']
            print_info(f"Transcript ({transcript.get('language')}):")
            print(f"  {transcript.get('text', '')[:100]}...")

        # Display headline
        if data.get('headline'):
            headline = data['headline']
            print_info(f"Headline: {headline.get('primary')}")
            print_info(f"Alternatives: {', '.join(headline.get('alternatives', [])[:2])}")

        # Display location
        if data.get('location') and data['location'].get('text'):
            location = data['location']
            print_info(f"Location: {location.get('text')} (confidence: {location.get('confidence', 0):.2f})")

        return True

    except Exception as e:
        print_error(f"Failed to get analysis: {e}")
        return False

def test_video_rendering(video_id):
    """Test video rendering."""
    print_header("Test 7: Video Rendering")

    if not video_id:
        print_warning("Skipping - no video ID")
        return False

    try:
        # Trigger rendering
        render_data = {
            "show_location": True
        }
        response = requests.post(f"{API_URL}/{video_id}/render", json=render_data)
        response.raise_for_status()
        data = response.json()

        print_success("Rendering triggered")
        print_info(f"Message: {data.get('message')}")

        # Poll for completion
        print_info("Waiting for rendering to complete...")
        max_wait = 300  # 5 minutes
        start_time = time.time()

        while time.time() - start_time < max_wait:
            time.sleep(5)

            status_response = requests.get(f"{API_URL}/{video_id}/status")
            status_data = status_response.json()
            current_status = status_data.get('status')
            progress = status_data.get('progress_percent', 0)

            print_info(f"Status: {current_status} ({progress}%)")

            if current_status == 'completed':
                print_success("Rendering completed!")
                return True
            elif current_status == 'error':
                print_error("Rendering failed")
                print_error(f"Error: {status_data.get('error')}")
                return False

        print_warning("Rendering timed out")
        return False

    except Exception as e:
        print_error(f"Rendering failed: {e}")
        return False

def test_download(video_id):
    """Test video download."""
    print_header("Test 8: Video Download")

    if not video_id:
        print_warning("Skipping - no video ID")
        return False

    try:
        response = requests.get(f"{API_URL}/{video_id}/download", stream=True)
        response.raise_for_status()

        # Save to file
        output_file = f"test_output_{video_id}.mp4"
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = Path(output_file).stat().st_size / (1024 * 1024)
        print_success(f"Video downloaded successfully")
        print_info(f"Saved to: {output_file}")
        print_info(f"File size: {file_size:.1f} MB")
        return True

    except Exception as e:
        print_error(f"Download failed: {e}")
        return False

def main():
    """Run all tests."""
    print_header("Video Template Generator - API Test Suite")
    print_info("Testing backend API endpoints...")

    # Basic connectivity tests
    if not test_health_check():
        print_error("Server not responding. Please ensure the backend is running.")
        return

    test_root_endpoint()

    # Upload and processing tests
    video_id = test_video_upload()

    if video_id:
        test_video_status(video_id)

        # Ask user if they want to run full analysis (costs API credits)
        print("\n" + "="*60)
        response = input("Run AI analysis and rendering? This will use API credits (y/n): ")
        if response.lower() == 'y':
            if test_video_analysis(video_id):
                test_get_analysis(video_id)
                if test_video_rendering(video_id):
                    test_download(video_id)
        else:
            print_info("Skipping AI analysis and rendering")

    print_header("Test Suite Complete")
    print_info("Check the results above for any errors")

if __name__ == "__main__":
    main()
