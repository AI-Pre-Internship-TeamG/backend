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
from .serializers import ImageSerializer, GetImageSerializer
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

class AllPhoto(APIView):

    def get(self, request):
        user = User.objects.get(email=request.user)
        if user is None:
            return Response({"message": "로그인 후 이용 가능한 서비스입니다."}, status=status.HTTP_401_AUTHENTICATE_ERROR)
        image = Image.objects.filter(user_id=user.id)
        print(image)
        imageSerializer = GetImageSerializer(image, many=True)
        print(imageSerializer)
        return Response(imageSerializer.data, status=status.HTTP_200_OK)

class History(APIView):

    def get(self, request, image_id):
        '''
        사용자가 선택한 이미지를 가져옴
        '''
        user = User.objects.get(email=request.user)
        if user is None:
            return Response({"message": "로그인 후 이용 가능한 서비스입니다."}, status=status.HTTP_401_AUTHENTICATE_ERROR)
        image = Image.objects.get(id=image_id, user_id=user.id)
        if image is None:
            return Response({"message": "존재하지 않는 이미지 입니다."}, stauts=status.404_NOT_FOUND)
        serializer = GetImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, image_id):
        '''
        사용자가 선택한 이미지 삭제
        '''
        user = User.objects.get(email=request.user)
        selectImage = Image.objects.get(id=image_id, user_id=user.id)
        if selectImage is None:
            return Response({"message": "존재하지 않는 이미지 입니다."}, stauts=status.404_NOT_FOUND)
        selectImage.delete()
        return JsonResponse({"messge": "이미지를 삭제하였습니다."}, status=status.HTTP_200_OK)