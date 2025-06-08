# 실행 방법

## 1. Poetry lock 파일 최신화 (처음 설정 시)

poetry lock

## 2. Docker 컨테이너 빌드 및 실행

docker-compose up --build

> 컨테이너가 시작되면 자동으로 Django ORM 마이그레이션이 적용되고,  
> FastAPI 앱이 http://localhost:8000 에서 실행됩니다.

## 3. FastAPI 문서 접속

- Swagger UI: http://localhost:8000/docs  
