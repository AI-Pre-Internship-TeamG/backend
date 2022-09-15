# backend
1. backend 폴더로 이동

2. 이미지 빌드
```
docker build -f Dockerfile -t backend .
```

3. 컨테이너 생성 및 실행
```
docker run -p 3000:3000 backend
```

**pip로 패키지 다운로드할 경우**
requirements.txt에 패키지명 작성 부탁드립니다!