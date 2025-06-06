# YouTube Video Transcriber

This Python script downloads a YouTube video's audio and generates a transcript. All processing is done locally on your machine - no API keys required!

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
Run the script with a YouTube URL:
```bash
python transcribe_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

By default, this will:
- Create a single transcript file
- Save transcript as `output.txt`

### Split Long Transcripts
For long videos, you can split the transcript into multiple files:
```bash
python transcribe_video.py "https://www.youtube.com/watch?v=VIDEO_ID" --split
```

This will create multiple files (`output_part1.txt`, `output_part2.txt`, etc.) if the transcript is long.

### Additional Options
- `-o` or `--output`: Specify output text file path (default: output.txt)
- `--split`: Split output into multiple files
- `--max-words`: Maximum words per file when splitting (default: 2000)

Example with all options:
```bash
python transcribe_video.py "https://www.youtube.com/watch?v=VIDEO_ID" \
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