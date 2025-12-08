#!/bin/bash

# 1. SSH 데몬 시작
service ssh start

# 2. Docker 데몬 시작 (백그라운드)
# - host 설정을 통해 내부 socket과 외부 TCP 포트(2375) 모두 엽니다.
dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 &

# 3. Docker가 완전히 켜질 때까지 잠시 대기
echo "Waiting for Docker daemon to start..."
while (! docker stats --no-stream > /dev/null 2>&1); do
  # Docker가 아직 안 켜졌으면 1초 대기
  sleep 1
done
echo "Docker daemon started!"

# 4. MinIO 실행 여부 확인 (환경 변수로 제어)
if [ "$RUN_MINIO" = "true" ]; then
  echo "Starting MinIO server as a container inside this silo..."
  
  # MinIO 포트 설정 (환경 변수로 제어 가능, 기본값: 9000, 9001)
  MINIO_API_PORT=${MINIO_API_PORT:-9000}
  MINIO_CONSOLE_PORT=${MINIO_CONSOLE_PORT:-9001}
  
  # MinIO 컨테이너가 이미 실행 중인지 확인
  if ! docker ps -a | grep -q minio-server; then
    # MinIO 이미지 pull (없는 경우)
    echo "Pulling MinIO image..."
    docker pull minio/minio:latest || echo "MinIO image pull failed or already exists"
    
    # MinIO를 silo 컨테이너 내부에서 Docker 컨테이너로 실행
    # 포트 매핑: silo 컨테이너 포트 -> MinIO 컨테이너 포트
    docker run -d \
      --name minio-server \
      --restart=unless-stopped \
      --memory="512m" \
      --memory-swap="512m" \
      -p ${MINIO_API_PORT}:9000 \
      -p ${MINIO_CONSOLE_PORT}:9001 \
      -e MINIO_ROOT_USER=${MINIO_ROOT_USER:-minio} \
      -e MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-minio} \
      -v /data:/data \
      minio/minio:latest \
      server /data --console-address ":9001"
    
    echo "MinIO container started inside silo!"
    echo "API: http://localhost:${MINIO_API_PORT}"
    echo "Console: http://localhost:${MINIO_CONSOLE_PORT}"
  elif ! docker ps | grep -q minio-server; then
    # 컨테이너가 있지만 중지된 경우 재시작
    echo "Restarting existing MinIO container..."
    docker start minio-server
    echo "MinIO container restarted!"
  else
    echo "MinIO container is already running"
  fi
fi

# 5. 컨테이너가 꺼지지 않도록 무한 대기 (Tail logs)
tail -f /dev/null