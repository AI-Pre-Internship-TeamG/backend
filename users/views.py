from os import access
from urllib import response
import jwt
import requests
from .services import recreateAccessToken, googleEmailRequest
from config.models import User
from django.conf import settings
from django.urls import reverse
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from dj_rest_auth.registration.views import SocialLoginView
from json.decoder import JSONDecodeError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view

BASE_URL = 'http://localhost:8000/api/v1/users/'
GOOGLE_CALLBACK_URI = BASE_URL + 'google/callback/'
KAKAO_CALLBACK_URI = BASE_URL + 'kakao/callback/'

state = getattr(settings, 'STATE')

class GoogleLogin(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Google login'],
        responses={status.HTTP_201_CREATED: '{"Authorization": "Bearer token"}'}
    )
    def get(self, request):
        """
        Code request
        """
        scope = "https://www.googleapis.com/auth/userinfo.email"
        client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

class GoogleCallback(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Google login'])
    def get(self, request):
        client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
        code = request.GET.get('code')
        """
        받은 Code를 통해 Access Token 요청
        """
        token_req = requests.post(
            f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
        token_req_json = token_req.json()
        error = token_req_json.get("error")
        if error is not None:
            raise JSONDecodeError(error)
        access_token = token_req_json.get('access_token')
        refresh_token = token_req_json.get("refresh_token")
        """
        Email request - Access Token을 이용해 사용자의 이메일 반환받음
        """
        email = googleEmailRequest(access_token)
        cache.set(email, refresh_token, 60*60*24*28)
        """
        Signup or Signin Request
        """
        try:
            """
            Sign in
            """
            user = User.objects.get(email=email)
            # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
            social_user = SocialAccount.objects.get(user=user)
            if social_user is None:
                return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
            if social_user.provider != 'google': # 다른 SNS를 통해 가입된 user
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
            # 기존에 Google로 가입한 user
            data = {'access_token': access_token, 'code': code}
            accept = requests.post(f"{BASE_URL}google/login/finish/", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
            accept_json = accept.json()
            access_token = {"Authorization" : "Bearer " + accept_json['access_token']}
            return JsonResponse(access_token)

        except User.DoesNotExist:
            """
            Sign up
            """
            data = {'access_token': access_token, 'code': code}
            accept = requests.post(f"{BASE_URL}google/login/finish/", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
            accept_json = accept.json()
            access_token = {"Authorization" : "Bearer " + accept_json['access_token']}
            return JsonResponse(access_token)

@swagger_auto_schema(tags=['Google login'])
class GoogleLoginToDjango(SocialLoginView):
    
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client

class KakaoLogin(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Kakao login'],
        responses={status.HTTP_201_CREATED: '{"Authorization": "Bearer token"}'}
    )
    def get(self, request):
        rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
        kakao_auth_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        return redirect(
            f"{kakao_auth_api}&client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}"
        )

class KakaoCallback(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Kakao login']
    )
    def get(self, request):
        rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
        code = request.GET.get("code")
        redirect_uri = KAKAO_CALLBACK_URI
        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': rest_api_key,
            'redirection_uri' : redirect_uri,
            'code': code,
        }
        """
        Access Token Request
        """
        token_res = requests.post(kakao_token_api, data=data)
        # return  JsonResponse({"token": token_res.json()})
        access_token = token_res.json().get('access_token')
        # return JsonResponse({"access_token": access_token})
        refresh_token = token_res.json().get('refresh_token')
        """
        Email Request 이메일이 출력이 안되고 있음!
        """
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f'Bearer ${access_token}'})
        profile_json = profile_request.json()
        # return JsonResponse({"user_info": profile_json})
        error = profile_json.get("error")
        if error is not None:
            raise JSONDecodeError(error)
        kakao_account = profile_json.get('kakao_account')
        # return JsonResponse({"user_info": profile_json})
        """
        kakao_account에서 이메일 외에
        카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
        print(kakao_account) 참고
        """
        # print(kakao_account)
        email = kakao_account.get('email')
        cache.set(email, refresh_token, 60*60*24*28)
        """
        Signup or Signin Request
        """
        try:
            user = User.objects.get(email=email)
            # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
            # 다른 SNS로 가입된 유저
            social_user = SocialAccount.objects.get(user=user)
            if social_user is None:
                return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
            if social_user.provider != 'kakao':
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
            # 기존에 kakao로 가입된 유저
            data = {'access_token': access_token, 'code': code}
            accept = requests.post(
                f"{BASE_URL}kakao/login/finish/", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
            accept_json = accept.json()
            accept_json.pop('user', None)
            refresh_token = accept_json['refresh_token']
            access_token = {"Authorization" : "Bearer " + accept_json['access_token']}
            return JsonResponse(access_token)

        except User.DoesNotExist:
            # 기존에 가입된 유저가 없으면 새로 가입
            data = {'access_token': access_token, 'code': code}
            accept = requests.post(
                f"{BASE_URL}kakao/login/finish/", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
            # user의 pk, email, first name, last name과 Access Token, Refresh token 가져옴
            accept_json = accept.json()
            accept_json.pop('user', None)
            refresh_token = accept_json['refresh_token']
            access_token = {"Authorization" : "Bearer " + accept_json['access_token']}
            return JsonResponse(access_token)

class KakaoLoginToDjango(SocialLoginView):

    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI

class RefreshAccessToken(APIView):
    @swagger_auto_schema(
        tags=['Refresh Access Token']
    )
    def get(self, request):
        """
        토큰 재발급을 위한 사용자 식별
        사용자의 provider 확인
        """
        user = request.user
        social_user = SocialAccount.objects.get(user=user)
        if social_user.provider == 'google':
            return redirect(reverse('google_refresh'))
        elif social_user.provider == 'kakao':
            return redirect(reverse('kakao_refresh'))

class RefresKakaoAccessToken(APIView):

    @swagger_auto_schema(
        tags=['Refresh Access Token']
    )
    def get(self, request):
        user = request.user
        refreshToken = cache.get(user)
        rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
        data = {
            "grant_type": "refresh_token",
            "client_id": rest_api_key,
            "refresh_token": refreshToken
        }
        token_res = requests.post("https://kauth.kakao.com/oauth/token", data=data)
        token_res_json = token_res.json()
        access_token = token_res_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f'Bearer ${access_token}'})
        profile_json = profile_request.json()
        error = profile_json.get("error")
        if error is not None:
            raise JSONDecodeError(error)
        kakao_account = profile_json.get('kakao_account')
        email = kakao_account.get('email')
        access_token_request = recreateAccessToken(email, user)  # request를 보낸 사용자와 Access token의 사용자가 일치하는지 확인 후 토큰 재발급
        token_status = access_token_request.get("status")
        response = Response(
            {
                "Authorization": access_token_request.get("access_token")
            },
            status=token_status
        )
        return response

class RefresGoogleAccessToken(APIView):
    
    @swagger_auto_schema(
        tags=['Refresh Access Token']
    )
    def get(self, request):
        user = request.user
        client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
        refreshToken = cache.get(user) # 저장해둔 사용자의 refresh token
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refreshToken,
            "grant_type": "refresh_token",
        }
        token_res = requests.post("https://oauth2.googleapis.com/token", data=data)
        token_res_json = token_res.json()
        googe_access_token = token_res_json.get("access_token")
        email = googleEmailRequest(googe_access_token) # 해당 사용자가 존재하는지 확인
        access_token_request = recreateAccessToken(email, user) # request를 보낸 사용자와 Access token의 사용자가 일치하는지 확인 후 토큰 재발급
        token_status = access_token_request.get("status")
        response = Response(
            {
                "Authorization": access_token_request.get("access_token")
            },
            status=token_status
        )
        return response