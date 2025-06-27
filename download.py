import requests
import time
import os
import argparse
import json
from datetime import datetime
import threading

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

def download_image(camera_slug, camera_url, camera_name):
    """Download the traffic camera image and save it with a timestamp"""
    try:
        # Get current timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create filename based on camera slug (more reliable than processing name)
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
            print(f"[{camera_slug}] Error: Received HTML page instead of image. Camera may be unavailable.")
            print(f"[{camera_slug}] Content preview: {response.text[:200]}...")
            return False
        
        # Additional check: see if content starts with HTML
        if response.content.startswith(b'<html') or response.content.startswith(b'<!DOCTYPE'):
            print(f"[{camera_slug}] Error: Received HTML content instead of image data.")
            return False
        
        # Check if content looks like an image (JPEG files start with specific bytes)
        if not response.content.startswith(b'\xff\xd8\xff'):
            print(f"[{camera_slug}] Warning: Content doesn't appear to be a JPEG image.")
            print(f"[{camera_slug}] Content preview: {response.content[:50]}")
            return False
        
        # Save the image
        with open(filepath, 'wb') as file:
            file.write(response.content)
        
        print(f"[{camera_slug}] Downloaded: {filename} (Size: {len(response.content)} bytes)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"[{camera_slug}] Error downloading image: {e}")
        return False
    except Exception as e:
        print(f"[{camera_slug}] Unexpected error: {e}")
        return False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Download traffic camera images for timelapse creation')
    parser.add_argument('--camera', '-c', 
                       nargs='+',  # Allow multiple values
                       choices=list(CAMERAS.keys()), 
                       default=['anzacbr'],
                       help='Camera(s) to download from. Can specify multiple cameras (default: anzacbr)')
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

class CameraDownloader:
    """Class to handle downloading from a single camera in a separate thread"""
    
    def __init__(self, camera_slug, camera_data, interval):
        self.camera_slug = camera_slug
        self.camera_url = camera_data['url']
        self.camera_name = camera_data['name']
        self.interval = interval
        self.download_count = 0
        self.running = True
        self.lock = threading.Lock()
    
    def run(self):
        """Main download loop for this camera"""
        print(f"[{self.camera_slug}] Starting download from {self.camera_name}")
        
        while self.running:
            if download_image(self.camera_slug, self.camera_url, self.camera_name):
                with self.lock:
                    self.download_count += 1
                    print(f"[{self.camera_slug}] Total images downloaded: {self.download_count}")
            
            # Wait for specified interval before next download
            time.sleep(self.interval)
    
    def stop(self):
        """Stop the download loop"""
        self.running = False

def main():
    """Main function to run the image downloading loop"""
    args = parse_arguments()
    
    # List cameras and exit if requested
    if args.list_cameras:
        list_available_cameras()
        return
    
    # Get selected cameras
    selected_cameras = args.camera
    
    print("Traffic Camera Image Downloader")
    print(f"Cameras: {', '.join([CAMERAS[cam]['name'] for cam in selected_cameras])}")
    print(f"Camera slugs: {', '.join(selected_cameras)}")
    print(f"Interval: {args.interval} seconds")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    # Create images directory
    create_images_directory()
    
    # Create camera downloaders
    downloaders = []
    threads = []
    
    for camera_slug in selected_cameras:
        camera_data = CAMERAS[camera_slug]
        downloader = CameraDownloader(camera_slug, camera_data, args.interval)
        downloaders.append(downloader)
        
        # Create and start thread for this camera
        thread = threading.Thread(target=downloader.run, daemon=True)
        threads.append(thread)
        thread.start()
    
    try:
        # Wait for all threads and show periodic status
        while True:
            time.sleep(10)  # Show status every 10 seconds
            total_downloads = sum(d.download_count for d in downloaders)
            print(f"Status: Total downloads across all cameras: {total_downloads}")
            
            # Check if any threads died unexpectedly
            alive_threads = [t for t in threads if t.is_alive()]
            if len(alive_threads) < len(threads):
                print("Warning: Some camera threads have stopped!")
                break
            
    except KeyboardInterrupt:
        print("\nStopping all cameras...")
        
        # Stop all downloaders
        for downloader in downloaders:
            downloader.stop()
        
        # Wait for threads to finish (with timeout)
        for thread in threads:
            thread.join(timeout=2)
        
        # Show final statistics
        print("\nFinal Statistics:")
        total_downloads = 0
        for downloader in downloaders:
            print(f"  {downloader.camera_slug}: {downloader.download_count} images")
            total_downloads += downloader.download_count
        print(f"Total images downloaded: {total_downloads}")
        
    except Exception as e:
        print(f"Unexpected error in main loop: {e}")
        # Stop all downloaders
        for downloader in downloaders:
            downloader.stop()

if __name__ == "__main__":
    main()