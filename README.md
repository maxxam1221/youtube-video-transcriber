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
- Create a single transcript file
- Save transcript as `output.txt`

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

This will create multiple files (`output_part1.txt`, `output_part2.txt`, etc.) if the transcript is long.

### Additional Options
- `-o` or `--output`: Specify output text file path (default: output.txt)
- `--split`: Split output into multiple files
- `--max-words`: Maximum words per file when splitting (default: 2000)

Example with all options:
```bash
python transcribe_video.py "VIDEO_URL" \
    --output "my_transcript.txt" \
    --split \
    --max-words 1500
```

## Output

The script generates a text file containing the video transcript:
- Single file by default
- Multiple files if --split is used (e.g., output_part1.txt, output_part2.txt, etc.)

## Notes

- The script uses Whisper for transcription
- All processing is done locally on your machine
- For very long videos, use the --split option to create multiple smaller transcript files
- Supports both YouTube and Bilibili videos 