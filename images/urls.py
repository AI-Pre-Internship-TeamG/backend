from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImagesView.as_view(), name='imagesView'),
    path('<int:photo>/', views.History.as_view(), name='imageView'),
    path('process/', views.Process.as_view(), name='imageView'),
    path('upload/', views.Upload.as_view(), name='imageView')
]