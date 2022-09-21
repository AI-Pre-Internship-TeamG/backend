import config.settings as setting
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.decorators import parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser
from PIL import Image
from .services import saveImageToS3, deleteImageToS3
from .serializers import GetImageResponseSerializer, ImageSerializer, GetImageSerializer, ImageBodySerializer, ProcessImageBodySerializer
from config.models import User, Image
from json.decoder import JSONDecodeError
import requests


class ImagesView(APIView):

    token_info = openapi.Parameter('Authorization', openapi.IN_HEADER, description="access token", required=True, type=openapi.TYPE_STRING)
    pageParam = openapi.Parameter('page', openapi.IN_QUERY, description='페이지 정보', required=True, type=openapi.TYPE_NUMBER)  
    @swagger_auto_schema(
        tags=['Mypage'],
        manual_parameters=[token_info, pageParam],
        responses={
            status.HTTP_200_OK: GetImageResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: '{"message": "로그인 후 이용 가능한 서비스입니다."}'
        }
    )
    def get(self, request):
        '''
        사용자가 저장한 모든 사진 조회
        '''
        user = User.objects.get(email=request.user)
        if user is None:
            return Response({"message": "로그인 후 이용 가능한 서비스입니다."}, status=status.HTTP_401_UNAUTHORIZED)
        images = Image.objects.filter(user_id=user.id, status="EXS")
        paginator = Paginator(images, 12)
        page = request.GET.get('page')
        curPage = paginator.page(page)
        image = paginator.get_page(page)
        imageSerializer = GetImageSerializer(image, many=True)
        next_page = 0
        prev_page = 0
        if curPage.has_next():
            next_page = curPage.next_page_number()
        if curPage.has_previous():
            prev_page = curPage.previous_page_number()

        content = {
            "images": imageSerializer.data,  
            "meta": {
                "page": curPage.number,
                "pages": paginator.num_pages,
                "prev_page": prev_page,
                "next_page": next_page,
                "has_next": curPage.has_next(),
                "has_prev": curPage.has_previous()
            }
        }
        return Response(content, status=status.HTTP_200_OK)


    parser_classes = [MultiPartParser]
    @swagger_auto_schema(
        tags=['Mypage'],
        request_body=ImageBodySerializer,
        manual_parameters=[token_info],
        responses={status.HTTP_200_OK: ImageSerializer}
    )
    def post(self, request):
        '''
        최종 선택한 아마자 URL를 프론트 결과 테이블에 저장
        '''
        ## 받아온 url로 이미지 처리 후 다시 url 값 반환
        # 이미지 처리
        ## 유저 정보와 함께 DB에 이미지 저장
        user = User.objects.get(email=request.user)
        if user is None:
            return Response({"message": "로그인 후 이용 가능한 서비스입니다."}, status=status.HTTP_401_UNAUTHORIZED)
        imgUrl = request.body['img_url']
        content = {
            'user_id': user.id,
            'url': imgUrl
        }
        serializer = ImageSerializer(data=content)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED) 

class History(APIView):

    token_info = openapi.Parameter('Authorization', openapi.IN_HEADER, description="access token", required=True, type=openapi.TYPE_STRING)
    image_id = openapi.Parameter('photo', openapi.IN_PATH, description='이미지 ID', required=True, type=openapi.TYPE_NUMBER)
    @swagger_auto_schema(
        tags=['mypage'],
        manual_parameters=[token_info, image_id],
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
        
        try:
            image = Image.objects.get(id=photo, user_id=user.id, status="EXS")
        except Image.DoesNotExist:
            return Response({"message": "존재하지 않는 이미지 입니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GetImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['mypage'],
        manual_parameters=[token_info, image_id],
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
        selectImage.status = "DEL"
        selectImage.save()
        return JsonResponse({"messge": "이미지를 삭제하였습니다."}, status=status.HTTP_200_OK)