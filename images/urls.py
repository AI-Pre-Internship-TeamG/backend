from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.Upload.as_view(), name='uploadView'),
    path('', views.AllPhoto.as_view(), name='imagesView'),
    path('<int:image_id>/', views.History.as_view(), name='imageView')
]