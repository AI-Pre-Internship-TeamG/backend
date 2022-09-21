import jwt
import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# 구글 OAuth 서버에서 사용자의 email을 받아옴
def googleEmailRequest(access_token):
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    print(email_req)
    if email_req_status != 200:
        raise ValidationError('인증에 실패하였습니다. 다시 로그인해 주세요')
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    return email

# Access Token 재발급
def recreateAccessToken(email, user):
    if email != user.email:
        return {"message":"인증에 실패하였습니다. 다시 로그인해 주세요." , "status":status.HTTP_401_UNAUTHORIZED}
    token = TokenObtainPairSerializer.get_token(user)
    access_token = str(token.access_token)
    response = {"access_token" : f"Bearer {access_token}", "status":status.HTTP_200_OK}
    return response