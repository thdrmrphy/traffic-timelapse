import os
import glob
import argparse
import subprocess
import sys
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
CAMERAS_DATA = load_cameras()

IMAGES_DIR = "images"
OUTPUT_DIR = "timelapses"

def check_ffmpeg():
    """Check if FFmpeg is installed and available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_output_directory():
    """Create the output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

def find_camera_images(camera_key, start_date=None, end_date=None):
    """Find all images for a specific camera, optionally filtered by date range"""
    # Use the camera key directly as the filename prefix (matches download.py behavior)
    pattern = os.path.join(IMAGES_DIR, f"{camera_key}_*.jpeg")
    image_files = glob.glob(pattern)
    
    if not image_files:
        return []
    
    # Filter by date range if specified
    if start_date or end_date:
        filtered_files = []
        for img_file in image_files:
            # Extract timestamp from filename
            basename = os.path.basename(img_file)
            try:
                # Format: camera_key_YYYYMMDD_HHMMSS.jpeg
                timestamp_part = basename.split('_')[-2] + '_' + basename.split('_')[-1].replace('.jpeg', '')
                img_datetime = datetime.strptime(timestamp_part, '%Y%m%d_%H%M%S')
                
                if start_date and img_datetime < start_date:
                    continue
                if end_date and img_datetime > end_date:
                    continue
                    
                filtered_files.append(img_file)
            except (ValueError, IndexError):
                # Skip files that don't match expected format
                continue
        
        image_files = filtered_files
    
    # Sort by filename (which includes timestamp)
    image_files.sort()
    return image_files

def create_timelapse(camera_key, framerate=30, output_quality='high', start_date=None, end_date=None):
    """Create a timelapse video from camera images"""
    if camera_key not in CAMERAS_DATA:
        print(f"Error: Unknown camera '{camera_key}'")
        return False
    
    camera = CAMERAS_DATA[camera_key]
    
    # Find images for this camera using the camera key directly
    image_files = find_camera_images(camera_key, start_date, end_date)
    
    if not image_files:
        print(f"No images found for camera '{camera_key}' ({camera['name']})")
        print(f"Looking for pattern: {camera_key}_*.jpeg in {IMAGES_DIR}/")
        return False
    
    print(f"Found {len(image_files)} images for {camera['name']}")
    
    # Create output directory
    create_output_directory()
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_suffix = ""
    if start_date or end_date:
        if start_date and end_date:
            date_suffix = f"_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}"
        elif start_date:
            date_suffix = f"_from_{start_date.strftime('%Y%m%d')}"
        elif end_date:
            date_suffix = f"_until_{end_date.strftime('%Y%m%d')}"
    
    output_filename = f"{camera_key}_timelapse{date_suffix}_{timestamp}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Set quality parameters
    quality_settings = {
        'low': ['-crf', '28'],
        'medium': ['-crf', '23'],
        'high': ['-crf', '18'],
        'highest': ['-crf', '15']
    }
    
    # Build FFmpeg command
    input_pattern = os.path.join(IMAGES_DIR, f"{camera_key}_*.jpeg")
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file
        '-framerate', str(framerate),
        '-pattern_type', 'glob',
        '-i', input_pattern,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        *quality_settings.get(output_quality, quality_settings['high']),
        '-movflags', '+faststart',  # Enable streaming
        output_path
    ]
    
    print("Creating timelapse video...")
    print(f"Framerate: {framerate} fps")
    print(f"Quality: {output_quality}")
    print(f"Output: {output_path}")
    print("-" * 50)
    
    try:
        # Run FFmpeg
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Timelapse created successfully: {output_path}")
            
            # Get file size
            file_size = os.path.getsize(output_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f"File size: {file_size_mb:.1f} MB")
            
            return True
        else:
            print("❌ FFmpeg error:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Error running FFmpeg: {e}")
        return False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Create timelapse videos from downloaded traffic camera images')
    
    parser.add_argument('--camera', '-c',
                       choices=list(CAMERAS_DATA.keys()),
                       help='Camera to create timelapse from')
    
    parser.add_argument('--framerate', '-f',
                       type=int,
                       default=30,
                       help='Video framerate (default: 30 fps)')
    
    parser.add_argument('--quality', '-q',
                       choices=['low', 'medium', 'high', 'highest'],
                       default='high',
                       help='Output quality (default: high)')
    
    parser.add_argument('--start-date',
                       type=str,
                       help='Start date (YYYY-MM-DD format)')
    
    parser.add_argument('--end-date',
                       type=str,
                       help='End date (YYYY-MM-DD format)')
    
    parser.add_argument('--list-cameras', '-l',
                       action='store_true',
                       help='List available cameras and exit')
    
    parser.add_argument('--list-images',
                       action='store_true',
                       help='List available images for the specified camera')
    
    args = parser.parse_args()
    
    # Check if camera is required
    if not args.list_cameras and not args.camera:
        parser.error("--camera/-c is required unless using --list-cameras")
    
    return args

def list_available_cameras():
    """List all available cameras"""
    print("Available cameras:")
    print("-" * 50)
    for key, camera in CAMERAS_DATA.items():
        # Count images for each camera using the camera key directly
        image_count = len(find_camera_images(key))
        print(f"  {key:25} - {camera['name']} ({image_count} images)")
    print()

def list_camera_images(camera_key):
    """List images for a specific camera"""
    if camera_key not in CAMERAS_DATA:
        print(f"Error: Unknown camera '{camera_key}'")
        return
    
    camera = CAMERAS_DATA[camera_key]
    image_files = find_camera_images(camera_key)
    
    if not image_files:
        print(f"No images found for camera '{camera_key}' ({camera['name']})")
        return
    
    print(f"Images for {camera['name']} ({len(image_files)} total):")
    print("-" * 70)
    
    for img_file in image_files:
        basename = os.path.basename(img_file)
        file_size = os.path.getsize(img_file)
        file_size_kb = file_size / 1024
        
        # Extract timestamp from filename
        try:
            timestamp_part = basename.split('_')[-2] + '_' + basename.split('_')[-1].replace('.jpeg', '')
            img_datetime = datetime.strptime(timestamp_part, '%Y%m%d_%H%M%S')
            formatted_time = img_datetime.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, IndexError):
            formatted_time = "Unknown"
        
        print(f"  {basename:50} {formatted_time} ({file_size_kb:6.1f} KB)")

def main():
    """Main function"""
    args = parse_arguments()
    
    # Check if FFmpeg is available
    if not check_ffmpeg():
        print("❌ Error: FFmpeg is not installed or not available in PATH")
        print("Please install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)
    
    # List cameras and exit if requested
    if args.list_cameras:
        list_available_cameras()
        return
    
    # List images for camera if requested
    if args.list_images:
        list_camera_images(args.camera)
        return
    
    # Parse date arguments
    start_date = None
    end_date = None
    
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid start date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
            # Set to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            print("Error: Invalid end date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Create timelapse
    success = create_timelapse(
        args.camera,
        framerate=args.framerate,
        output_quality=args.quality,
        start_date=start_date,
        end_date=end_date
    )
    
    if success:
        print("\n🎬 Timelapse creation completed!")
    else:
        print("\n❌ Timelapse creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
