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
            'preferredquality': '192',
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

def transcribe_audio(audio_path, output_srt):
    """Transcribe audio file and save as SRT"""
    print("Loading Whisper model (this might take a moment)...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    
    print("Transcribing audio...")
    segments, _ = model.transcribe(audio_path, beam_size=5)
    
    print("Generating SRT file...")
    with open(output_srt, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            text = segment.text.strip()
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

def main():
    parser = argparse.ArgumentParser(description="Transcribe YouTube video to SRT subtitles")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output", "-o", default="output.srt", help="Output SRT file path")
    args = parser.parse_args()

    temp_audio = "temp_audio.mp3"
    
    try:
        print("Downloading audio...")
        if not download_audio(args.url, temp_audio):
            sys.exit(1)
        
        print("Starting transcription...")
        transcribe_audio(temp_audio, args.output)
        
        print(f"Transcription completed! Subtitles saved to {args.output}")
    
    finally:
        # Cleanup temporary audio file
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

if __name__ == "__main__":
    main() 