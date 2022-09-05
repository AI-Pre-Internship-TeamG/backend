from django.shortcuts import render
import boto3
import config.settings as setting
from rest_framework.views import APIView

from django.http import HttpResponse, JsonResponse


class upload(APIView):
    def post(self, request):
        try:
            files = request.FILES.getlist('files')  # request에서 files라는 키의 이미지 데이터
            client = boto3.resource('s3', aws_access_key_id=setting.AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=setting.AWS_SECRET_ACCESS_KEY)
            for file in files:
                file._set_name('test')  # 업로드할 파일 이름 지정
                client.Bucket(setting.AWS_STORAGE_BUCKET_NAME).put_object(Key='test.jpg', Body=file, ContentType='jpg')
            return JsonResponse({"MESSGE": "SUCCESS"}, status=200)

        except Exception as e:
            return JsonResponse({"ERROR": e.message})
