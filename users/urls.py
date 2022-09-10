from django.urls import path, include
from users import views

urlpatterns = [
    path('google/login/', views.GoogleLogin.as_view(), name='google_login'),
    path('google/callback/', views.GoogleCallback.as_view(), name='google_callback'),
    path('google/login/finish/', views.GoogleLoginToDjango.as_view(), name='google_login_todjango'),
    path('google/refresh/', views.refresGoogleAccessToken, name='refresh_google'),
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', views.KakaoLogin.as_view(), name='kakao_login_todjango'),
    path('kakao/refresh/', views.refreshKakaoAccessToken, name='refresh_kakao'),
]