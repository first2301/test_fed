# app/services/docker_service.py
import docker
from fastapi import HTTPException
from app.services.server_service import DOCKER_HOSTS

def get_docker_client(node_id: str) -> docker.DockerClient:
    """노드 ID로 Docker 클라이언트 생성"""
    if node_id not in DOCKER_HOSTS:
        raise HTTPException(status_code=404, detail="Unknown node")
    
    cfg = DOCKER_HOSTS[node_id]
    return docker.DockerClient(base_url=cfg["base_url"])

