import subprocess
import os
import boto3
from celery import shared_task
import logging
from django.conf import settings
import re

logger = logging.getLogger(__name__)

@shared_task
def extract_subtitles(filename):
    try:
        # Create S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='ap-south-1'
        )

        # Define the local paths
        media_root = settings.MEDIA_ROOT
        
        # Path to the downloaded video file
        local_video_path = os.path.join(media_root, 'media', filename)

        # Download the video file from S3
        s3_key = f'videos/{filename}'
        s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, s3_key, local_video_path)
        
        # Path to the output .srt file
        base_filename = os.path.splitext(filename)[0]
        output_filename = base_filename + '.srt'
        output_srt_path = os.path.join(media_root, 'media', output_filename)
        
        # Command for subtitle extraction
        command = [
            'video/ccextractor_win_portable/ccextractorwinfull.exe',
            f'media/media/{filename}',
            '-o',
            f'media/media/{output_filename}'
        ]
        
        # Run subtitle extraction command
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            logger.info("Subtitle extraction successful.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Subtitle extraction failed: {e}")
            logger.error(e.stderr)
            return

        # Parse the .srt file
        subtitles = parse_srt(output_srt_path)

        # Upload parsed subtitles to DynamoDB
        upload_subtitles_to_dynamodb(base_filename, subtitles)

        logger.info(f"Uploaded subtitles for {base_filename} to DynamoDB.")

    except Exception as e:
        logger.error(f'Exception occurred: {str(e)}')
        return str(e)

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    pattern = re.compile(r'(\d+)\n([\d:,]+) --> ([\d:,]+)\n(.+?)(?=\n\d|\Z)', re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for match in matches:
        subtitle = {
            'StartTime': match[1].strip(),
            'EndTime': match[2].strip(),
            'SubtitleText': ' '.join(match[3].strip().split())
        }
        subtitles.append(subtitle)

    return subtitles

def upload_subtitles_to_dynamodb(video_id, subtitles):
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='ap-south-1'
        )

        # Upload subtitles to DynamoDB
        for subtitle in subtitles:
            dynamodb.put_item(
                TableName='Subtitles',
                Item={
                    'VideoID': {'S': video_id},
                    'StartTime': {'S': subtitle['StartTime']},
                    'EndTime': {'S': subtitle['EndTime']},
                    'SubtitleText': {'S': subtitle['SubtitleText']}
                }
            )
    except Exception as e:
        logger.error(f'Error uploading subtitles to DynamoDB: {str(e)}')
        raise


