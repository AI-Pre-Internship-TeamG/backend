import jwt
import requests
from .models import User
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.registration.views import SocialLoginView
from json.decoder import JSONDecodeError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress

# Create your views here.
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'users/google/callback/'

state = getattr(settings, 'STATE')

class GoogleLogin(APIView):
    """
    Code request
    """
    def get(self, request):
        scope = "https://www.googleapis.com/auth/userinfo.email"
        client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


class GoogleCallback(APIView):
    def get(request, self):
        client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
        code = request.GET.get('code')
        """
        받은 Code를 통해 Access Token 요청
        """
        param = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_CALLBACK_URI,
            'grant_type': 'authorization_code'
        }
        token_req = requests.post( "https://oauth2.googleapis.com/token", data=data)
        token_req_json = token_req.json()
        error = token_req_json.get("error")
        if error is not None:
            raise JSONDecodeError(error)
        access_token = token_req_json.get('access_token')
        """
        Email request - Access Token을 이용해 사용자의 이메일 반환받음
        """
        email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
        email_req_status = email_req.status_code
        if email_req_status != 200:
            return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
        email_req_json = email_req.json()
        email = email_req_json.get('email')

        """
        Signup or Signin Request
        """
        try:
            """
            Sign in
            """
            user = User.objects.get(email=email)
            social_user = SocialAccount.objects.get(user=user)
            if social_user is None: # 소셜 로그인 회원이 아닌 user
                return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
            if social_user.provider != 'google': # 다른 SNS를 통해 가입된 user
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
            data = {'access_token': access_token, 'code': code}
            accept = accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
            accept_json = accept.json()
            refresh_token = acceept_json['refresh_token']
            cache.set(email, refresh_token)
            return JsonResponse(accept_json)
        
        except User.DoseNotExist:
            """
            Sign up
            """
            data = {'access_token': access_token, 'code': code}
            accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
            accept_json = accept.json()
            refresh_token = accept_json['refresh_token']
            cache.set(email, refresh_token)
            return JsonResponse(accept_json)

class GoogleLoginToDjango(SocialLoginView):

    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client
