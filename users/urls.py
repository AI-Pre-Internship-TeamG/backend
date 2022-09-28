from django.urls import path, include
from users import views

urlpatterns = [
    path('google/login/', views.GoogleLogin.as_view(), name='google_login'),
    path('google/callback/', views.GoogleCallback.as_view(), name='google_callback'),
    path('google/login/finish/', views.GoogleLoginToDjango.as_view(), name='google_login_todjango'),
    path('google/refresh/', views.RefresGoogleAccessToken.as_view(), name="google_refresh"),
    path('kakao/login/', views.KakaoLogin.as_view(), name='kakao_login'),
    path('kakao/callback/', views.KakaoCallback.as_view(), name='kakao_callback'),
    path('kakao/login/finish/', views.KakaoLoginToDjango.as_view(), name='kakao_login_todjango'),
    path('kakao/refresh/', views.RefresKakaoAccessToken.as_view(), name="kakao_refresh"),
    path('o/token/', views.RefreshAccessToken.as_view(), name='refresh_access_token'),
    path('logout', views.Logout.as_view(), name='user_logout')
]