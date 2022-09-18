from rest_framework import serializers
from config.models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image  # 모델 설정
        fields = ['user_id', 'url']

class GetImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'url']

class ImageBodySerializer(serializers.Serializer):
    file = serializers.ImageField(help_text='이미지 파일')

class GetImageResponseSerializer(serializers.Serializer):
    image = GetImageSerializer(read_only=True)
    page = serializers.IntegerField(help_text='현재 페이지')
    pages = serializers.IntegerField(help_text='전체 페이지')
    prev_page = serializers.IntegerField(help_text='이전 페이지')
    next_page = serializers.IntegerField(help_text='다음 페이지')
    has_next = serializers.IntegerField(help_text='다음 페이지 유무')
    has_prev = serializers.IntegerField(help_text='이전 페이지 유무')