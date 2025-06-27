# Traffic Timelapse

A Python script to download NSW traffic camera images at regular intervals for creating timelapses.

## Features

- Download images from multiple NSW traffic cameras
- **Support for simultaneous downloads from multiple cameras**
- Configurable download intervals
- Automatic image validation (ensures actual images, not error pages)
- Timestamped filenames for easy chronological sorting
- Browser-like headers to avoid being blocked
- Thread-safe concurrent downloads with individual camera progress tracking

## Available Cameras

The system supports 113 NSW traffic cameras. Use the camera slug (shown in bold) with the `--camera` parameter. You can also use `--list-cameras` to see all available options with image counts.

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
python download.py --camera georgest
```

### Download from multiple cameras simultaneously:
```bash
python download.py --camera anzacbr georgest harbourbridge --interval 30
```

### Set custom interval (in seconds):
```bash
python download.py --camera williamst --interval 30
```

### List available cameras:
```bash
python download.py --list-cameras
```

## Multi-Camera Downloads

The system supports downloading from multiple cameras simultaneously using threading. Each camera runs in its own thread with individual progress tracking:

### Download from multiple specific cameras:
```bash
# Download from 3 cameras at once
python download.py --camera anzacbr georgest harbourbridge

# Download from both directions of Anzac Bridge
python download.py --camera anzacbr anzacbr-westbound

# Download from all three Anzac Bridge cameras for comprehensive coverage
python download.py --camera anzacbr anzacbr-westbound anzacbr-westtower

# Download from multiple highway cameras
python download.py --camera m4-auburn m5-liverpool f3-kariong --interval 15
```

### Benefits of multi-camera mode:
- **Concurrent downloads**: All cameras download simultaneously, not sequentially
- **Individual tracking**: Each camera shows its own download count and status
- **Shared interval**: All cameras use the same download interval
- **Separate image files**: Each camera saves images with its own naming convention

### Output format for multi-camera:
When downloading from multiple cameras, the console output includes camera identifiers:
```
[anzacbr] Downloaded: anzacbr_20250627_141547.jpeg (Size: 108139 bytes)
[georgest] Downloaded: georgest_20250627_141547.jpeg (Size: 112495 bytes)
[anzacbr] Total images downloaded: 1
[georgest] Total images downloaded: 1
Status: Total downloads across all cameras: 2
```

### Command line options:
- `--camera, -c`: Choose camera(s) (use --list-cameras to see all available options). Can specify multiple cameras for simultaneous downloading
- `--interval, -i`: Download interval in seconds (default: 20)
- `--list-cameras, -l`: List available cameras and exit
- `--help, -h`: Show help message

## Output

Images are saved in the `images/` directory with filenames like:
- `anzacbr_20250627_100315.jpeg` (single camera or multi-camera mode)
- `georgest_20250627_100325.jpeg`
- `harbourbridge_20250627_100330.jpeg`

The timestamp format is: `YYYYMMDD_HHMMSS`

When using multiple cameras, each camera creates its own files with its camera slug as the prefix, making it easy to sort and organize images by camera source.

## Stopping

Press `Ctrl+C` to stop the download process.

## Creating Timelapses

Once you have collected enough images, you can use the included `timelapse.py` script to create videos:

### Basic usage:
```bash
python timelapse.py --camera anzacbr
```

### Advanced options:
```bash
# Custom framerate and quality
python timelapse.py --camera georgest --framerate 60 --quality highest

# Create timelapse for specific date range
python timelapse.py --camera williamst --start-date 2025-06-27 --end-date 2025-06-28

# List available cameras and image counts
python timelapse.py --list-cameras

# List images for a specific camera
python timelapse.py --camera anzacbr --list-images
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

## Complete Camera List

All 113 available NSW traffic cameras (use the slug in bold with `--camera`):

- **5ways** - Five Ways Junction
- **alfords-bangorbp** - Alfords Point Bridge
- **alisonrd-randwick** - Alison Road, Randwick
- **anzacbr** - Anzac Bridge
- **anzacbr-westbound** - Anzac Bridge, Westbound
- **anzacbr-westtower** - Anzac Bridge, West Tower Looking East
- **anzacpde** - Anzac Parade
- **audleyrd-audley** - Audley Road, Audley
- **beecroftrd-epping** - Beecroft Road, Epping
- **burntbrdg-seaforth** - Burnt Bridge, Seaforth
- **churchst-parra** - Church Street, Parramatta
- **citywestlink** - City West Link
- **cumberlandhwy-carlingford** - Cumberland Highway, Carlingford
- **cumberlandhwy-merrylands** - Cumberland Highway, Merrylands
- **easterndist** - Eastern Distributor
- **elizabethdr-livepool** - Elizabeth Drive, Liverpool
- **eppingrd-lanecove** - Epping Road, Lane Cove
- **eppingrd-macquariepark** - Epping Road, Macquarie Park
- **f3-johnrenshawdr** - M1 Pacific Motorway, John Renshaw Drive
- **f3-kariong** - M1 Pacific Motorway, Kariong
- **f3-mooney** - M1 Pacific Motorway, Mooney Mooney
- **f3-mountwhite** - M1 Pacific Motorway, Mount White
- **f3-ourimbah** - M1 Pacific Motorway, Ourimbah
- **f3-sparkesrd** - M1 Pacific Motorway, Sparkes Road
- **f3-wahroonga** - M1 Pacific Motorway, Wahroonga
- **f3-windybanks** - M1 Pacific Motorway, Windy Banks
- **f6-mtousley** - F6 Grand Pacific Drive, Mount Ousley
- **f6-waterfall** - F6 Grand Pacific Drive, Waterfall
- **falconst-crowsnest** - Falcon Street, Crows Nest
- **fiveislands-portkembla** - Five Islands Road, Port Kembla
- **foreshore-banksmeadow** - Foreshore Road, Banksmeadow
- **georgest** - George Street
- **ghd-airport** - General Holmes Drive, Airport
- **gladesvillebr** - Gladesville Bridge
- **gorehillfwy-artarmon** - Gore Hill Freeway, Artarmon
- **grandpde-bls** - Grand Parade, Brighton-Le-Sands
- **greatwesternhwy-hazelbrook** - Great Western Highway, Hazelbrook
- **harbourbridge** - Sydney Harbour Bridge
- **homebushbay-homebush** - Homebush Bay Drive, Homebush
- **humehwy-ashfield** - Hume Highway, Ashfield
- **humehwy-bankstown** - Hume Highway, Bankstown
- **humehwy-campbelltown** - Hume Highway, Campbelltown
- **humehwy-liverpool** - Hume Highway, Liverpool
- **humehwy-standrews** - Hume Highway, St Andrews
- **humehwy-strathfield** - Hume Highway, Strathfield
- **humehwy-villawood** - Hume Highway, Villawood
- **hunterexp-allandale** - Hunter Expressway, Allandale
- **hunterexp-branxton** - Hunter Expressway, Branxton
- **hunterexp-buchanan** - Hunter Expressway, Buchanan
- **hunterexpressway-m1** - Hunter Expressway, M1 Junction
- **jrd-rosehill** - James Ruse Drive, Rosehill
- **kinggeorge-hurstville** - King Georges Road, Hurstville
- **knggrd-beverlyhills** - King Georges Road, Beverly Hills
- **kosciuszkord-wilsonsvalley** - Kosciuszko Road, Wilsons Valley
- **m2-pennanthills** - M2 Hills Motorway, Pennant Hills
- **m2-ryde** - M2 Hills Motorway, Ryde
- **m4-auburn** - M4 Western Motorway, Auburn
- **m4-mayshill** - M4 Western Motorway, Mays Hill
- **m4-minchinbury** - M4 Western Motorway, Minchinbury
- **m4-olympic** - M4 Western Motorway, Olympic Park
- **m4-stmarys** - M4 Western Motorway, St Marys
- **m5-arncliffe** - M5 South Western Motorway, Arncliffe
- **m5-kingsgrove** - M5 South Western Motorway, Kingsgrove
- **m5-liverpool** - M5 South Western Motorway, Liverpool
- **m5-m7** - M5 South Western Motorway, M7 Junction
- **m5-milperra** - M5 South Western Motorway, Milperra
- **m5-padstow** - M5 South Western Motorway, Padstow
- **m5east** - M5 East Freeway
- **m7-glenwood** - M7 Westlink, Glenwood
- **m7-horsleydr** - M7 Westlink, Horsley Drive
- **manlyrd** - Manly Road
- **memorialdr-towradge** - Memorial Drive, Towradge
- **militaryrd-neutralbay** - Military Road, Neutral Bay
- **narelland-campbelltown** - Narellan Road, Campbelltown
- **newcastlelinkrd-newcastle** - Newcastle Link Road, Newcastle
- **newenglandhwy-hexham** - New England Highway, Hexham
- **newsthhead-edgecliff** - New South Head Road, Edgecliff
- **oldsthhead-bondi** - Old South Head Road, Bondi
- **oldwindsorrd** - Old Windsor Road
- **oldwindsorrd-winstonhills** - Old Windsor Road, Winston Hills
- **pacific-chats** - Pacific Highway, Chatswood
- **pacific-pymble** - Pacific Highway, Pymble
- **pacifichwy-macksville** - Pacific Highway, Macksville
- **pacifichwy-tomago** - Pacific Highway, Tomago
- **parra-ashfield** - Parramatta Road, Ashfield
- **parrard-leichhardt** - Parramatta Road, Leichhardt
- **parrard-parra** - Parramatta Road, Parramatta
- **parrard-silverwater** - Parramatta Road, Silverwater
- **parrard-strathfield** - Parramatta Road, Strathfield
- **pennanthills-beecroft** - Pennant Hills Road, Beecroft
- **pennanthillsrd-thornleigh** - Pennant Hills Road, Thornleigh
- **pittwaterrd-narrabeen** - Pittwater Road, Narrabeen
- **princes-blakehurst** - Princes Highway, Blakehurst
- **princes-kogarah** - Princes Highway, Kogarah
- **princes-stpeters** - Princes Highway, St Peters
- **princeshwy-albionparkrail** - Princes Highway, Albion Park Rail
- **princeshwy-batemans** - Princes Highway, Batemans Bay
- **princeshwy-bulli** - Princes Highway, Bulli
- **princeshwy-sutherland** - Princes Highway, Sutherland
- **princeshwy-wollongong** - Princes Highway, Wollongong
- **rydebridge** - Ryde Bridge
- **scd-eastlakes** - Southern Cross Drive, Eastlakes
- **sed-bondijunction** - South Eastern Distributor, Bondi Junction
- **sevenhillsrd-sevenhills** - Seven Hills Road, Seven Hills
- **shellharbour-warilla** - Shellharbour Road, Warilla
- **silverwaterrd-silverwater** - Silverwater Road, Silverwater
- **stewartst-eastwood** - Stewart Street, Eastwood
- **victoriard-gladesville** - Victoria Road, Gladesville
- **warringahfwy** - Warringah Freeway
- **warringahrd-forestville** - Warringah Road, Forestville
- **warringahrd-frenchsforest** - Warringah Road, Frenchs Forest
- **williamst** - William Street
- **yorkst-sydney** - York Street, Sydney