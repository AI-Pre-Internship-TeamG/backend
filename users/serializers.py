from rest_framework import serializers
from .models import Users


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users  # 모델 설정
        fields = '__all__'
