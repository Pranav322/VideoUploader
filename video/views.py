
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.http import require_POST
from .models import Video
from .forms import VideoForm
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.conf import settings
import json


def home(request):
    return render(request, 'video/home.html')

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            video_file = form.cleaned_data['video']

            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name='ap-south-1'
            )
            
            try:
                presigned_url = s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                        'Key': f'videos/{video_file.name}'
                    },
                    ExpiresIn=3600  # URL expiration time in seconds
                )
                return JsonResponse({'url': presigned_url})
            except (NoCredentialsError, PartialCredentialsError):
                return JsonResponse({'error': 'Could not generate presigned URL'}, status=500)
    else:
        form = VideoForm()
    
    return render(request, 'video/upload_video.html', {'form': form})
import re
from .tasks import extract_subtitles
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def notify_upload_complete(request):
    try:
        logger.debug("Request body: %s", request.body)
        data = json.loads(request.body)
        title = data['title']
        filename = data['filename']

        # Save the video information to the database
        Video.objects.create(title=title, video=f'videos/{filename}')

        # Trigger Celery task to extract subtitles
        extract_subtitles.delay(filename)
        # upload_subtitles.delay(filename)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error("Error in notify_upload_complete: %s", str(e))
        return JsonResponse({'error': str(e)}, status=400)
 



from boto3.dynamodb.conditions import Key

def search_subtitles(request):
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()

        if not query:
            return render(request, 'video/search_subtitle.html', {'error': 'No query provided.'})

        try:
            dynamodb = boto3.resource('dynamodb',
                                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                     region_name='ap-south-1')

            table = dynamodb.Table('Subtitles')

            # Perform the query using DynamoDB
            response = table.scan()

            # Filter items client-side based on the query using regex
            subtitles = []
            for item in response.get('Items', []):
                subtitle_text = item.get('SubtitleText', '')
                # Match whole words only using regex
                if re.search(r'\b{}\b'.format(re.escape(query.lower())), subtitle_text.lower()):
                    video_id = item['VideoID']
                    s3_url = f"https://pranaw-bucket.s3.ap-south-1.amazonaws.com/videos/{video_id}.mp4"
                    subtitle = {
                        'VideoID': video_id,
                        'StartTime': item['StartTime'],
                        'EndTime': item['EndTime'],
                        'SubtitleText': subtitle_text,
                        'S3Url': s3_url
                    }
                    subtitles.append(subtitle)

            return render(request, 'video/search_subtitle.html', {'results': subtitles, 'query': query})

        except Exception as e:
            logger.error(f"Error fetching results: {str(e)}")
            return render(request, 'video/search_subtitle.html', {'error': 'Error fetching results. Please try again later.'})

    return render(request, 'video/search_subtitle.html', {'error': 'Method not allowed.'})