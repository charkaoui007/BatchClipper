import subprocess
import os
import shutil

# Path to the configuration file
config_file = './clips_config.txt'

# Directory to save the processed clips
output_dir = 'C:\\Users\\anass\\Desktop\\clips'
os.makedirs(output_dir, exist_ok=True)

def time_to_seconds(time_str):
    """Convert a time string in hh:mm:ss or mm:ss format to seconds."""
    if time_str == '-':
        return None
    parts = time_str.split(':')
    if len(parts) == 3:  # hh:mm:ss
        hours, minutes, seconds = map(int, parts)
    elif len(parts) == 2:  # mm:ss
        hours = 0
        minutes, seconds = map(int, parts)
    else:  # ss
        hours = 0
        minutes = 0
        seconds = int(parts[0])
    return hours * 3600 + minutes * 60 + seconds

def download_and_cut_audio(url, start_time_str, end_time_str, output_filename):
    try:
        # Clean up the output filename (remove extra quotes)
        output_filename = output_filename.replace('"', '')

        # Convert time strings to seconds if needed
        start_time = time_to_seconds(start_time_str)
        end_time = time_to_seconds(end_time_str)

        print(f"Processing {url}...")

        # Define the output file path
        output_file_path = os.path.join(output_dir, output_filename)
        print(f"Output file path: {output_file_path}")

        # Command to download the audio and pipe it directly to FFmpeg (extract audio)
        download_command = [
            'yt-dlp',
            '--quiet',  # Suppress unnecessary output
            '-f', 'bestaudio',  # Download the best audio format
            '-o', '-',  # Output to stdout
            url
        ]

        # FFmpeg command to convert the audio to MP3 format
        cut_command = [
            'ffmpeg',
            '-i', 'pipe:0',  # Read from stdin
            '-vn',  # Disable video
            '-acodec', 'libmp3lame',  # Use MP3 codec
            '-ab', '192k',  # Set audio bitrate to 192k
            output_file_path
        ]

        # If start_time and end_time are both None, don't cut the audio
        if start_time is not None and end_time is not None:
            cut_command = [
                'ffmpeg',
                '-i', 'pipe:0',  # Read from stdin
                '-vn',  # Disable video
                '-acodec', 'libmp3lame',  # Use MP3 codec
                '-ab', '192k',  # Set audio bitrate to 192k
                '-ss', str(start_time),  # Start time
                '-to', str(end_time),  # End time
                output_file_path
            ]

        # Run yt-dlp to stream audio to FFmpeg
        with subprocess.Popen(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            with subprocess.Popen(cut_command, stdin=proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as ffmpeg_proc:
                # Capture output and errors for debugging
                stdout, stderr = ffmpeg_proc.communicate()
                if stderr:
                    print(f"FFmpeg error: {stderr.decode('utf-8')}")
                if stdout:
                    print(f"FFmpeg output: {stdout.decode('utf-8')}")

        print(f"Processed audio saved to {output_file_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to process {url}: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

# Check disk space before running
def check_disk_space():
    """Print disk space details."""
    total, used, free = shutil.disk_usage(output_dir)
    print(f"Disk space before processing: {free // (2 ** 30)} GiB free")

check_disk_space()

# Read configuration file and process each video
with open(config_file, 'r') as file:
    for line in file:
        # Parse the configuration line
        line = line.strip()
        if line:
            try:
                video_url, start_time_str, end_time_str, output_filename = line.split(',')
                print(f"Processing: {video_url} -> {output_filename}")
                # Process the audio
                download_and_cut_audio(video_url, start_time_str, end_time_str, output_filename)
            except ValueError as e:
                print(f"Skipping invalid line: {line} (Error: {e})")

# Check disk space after running
check_disk_space()

print("Batch processing completed.")
