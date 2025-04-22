#!/bin/bash

# Docker 이미지 빌드
echo "Docker 이미지 빌드 중..."
docker build -t dynamic-dashboard:latest .

# 로그인 정보 입력
echo "Docker Hub 계정으로 로그인하세요:"
docker login

# 이미지 태그 설정
echo "Docker 이미지에 태그 설정 중..."
docker tag dynamic-dashboard:latest YOUR_DOCKERHUB_USERNAME/dynamic-dashboard:latest

# Docker Hub에 이미지 푸시
echo "Docker Hub에 이미지 푸시 중..."
docker push YOUR_DOCKERHUB_USERNAME/dynamic-dashboard:latest

echo "배포 완료! 이제 클라우드 서비스에서 이 이미지를 사용할 수 있습니다."
echo "예: docker run -d -p 8501:8501 --env-file .env YOUR_DOCKERHUB_USERNAME/dynamic-dashboard:latest" 