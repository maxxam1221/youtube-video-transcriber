# Video Transcription Tool

A Python tool for transcribing videos from YouTube and Bilibili using Whisper AI.

## Features

- Supports YouTube and Bilibili video URLs
- Uses Faster Whisper for efficient transcription
- Option to split long transcripts into multiple files
- Automatic cleanup of temporary files
- Supports multiple languages
- Configurable model size and compute type

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/transcript_video.git
cd transcript_video
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python transcribe_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Advanced options:
```bash
python transcribe_video.py "https://www.youtube.com/watch?v=VIDEO_ID" \
    --output custom_output.txt \
    --split \
    --max-words 2000 \
    --model base \
    --device cuda \
    --language en \
    --compute_type float16
```

### Command Line Arguments

- `url`: URL of the video to transcribe (required)
- `--output`, `-o`: Custom output file path
- `--split`: Split output into multiple files
- `--max-words`: Maximum words per file when splitting (default: 2000)
- `--model`, `-m`: Whisper model size (tiny, base, small, medium, large)
- `--device`, `-d`: Device to run inference on (cuda, cpu)
- `--language`, `-l`: Language code (e.g., en, zh, ja)
- `--compute_type`, `-c`: Model compute type (float16, float32, int8)

## Requirements

- Python 3.7+
- FFmpeg
- CUDA (optional, for GPU acceleration)

## License

MIT License 