import sys
import os
import yt_dlp
from faster_whisper import WhisperModel
import argparse
from datetime import timedelta
import re

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    td = timedelta(seconds=seconds)
    hours = td.seconds//3600
    minutes = (td.seconds%3600)//60
    seconds = td.seconds%60
    milliseconds = td.microseconds//1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def is_bilibili_url(url):
    """Check if the URL is from Bilibili"""
    bilibili_patterns = [
        r'bilibili\.com/video/BV\w+',
        r'bilibili\.com/video/av\d+',
        r'b23\.tv/\w+'
    ]
    return any(re.search(pattern, url) for pattern in bilibili_patterns)

def is_youtube_url(url):
    """Check if the URL is from YouTube"""
    youtube_patterns = [
        r'youtube\.com/watch\?v=[\w-]+',
        r'youtu\.be/[\w-]+',
        r'youtube\.com/shorts/[\w-]+'
    ]
    return any(re.search(pattern, url) for pattern in youtube_patterns)

def extract_youtube_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'youtube\.com/watch\?v=([\w-]+)',
        r'youtu\.be/([\w-]+)',
        r'youtube\.com/shorts/([\w-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_bilibili_id(url):
    """Extract video ID from Bilibili URL"""
    patterns = [
        r'bilibili\.com/video/(BV\w+)',
        r'bilibili\.com/video/av(\d+)',
        r'b23\.tv/(\w+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_default_output_filename(url):
    """Generate default output filename based on video ID"""
    if is_youtube_url(url):
        video_id = extract_youtube_id(url)
        return f"youtube_{video_id}.txt" if video_id else "output.txt"
    elif is_bilibili_url(url):
        video_id = extract_bilibili_id(url)
        return f"bilibili_{video_id}.txt" if video_id else "output.txt"
    return "output.txt"

def get_download_options(url, output_path):
    """Get platform-specific download options"""
    base_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',  # Reduced quality for faster download
        }],
        'outtmpl': output_path.replace('.mp3', ''),
    }

    if is_youtube_url(url):
        base_opts['cookiesfrombrowser'] = ('chrome',)  # Use Chrome cookies for YouTube
    elif is_bilibili_url(url):
        base_opts.update({
            'extractor_args': {
                'bilibili': {
                    'cookie': os.getenv('BILIBILI_COOKIE', ''),  # Allow cookie override via env variable
                }
            }
        })
    
    return base_opts

def download_audio(url, output_path="temp_audio.mp3"):
    """Download audio from video"""
    if not (is_youtube_url(url) or is_bilibili_url(url)):
        print("Error: Unsupported video platform. Only YouTube and Bilibili are supported.")
        return False

    ydl_opts = get_download_options(url, output_path)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return True
        except Exception as e:
            print(f"Error downloading video: {e}")
            if "Sign in to confirm you're not a bot" in str(e):
                print("\nTroubleshooting tips for YouTube:")
                print("1. Make sure you're logged into YouTube in Chrome")
                print("2. If the error persists, try visiting YouTube in Chrome and solving any CAPTCHAs")
                print("3. Close and reopen Chrome, then try again")
            elif is_bilibili_url(url) and ("403" in str(e) or "login" in str(e).lower()):
                print("\nTroubleshooting tips for Bilibili:")
                print("1. Set your Bilibili cookie using the BILIBILI_COOKIE environment variable:")
                print("   export BILIBILI_COOKIE='your_cookie_here'")
                print("2. To get your cookie:")
                print("   a. Log into Bilibili in your browser")
                print("   b. Press F12 to open Developer Tools")
                print("   c. Go to Application > Cookies > bilibili.com")
                print("   d. Copy the SESSDATA cookie value")
            return False

def split_segments(segments, max_words_per_file=2000):
    """Split segments into chunks that won't exceed max_words_per_file"""
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for segment in segments:
        words_in_segment = len(segment.text.split())
        
        if current_word_count + words_in_segment >= max_words_per_file and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_word_count = 0
        
        current_chunk.append(segment)
        current_word_count += words_in_segment
    
    if current_chunk:
        chunks.append(current_chunk)
    
    if not chunks:
        chunks = [segments]
    
    return chunks

def write_transcript_file(segments, output_file):
    """Write segments to a text file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for segment in segments:
            f.write(f"{segment.text.strip()}\n")

def transcribe_audio(audio_path, output_path, max_words=2000, split=False):
    """Transcribe audio file and save as text"""
    print("Loading Whisper model (this might take a moment)...")
    # Optimize model settings for speed
    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8",
        cpu_threads=4,  # Adjust based on your CPU
        num_workers=2   # Parallel processing
    )
    
    print("Transcribing audio...")
    segments, _ = model.transcribe(
        audio_path,
        beam_size=1,          # Reduced beam size for speed
        best_of=1,            # Don't generate multiple candidates
        temperature=0.0,      # Deterministic output
        condition_on_previous_text=False,  # Don't condition on previous text
        initial_prompt=None   # No initial prompt
    )
    
    # Convert generator to list only once
    segments = list(segments)
    print(f"Transcribed {len(segments)} segments")
    
    if not split:
        print("Writing single file...")
        write_transcript_file(segments, output_path)
        return True
    
    # Split into multiple files
    chunks = split_segments(segments, max_words)
    if len(chunks) == 1:
        print("Content fits in a single file")
        write_transcript_file(segments, output_path)
        return True
    
    print(f"\nCreating {len(chunks)} separate files...")
    base_name, ext = os.path.splitext(output_path)
    
    for i, chunk in enumerate(chunks, 1):
        chunk_file = f"{base_name}_part{i}{ext}"
        write_transcript_file(chunk, chunk_file)
        print(f"Part {i} saved to {chunk_file}")
    
    return True

def main():
    """Main function to run the transcription process"""
    parser = argparse.ArgumentParser(description="Transcribe YouTube video")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output", "-o", help="Output text file path")
    parser.add_argument("--split", action="store_true", help="Split output into multiple files")
    parser.add_argument("--max-words", type=int, default=2000, 
                       help="Maximum words per file when splitting (default: 2000)")
    args = parser.parse_args()

    # Clean up any existing transcript files
    for file in os.listdir('.'):
        if (file.startswith('youtube_') or file.startswith('bilibili_')) and file.endswith('.txt'):
            os.remove(file)
            print(f"Removed existing file: {file}")

    # Set default output filename based on video ID if not specified
    if not args.output:
        args.output = get_default_output_filename(args.url)

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