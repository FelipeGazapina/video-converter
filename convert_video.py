import subprocess
import os
import shutil
import sys

def check_ffmpeg():
    """
    Checks if FFmpeg is installed and available in PATH.
    """
    if not shutil.which("ffmpeg"):
        print("❌ Error: FFmpeg is not installed or not in PATH.")
        print("\nTo install FFmpeg, run:")
        print("  sudo apt update")
        print("  sudo apt install -y ffmpeg")
        print("\nOr download from: https://ffmpeg.org/download.html")
        sys.exit(1)

def convert_mkv_to_mp4(input_file, output_file=None):
    """
    Converts an MKV file to MP4 using FFmpeg.
    """
    if not output_file:
        output_dir = "output/mp4"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + ".mp4")

    print(f"Converting {input_file} → {output_file} ...")
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "copy",  # copy video stream (no re-encoding)
        "-c:a", "aac",   # convert audio to AAC for MP4 compatibility
        "-strict", "experimental",
        output_file,
        "-y"  # overwrite output without asking
    ]
    subprocess.run(command, check=True)
    print("✅ Conversion to MP4 complete.")
    return output_file


def extract_mp3_from_mp4(input_file, output_file=None):
    """
    Extracts MP3 audio from an MP4 file using FFmpeg.
    """
    if not output_file:
        output_dir = "output/mp3"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + ".mp3")

    print(f"Extracting MP3 from {input_file} → {output_file} ...")
    command = [
        "ffmpeg",
        "-i", input_file,
        "-q:a", "0",   # best quality
        "-map", "a",
        output_file,
        "-y"
    ]
    subprocess.run(command, check=True)
    print("✅ MP3 extraction complete.")
    return output_file


def compress_mp4(input_file, output_file=None):
    """
    Compresses an MP4 file using FFmpeg with H.264 codec.
    """
    if not output_file:
        output_dir = "output/mp4/compressed"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + "_compressed.mp4")

    print(f"Compressing {input_file} → {output_file} ...")
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "libx264",      # H.264 video codec
        "-crf", "23",           # quality (lower = better, 23 is default)
        "-preset", "medium",    # encoding speed vs compression ratio
        "-c:a", "aac",          # AAC audio codec
        "-b:a", "128k",         # audio bitrate
        output_file,
        "-y"
    ]
    subprocess.run(command, check=True)
    print("✅ Compression complete.")
    return output_file


if __name__ == "__main__":
    import argparse

    # Check if FFmpeg is installed before proceeding
    check_ffmpeg()

    parser = argparse.ArgumentParser(description="Convert video files: MKV → MP4, compress MP4, or extract MP3")
    parser.add_argument("input", help="Path to the input video file")
    parser.add_argument("--to-mp3", action="store_true", help="Extract MP3 from MP4 file")
    parser.add_argument("--compress", action="store_true", help="Compress MP4 file (outputs to output/mp4/compressed)")

    args = parser.parse_args()

    # Get the file extension
    _, ext = os.path.splitext(args.input)
    ext = ext.lower()

    # Check if input is MP4
    if ext == ".mp4":
        # If input is MP4, require a flag to know what to do
        if not args.to_mp3 and not args.compress:
            print("❌ Error: Input file is already MP4. Please specify what to do:")
            print("  --to-mp3     Extract MP3 audio from the MP4")
            print("  --compress   Compress the MP4 file")
            sys.exit(1)
        
        mp4_file = args.input
        
        if args.compress:
            compress_mp4(mp4_file)
        
        if args.to_mp3:
            extract_mp3_from_mp4(mp4_file)
    else:
        # For non-MP4 files (like MKV), convert to MP4 first
        mp4_file = convert_mkv_to_mp4(args.input)
        
        if args.compress:
            mp4_file = compress_mp4(mp4_file)
        
        if args.to_mp3:
            extract_mp3_from_mp4(mp4_file)
