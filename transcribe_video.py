"""A tool for transcribing videos from YouTube and Bilibili using Whisper AI."""

import sys
import os
import yt_dlp
from faster_whisper import WhisperModel
import argparse
from datetime import timedelta
import re


def format_timestamp(seconds):
    """Format seconds into HH:MM:SS format."""
    return str(timedelta(seconds=int(seconds)))


def is_bilibili_url(url):
    """Check if the URL is a valid Bilibili URL."""
    return "bilibili.com" in url


def is_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    return "youtube.com" in url or "youtu.be" in url


def extract_youtube_id(url):
    """Extract video ID from YouTube URL."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:embed\/)([0-9A-Za-z_-]{11})",
        r"(?:watch\?v=)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_bilibili_id(url):
    """Extract video ID from Bilibili URL."""
    patterns = [r"BV[a-zA-Z0-9]{10}", r"av\d+"]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(0)
    return None


def get_default_output_filename(url):
    """Generate default output filename based on video URL."""
    if is_youtube_url(url):
        video_id = extract_youtube_id(url)
        return f"youtube_{video_id}.txt" if video_id else "output.txt"
    elif is_bilibili_url(url):
        video_id = extract_bilibili_id(url)
        return f"bilibili_{video_id}.txt" if video_id else "output.txt"
    return "output.txt"


def get_download_options(url, output_path):
    """Get platform-specific download options."""
    base_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": os.path.splitext(output_path)[0],
    }

    if is_youtube_url(url):
        base_opts["cookiesfrombrowser"] = ("chrome",)  # Use Chrome cookies for YouTube
    elif is_bilibili_url(url):
        base_opts.update(
            {
                "extractor_args": {
                    "bilibili": {
                        "cookie": os.getenv(
                            "BILIBILI_COOKIE", ""
                        ),  # Allow cookie override via env variable
                    }
                }
            }
        )

    return base_opts


def download_audio(url, output_path="temp_audio.mp3"):
    """Download audio from video URL and save to output path."""
    try:
        ydl_opts = get_download_options(url, output_path)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        return False


def split_segments(segments, max_words_per_file=2000):
    """Split segments into chunks that won't exceed max_words_per_file."""
    chunks = []
    current_chunk = []
    current_word_count = 0

    for segment in segments:
        segment_words = len(segment.text.split())
        if current_word_count + segment_words > max_words_per_file:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [segment]
            current_word_count = segment_words
        else:
            current_chunk.append(segment)
            current_word_count += segment_words

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def write_transcript_file(segments, output_file):
    """Write transcript segments to output file."""
    with open(output_file, "w", encoding="utf-8") as f:
        for segment in segments:
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            text = segment.text.strip()
            f.write(f"[{start} --> {end}] {text}\n")


def transcribe_audio(audio_path, output_path, max_words=2000, split=False):
    """Transcribe audio file and save transcript to output path."""
    try:
        # Initialize Whisper model
        model = WhisperModel("base", device="cuda", compute_type="float16")

        # Transcribe audio
        segments, _ = model.transcribe(audio_path)

        if not split:
            print("Writing single file...")
            write_transcript_file(segments, output_path)
            return True

        # Split into multiple files
        current_chunk = []
        current_word_count = 0
        chunks = []

        for segment in segments:
            segment_words = len(segment.text.split())
            if current_word_count + segment_words > max_words:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [segment]
                current_word_count = segment_words
            else:
                current_chunk.append(segment)
                current_word_count += segment_words

        if current_chunk:
            chunks.append(current_chunk)

        if len(chunks) == 1:
            print("Content fits in a single file")
            write_transcript_file(segments, output_path)
            return True

        print(f"\nCreating {len(chunks)} separate files...")
        base_name = os.path.splitext(output_path)[0]

        for i, chunk in enumerate(chunks, 1):
            chunk_file = f"{base_name}_part_{i}.txt"
            write_transcript_file(chunk, chunk_file)
            print(f"Part {i} saved to {chunk_file}")

        return True
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return False


def main():
    """Run the transcription process."""
    parser = argparse.ArgumentParser(description="Transcribe YouTube video")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output", "-o", help="Output text file path")
    parser.add_argument(
        "--split", action="store_true", help="Split output into multiple files"
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=2000,
        help="Maximum words per file when splitting (default: 2000)",
    )
    args = parser.parse_args()

    # Set default output filename based on video ID if not specified
    if not args.output:
        args.output = get_default_output_filename(args.url)
        # Clean up any existing files with the same pattern
        base_name = os.path.splitext(args.output)[0]
        for file in os.listdir("."):
            if file.startswith(base_name) and file.endswith(".txt"):
                os.remove(file)
                print(f"Removed existing file: {file}")

    # Print configuration
    print("\nConfiguration:")
    print(f"Input URL: {args.url}")
    print(f"Output file: {args.output}")
    print(f"Split files: {args.split}")
    if args.split:
        print(f"Max words per file: {args.max_words}")
    print()

    temp_audio = "temp_audio.mp3"

    try:
        print("Downloading audio...")
        if not download_audio(args.url, temp_audio):
            print("Error: Failed to download audio")
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            sys.exit(1)

        print("Starting transcription...")
        if not transcribe_audio(temp_audio, args.output, args.max_words, args.split):
            print("Error: Failed to transcribe audio")
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            sys.exit(1)

        if not args.split:
            print(f"Transcription completed! Text saved to {args.output}")

    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        sys.exit(1)
    finally:
        # Clean up temporary file
        if os.path.exists(temp_audio):
            os.remove(temp_audio)


if __name__ == "__main__":
    main()
