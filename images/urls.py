from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImagesView.as_view(), name='imagesView'),
    path('<int:image_id>/', views.History.as_view(), name='imageView')
]