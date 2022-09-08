import boto3
import uuid
import config.settings as setting
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.decorators import parser_classes
from PIL import Image
import config.settings as settings

class Upload(APIView):
    '''
    프론트에서 받아온 이미지를 S3에 저장 후 처리한 이미지의 결과 반환
    반환된 결과는 DB에 저장
    '''
    def post(self, request):
        user = request.user
        uploadFile = request.FILES['filename']
        uploadFile._set_name(str(uuid.uuid4()))
        s3r = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)
        key = f"before/{uploadFile}" # 사진이 저장될 경로 설정
        s3r.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object( Key=key, Body=uploadFile, ContentType = "png") # 버켓에 이미지 저장
        imageUrl = settings.AWS_S3_CUSTOM_DOMAIN+key # 이 뒤로 이미지 처리
        return JsonResponse({"imageUrl": imageUrl})
        ## 받아온 url로 이미지 처리 후 다시 url 값 반환