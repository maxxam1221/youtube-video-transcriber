import sys
import os
import yt_dlp
from faster_whisper import WhisperModel
import argparse
from datetime import timedelta

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    td = timedelta(seconds=seconds)
    hours = td.seconds//3600
    minutes = (td.seconds%3600)//60
    seconds = td.seconds%60
    milliseconds = td.microseconds//1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def download_audio(url, output_path="temp_audio.mp3"):
    """Download audio from YouTube video"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',  # Reduced quality for faster download
        }],
        'outtmpl': output_path.replace('.mp3', ''),
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return True
        except Exception as e:
            print(f"Error downloading video: {e}")
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
        return
    
    # Split into multiple files
    chunks = split_segments(segments, max_words)
    if len(chunks) == 1:
        print("Content fits in a single file")
        write_transcript_file(segments, output_path)
        return
    
    print(f"\nCreating {len(chunks)} separate files...")
    base_name, ext = os.path.splitext(output_path)
    
    for i, chunk in enumerate(chunks, 1):
        chunk_file = f"{base_name}_part{i}{ext}"
        write_transcript_file(chunk, chunk_file)
        print(f"Part {i} saved to {chunk_file}")

def main():
    parser = argparse.ArgumentParser(description="Transcribe YouTube video")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output", "-o", default="output.txt", help="Output text file path")
    parser.add_argument("--split", action="store_true", help="Split output into multiple files")
    parser.add_argument("--max-words", type=int, default=2000, 
                       help="Maximum words per file when splitting (default: 2000)")
    args = parser.parse_args()

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
            sys.exit(1)
        
        print("Starting transcription...")
        transcribe_audio(temp_audio, args.output, args.max_words, args.split)
        
        if not args.split:
            print(f"Transcription completed! Text saved to {args.output}")
    
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

if __name__ == "__main__":
    main() 