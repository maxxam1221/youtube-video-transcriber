# YouTube Video Transcriber

This Python script downloads a YouTube video's audio and generates subtitles in SRT format using OpenAI's Whisper speech recognition model.

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

Run the script with a YouTube URL:
```bash
python transcribe_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

To specify a custom output file:
```bash
python transcribe_video.py "https://www.youtube.com/watch?v=VIDEO_ID" -o my_subtitles.srt
```

The script will:
1. Download the audio from the YouTube video
2. Transcribe the audio using Whisper
3. Generate subtitles in SRT format
4. Clean up temporary files automatically

## Output

The script generates an SRT file containing the video transcription with timestamps. By default, the output file is named `output.srt`. 