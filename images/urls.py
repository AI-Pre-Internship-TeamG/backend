from django.urls import path
from images.views import upload

urlpatterns = [
    path('images/', upload.as_view())
]