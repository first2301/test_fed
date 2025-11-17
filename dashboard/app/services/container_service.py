# app/services/container_service.py
from typing import List, Dict
from app.services.docker_service import get_docker_client

class ContainerService:
    """컨테이너 관련 비즈니스 로직"""
    
    @staticmethod
    def list_containers(node_id: str, all: bool = True) -> List[Dict]:
        """컨테이너 목록 조회"""
        client = get_docker_client(node_id)
        containers = client.containers.list(all=all)
        
        result = []
        for c in containers:
            ports = ContainerService._parse_ports(c.ports)
            
            result.append({
                "id": c.short_id,
                "name": c.name,
                "image": ", ".join(c.image.tags) if c.image.tags else c.image.id,
                "status": c.status,
                "ports": ", ".join(ports),
            })
        return result
    
    @staticmethod
    def _parse_ports(ports: dict) -> List[str]:
        """포트 정보 파싱"""
        port_list = []
        if ports:
            for k, v in ports.items():
                if v:
                    for m in v:
                        host = m.get("HostIp")
                        port = m.get("HostPort")
                        port_list.append(f"{host}:{port}->{k}")
                else:
                    port_list.append(k)
        return port_list
    
    @staticmethod
    def start_container(node_id: str, container_id: str) -> Dict:
        """컨테이너 시작"""
        client = get_docker_client(node_id)
        container = client.containers.get(container_id)
        container.start()
        return {"ok": True}
    
    @staticmethod
    def stop_container(node_id: str, container_id: str) -> Dict:
        """컨테이너 중지"""
        client = get_docker_client(node_id)
        container = client.containers.get(container_id)
        container.stop()
        return {"ok": True}
    
    @staticmethod
    def restart_container(node_id: str, container_id: str) -> Dict:
        """컨테이너 재시작"""
        client = get_docker_client(node_id)
        container = client.containers.get(container_id)
        container.restart()
        return {"ok": True}

