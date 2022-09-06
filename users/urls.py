from django.urls import path, include
from users import views

urlpatterns = [
    path('google/login/', views.GoogleLogin.as_view(), name='google_login'),
    path('google/callback/', views.GoogleCallback.as_view, name='google_callback'),
    path('google/login/finish/', views.GoogleLoginToDjango.as_view(), name='google_login_todjango'),
]