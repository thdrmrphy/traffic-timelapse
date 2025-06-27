# Traffic Timelapse

A Python script to download NSW traffic camera images at regular intervals for creating timelapses.

## Features

- Download images from multiple NSW traffic cameras
- Configurable download intervals
- Automatic image validation (ensures actual images, not error pages)
- Timestamped filenames for easy chronological sorting
- Browser-like headers to avoid being blocked

## Available Cameras

- **anzac-bridge** - Anzac Bridge Looking East
- **railway-square** - George St Railway Square  
- **william-street** - William Street East Sydney
- **anzac-parade** - Anzac Parade Kensington

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic usage (default: Anzac Bridge, 20-second intervals):
```bash
python download.py
```

### Choose a specific camera:
```bash
python download.py --camera railway-square
```

### Set custom interval (in seconds):
```bash
python download.py --camera william-street --interval 30
```

### List available cameras:
```bash
python download.py --list-cameras
```

### Command line options:
- `--camera, -c`: Choose camera (anzac-bridge, railway-square, william-street, anzac-parade)
- `--interval, -i`: Download interval in seconds (default: 20)
- `--list-cameras, -l`: List available cameras and exit
- `--help, -h`: Show help message

## Output

Images are saved in the `images/` directory with filenames like:
- `anzac_bridge_looking_east_20250627_100315.jpeg`
- `george_st_railway_square_20250627_100325.jpeg`

The timestamp format is: `YYYYMMDD_HHMMSS`

## Stopping

Press `Ctrl+C` to stop the download process.

## Creating Timelapses

Once you have collected enough images, you can use the included `timelapse.py` script to create videos:

### Basic usage:
```bash
python timelapse.py --camera anzac-bridge
```

### Advanced options:
```bash
# Custom framerate and quality
python timelapse.py --camera railway-square --framerate 60 --quality highest

# Create timelapse for specific date range
python timelapse.py --camera william-street --start-date 2025-06-27 --end-date 2025-06-28

# List available cameras and image counts
python timelapse.py --list-cameras

# List images for a specific camera
python timelapse.py --camera anzac-bridge --list-images
```

### Timelapse options:
- `--camera, -c`: Choose camera (required)
- `--framerate, -f`: Video framerate in fps (default: 30)
- `--quality, -q`: Output quality (low, medium, high, highest - default: high)
- `--start-date`: Start date filter (YYYY-MM-DD format)
- `--end-date`: End date filter (YYYY-MM-DD format)
- `--list-cameras, -l`: List available cameras and image counts
- `--list-images`: List available images for specified camera

Videos are saved in the `timelapses/` directory with descriptive filenames.

### Requirements for timelapse creation:
- **FFmpeg** must be installed:
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: Download from https://ffmpeg.org/download.html

### Alternative (Manual FFmpeg):
You can also create timelapses manually with FFmpeg:

```bash
ffmpeg -framerate 30 -pattern_type glob -i 'images/camera_name_*.jpeg' -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```