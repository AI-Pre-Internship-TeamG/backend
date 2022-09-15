import boto3
import uuid
import config.settings as setting
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.decorators import parser_classes
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
from .services import saveImageToS3
from .serializers import ImageSerializer, GetImageSerializer
from config.models import User, Image

class ImagesView(APIView):

    @swagger_auto_schema(
        tags=['mypage'],
        responses={status.HTTP_200_OK: GetImageSerializer}
    )
    def get(self, request):
        '''
        사용자가 저장한 모든 사진 조회
        '''
        user = User.objects.get(email=request.user)
        if user is None:
            return Response({"message": "로그인 후 이용 가능한 서비스입니다."}, status=status.HTTP_401_UNAUTHORIZED)
        images = Image.objects.filter(user_id=user.id)
        paginator = Paginator(images, 12)
        page = request.GET.get('page')
        curPage = paginator.page(page)
        image = paginator.get_page(page)
        imageSerializer = GetImageSerializer(image, many=True)
        if curPage.has_next():
            next_page = curPage.previous_page_number()
        else:
            next_page = 0

        if curPage.has_previous():
            prev_page = curPage.previous_page_number()
        else:
            prev_page = 0

        content ={
            "images": imageSerializer.data,
            "page_info": {
                "page": page,
                "pages": curPage.end_index(),
                "prev_page": prev_page,
                "next_page": next_page,
                "has_next": curPage.has_next(),
                "has_prev": curPage.has_previous()
            }
        }
        return Response(content, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=['Image upload'],
        responses={status.HTTP_200_OK: ImageSerializer}
    )
    def post(self, request):
        '''
        프론트에서 받아온 이미지를 S3에 저장 후 처리한 이미지의 결과 반환
        반환된 결과는 DB에 저장
        '''
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

class History(APIView):

    @swagger_auto_schema(
        tags=['mypage'],
        responses={
            status.HTTP_401_UNAUTHORIZED: '{"message": "로그인 후 이용 가능한 서비스입니다."}',
            status.HTTP_404_NOT_FOUND: '{"message": "존재하지 않는 이미지 입니다."}',
            status.HTTP_200_OK: GetImageSerializer
        }
    )
    def get(self, request, photo):
        '''
        사용자가 선택한 이미지 조회
        '''
        user = User.objects.get(email=request.user)
        if user is None:
            return Response({"message": "로그인 후 이용 가능한 서비스입니다."}, status=status.HTTP_401_UNAUTHORIZED)
        image = Image.objects.get(id=photo, user_id=user.id)
        if image is None:
            return Response({"message": "존재하지 않는 이미지 입니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = GetImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['mypage'],
        responses={
            status.HTTP_401_UNAUTHORIZED: '{"message": "로그인 후 이용 가능한 서비스입니다."}',
            status.HTTP_404_NOT_FOUND: '{"message": "존재하지 않는 이미지 입니다."}',
            status.HTTP_200_OK: '{"message": "이미지를 삭제하였습니다."}'
        }
    )
    def delete(self, request, photo):
        '''
        사용자가 선택한 이미지 삭제
        '''
        user = User.objects.get(email=request.user)
        if user is None:
            return Response({"message": "로그인 후 이용 가능한 서비스입니다."}, status=status.HTTP_401_UNAUTHORIZED)
        selectImage = Image.objects.get(id=photo, user_id=user.id)
        if selectImage is None:
            return Response({"message": "존재하지 않는 이미지 입니다."}, status=status.HTTP_404_NOT_FOUND)
        selectImage.delete()
        return JsonResponse({"messge": "이미지를 삭제하였습니다."}, status=status.HTTP_200_OK)