from rest_framework import serializers
from config.models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image  # 모델 설정
        fields = ['user_id', 'url']

class GetImageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.URLField()
    created_at = serializers.DateTimeField(format = "%Y/%m/%d")
    class Meta:
        model = Image
        fields = ['id', 'url', 'created_at']

class ProcessImageBodySerializer(serializers.Serializer):
    imgData = serializers.CharField(help_text='마스킹 이미지 파일')
    originImgUrl = serializers.URLField(help_text='원본 이미지 파일')

class ImageBodySerializer(serializers.Serializer):
    file = serializers.ImageField(help_text='마스킹 이미지 파일')

class PageInfoSerializer(serializers.Serializer):
    page = serializers.IntegerField(help_text='현재 페이지')
    pages = serializers.IntegerField(help_text='전체 페이지')
    prev_page = serializers.IntegerField(help_text='이전 페이지')
    next_page = serializers.IntegerField(help_text='다음 페이지')
    has_next = serializers.IntegerField(help_text='다음 페이지 유무')
    has_prev = serializers.IntegerField(help_text='이전 페이지 유무')
    
class GetImageResponseSerializer(serializers.Serializer):
    image = GetImageSerializer(read_only=True)
    meta = PageInfoSerializer(read_only=True)