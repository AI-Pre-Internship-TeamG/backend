from rest_framework import serializers
from config.models import User

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # 모델 설정
        fields = '__all__'


class CustomLoginSerializer(serializers.ModelSerializer):
    username = None
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email','password')
        