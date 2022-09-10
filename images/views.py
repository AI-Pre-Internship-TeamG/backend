import boto3
import uuid
import config.settings as setting
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.decorators import parser_classes
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
from .services import saveImageToS3
from .serializers import ImageSerializer
from config.models import User, Image

class Upload(APIView):
    '''
    프론트에서 받아온 이미지를 S3에 저장 후 처리한 이미지의 결과 반환
    반환된 결과는 DB에 저장
    '''
    def post(self, request):
        user = request.user
        uploadFile = request.FILES['filename']
        imageUrl = saveImageToS3(uploadFile, "before")
        ## 받아온 url로 이미지 처리 후 다시 url 값 반환
        # 이미지 처리
        ## 유저 정보와 함께 DB에 이미지 저장
        uploadUser = User.objects.get(email=user)
        content = {
            'user_id': uploadUser.id,
            'url': imageUrl
        }
        serializer = ImageSerializer(data=content)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)