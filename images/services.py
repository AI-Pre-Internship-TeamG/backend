import config.settings as settings
import boto3
import uuid
def saveImageToS3(uploadFile, state):
    # 파일 확장자 추출
    fileFormat = uploadFile.content_type.split("/")[1]
    uploadFile._set_name(str(uuid.uuid4()))
    s3r = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)
    key = f"{state}/{uploadFile}" # 사진이 저장될 경로 설정
    s3r.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=key, Body=uploadFile, ContentType=fileFormat) # 버켓에 이미지 저장
    imageUrl = settings.AWS_S3_CUSTOM_DOMAIN+key # 이 뒤로 이미지 처리
    return imageUrl