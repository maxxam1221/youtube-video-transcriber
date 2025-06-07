# Video Transcriber

This Python script downloads videos from YouTube or Bilibili and generates transcripts. All processing is done locally on your machine - no API keys required!

## Prerequisites

- Python 3.7 or higher
- FFmpeg (required for audio processing)

## Installation

1. Install FFmpeg:
   - On macOS: `brew install ffmpeg`
   - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - On Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Run the script with a video URL:
```bash
# For YouTube
python transcribe_video.py "https://www.youtube.com/watch?v=VIDEO_ID"

# For Bilibili
python transcribe_video.py "https://www.bilibili.com/video/BV..."
```

By default, this will:
- Create a transcript file named after the video ID:
  - YouTube videos: `youtube_VIDEO_ID.txt`
  - Bilibili videos: `bilibili_VIDEO_ID.txt`

### Authentication

#### YouTube
The script uses Chrome cookies for YouTube authentication. Make sure you:
1. Are logged into YouTube in Chrome
2. Have completed any CAPTCHAs if requested

#### Bilibili
For Bilibili videos that require login, you'll need to provide your cookie:
1. Log into Bilibili in your browser
2. Get your SESSDATA cookie:
   - Press F12 to open Developer Tools
   - Go to Application > Cookies > bilibili.com
   - Find and copy the SESSDATA cookie value
3. Set the environment variable:
```bash
export BILIBILI_COOKIE='your_cookie_here'
```

### Split Long Transcripts
For long videos, you can split the transcript into multiple files:
```bash
python transcribe_video.py "VIDEO_URL" --split
```

This will create multiple files with the video ID in the name:
- For YouTube: `youtube_VIDEO_ID_part1.txt`, `youtube_VIDEO_ID_part2.txt`, etc.
- For Bilibili: `bilibili_VIDEO_ID_part1.txt`, `bilibili_VIDEO_ID_part2.txt`, etc.

### Additional Options
- `-o` or `--output`: Specify custom output text file path (optional)
- `--split`: Split output into multiple files
- `--max-words`: Maximum words per file when splitting (default: 2000)

Example with all options:
```bash
python transcribe_video.py "VIDEO_URL" \
    --output "custom_name.txt" \
    --split \
    --max-words 1500
```

## Output

The script generates a text file containing the video transcript:
- Single file by default, named after the video ID
- Multiple files if --split is used, with part numbers appended
- Custom filename if specified with --output

## Notes

- The script uses Whisper for transcription
- All processing is done locally on your machine
- For very long videos, use the --split option to create multiple smaller transcript files
- Supports both YouTube and Bilibili videos 