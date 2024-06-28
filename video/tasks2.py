import logging
import os
import subprocess

# Set up logging
logger = logging.getLogger(__name__)

# Define paths and variables
ccextractor_path = os.path.join('ccextractor_win_portable', 'ccextractorwinfull.exe')
output_file = 'subtitles.srt'
video_file = 'test.mp4'

# Command to extract subtitles
cmd = [ccextractor_path, video_file, '-o', output_file]

# Run command
try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    logger.info(f'Subtitles extracted successfully for {video_file}')
except subprocess.CalledProcessError as e:
    logger.error(f'Failed to extract subtitles for {video_file}: {e}')
