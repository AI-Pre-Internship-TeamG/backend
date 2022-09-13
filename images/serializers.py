from rest_framework import serializers
from config.models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image  # 모델 설정
        fields = ['user_id', 'url']

class GetImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'user_id', 'url', 'created_at']