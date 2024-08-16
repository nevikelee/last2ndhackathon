import subprocess

def split_audio(input_file, output_pattern, segment_time):
    # Splits an audio file into smaller segments
    # Input_file is the path of the chosen file
    # Output pattern is printf like. Segment time is measured in seconds
    # Example usage: split_audio('audio.mp3', 'output_audio_%03d.mp3', 10)
    try:
        command = [
            'ffmpeg',
            '-i', input_file,
            '-f', 'segment',
            '-segment_time', str(segment_time),
            '-c', 'copy',
            output_pattern
        ]
        
        subprocess.run(command, check=True)
        print(f"Audio split successfully. ")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    except FileNotFoundError:
        print("ffmpeg is not installed or not found in the system PATH.")
