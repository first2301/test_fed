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
  
  # MinIO 데이터 디렉토리 준비 및 권한 설정
  echo "Preparing MinIO data directory..."
  mkdir -p /data
  chmod 755 /data
  
  # MinIO 컨테이너 시작 함수
  start_minio() {
    # 기존 컨테이너가 있으면 제거
    if docker ps -a | grep -q minio-server; then
      echo "Removing existing MinIO container..."
      docker rm -f minio-server 2>/dev/null || true
      sleep 1
    fi
    
    # MinIO 이미지 pull (없는 경우)
    echo "Pulling MinIO image..."
    docker pull minio/minio:latest || echo "MinIO image pull failed or already exists"
    
    # MinIO를 silo 컨테이너 내부에서 Docker 컨테이너로 실행
    # 포트 매핑: silo 컨테이너 포트(9000, 9001) -> MinIO 컨테이너 포트(9000, 9001)
    # compose.silo.yaml에서 호스트 포트로 매핑됨
    docker run -d \
      --name minio-server \
      --restart=unless-stopped \
      --memory="512m" \
      --memory-swap="512m" \
      -p 9000:9000 \
      -p 9001:9001 \
      -e MINIO_ROOT_USER=${MINIO_ROOT_USER:-minio} \
      -e MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-minio1234} \
      -v /data:/data \
      minio/minio:latest \
      server /data --console-address ":9001"
    
    echo "MinIO container started!"
  }
  
  # MinIO 컨테이너 상태 확인 및 시작
  if ! docker ps | grep -q minio-server; then
    if docker ps -a | grep -q minio-server; then
      # 컨테이너가 있지만 중지된 경우 - 종료 이유 확인
      echo "MinIO container exists but is stopped. Checking logs..."
      docker logs --tail 50 minio-server 2>&1 || true
      echo "Removing stopped container and recreating..."
      docker rm -f minio-server 2>/dev/null || true
      sleep 1
    fi
    start_minio
    
    # 컨테이너가 정상적으로 시작되었는지 확인 (최대 30초 대기)
    echo "Waiting for MinIO to be ready..."
    MAX_WAIT=30
    for i in $(seq 1 $MAX_WAIT); do
      if docker ps | grep -q minio-server; then
        # MinIO가 응답하는지 확인 (간단한 HTTP 체크)
        if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
          echo "MinIO is ready!"
          break
        fi
        sleep 1
      else
        echo "MinIO container stopped unexpectedly (attempt $i/$MAX_WAIT). Attempting to restart..."
        start_minio
        sleep 2
      fi
    done
  else
    echo "MinIO container is already running"
  fi
  
  # 최종 상태 확인 및 로그 출력
  if docker ps | grep -q minio-server; then
    echo "MinIO container status:"
    docker ps | grep minio-server
    echo "API: http://localhost:${MINIO_API_PORT}"
    echo "Console: http://localhost:${MINIO_CONSOLE_PORT}"
  else
    echo "WARNING: MinIO container failed to start. Checking logs..."
    docker logs --tail 100 minio-server 2>&1 || true
    echo "Attempting final restart..."
    start_minio
    sleep 3
    if docker ps | grep -q minio-server; then
      echo "MinIO container restarted successfully!"
    else
      echo "ERROR: MinIO container failed to start. Please check logs manually."
    fi
  fi
fi

# 5. 컨테이너가 꺼지지 않도록 무한 대기 (Tail logs)
tail -f /dev/null