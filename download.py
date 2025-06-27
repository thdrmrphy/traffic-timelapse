import requests
import time
import os
import argparse
import json
from datetime import datetime

def load_cameras():
    """Load camera configurations from cameras.json"""
    try:
        with open('cameras.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: cameras.json file not found!")
        print("Please ensure cameras.json is in the same directory as this script.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in cameras.json: {e}")
        exit(1)

# Load available traffic cameras from JSON file
CAMERAS = load_cameras()

# Directory to save images
IMAGES_DIR = "images"

def create_images_directory():
    """Create the images directory if it doesn't exist"""
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        print(f"Created directory: {IMAGES_DIR}")

def download_image(camera_url, camera_name):
    """Download the traffic camera image and save it with a timestamp"""
    try:
        # Get current timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create filename based on camera name
        camera_slug = camera_name.lower().replace(' ', '_').replace('/', '_')
        filename = f"{camera_slug}_{timestamp}.jpeg"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Download the image
        response = requests.get(camera_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Check if we actually got an image (not HTML error page)
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            print("Error: Received HTML page instead of image. Camera may be unavailable.")
            print(f"Content preview: {response.text[:200]}...")
            return False
        
        # Additional check: see if content starts with HTML
        if response.content.startswith(b'<html') or response.content.startswith(b'<!DOCTYPE'):
            print("Error: Received HTML content instead of image data.")
            return False
        
        # Check if content looks like an image (JPEG files start with specific bytes)
        if not response.content.startswith(b'\xff\xd8\xff'):
            print("Warning: Content doesn't appear to be a JPEG image.")
            print(f"Content preview: {response.content[:50]}")
            return False
        
        # Save the image
        with open(filepath, 'wb') as file:
            file.write(response.content)
        
        print(f"Downloaded: {filename} (Size: {len(response.content)} bytes)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Download traffic camera images for timelapse creation')
    parser.add_argument('--camera', '-c', 
                       choices=list(CAMERAS.keys()), 
                       default='anzacbr',
                       help='Camera to download from (default: anzacbr)')
    parser.add_argument('--interval', '-i', 
                       type=int, 
                       default=20,
                       help='Download interval in seconds (default: 20)')
    parser.add_argument('--list-cameras', '-l', 
                       action='store_true',
                       help='List available cameras and exit')
    
    return parser.parse_args()

def list_available_cameras():
    """List all available cameras"""
    print("Available cameras:")
    print("-" * 50)
    for key, camera in CAMERAS.items():
        print(f"  {key:15} - {camera['name']}")
    print()

def main():
    """Main function to run the image downloading loop"""
    args = parse_arguments()
    
    # List cameras and exit if requested
    if args.list_cameras:
        list_available_cameras()
        return
    
    # Get selected camera
    camera = CAMERAS[args.camera]
    camera_url = camera['url']
    camera_name = camera['name']
    
    print("Traffic Camera Image Downloader")
    print(f"Camera: {camera_name}")
    print(f"Downloading from: {camera_url}")
    print(f"Interval: {args.interval} seconds")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    # Create images directory
    create_images_directory()
    
    download_count = 0
    
    try:
        while True:
            if download_image(camera_url, camera_name):
                download_count += 1
                print(f"Total images downloaded: {download_count}")
            
            # Wait for specified interval before next download
            print(f"Waiting {args.interval} seconds...")
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print(f"\nStopped by user. Total images downloaded: {download_count}")
    except Exception as e:
        print(f"Unexpected error in main loop: {e}")

if __name__ == "__main__":
    main()