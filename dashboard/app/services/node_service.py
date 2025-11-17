# app/services/node_service.py
from datetime import datetime
from typing import List, Dict
import docker
from app.services.server_service import (
    load_servers, 
    save_servers, 
    DOCKER_HOSTS,
    refresh_docker_hosts
)
from app.models import ServerConfig

class NodeService:
    """노드 관련 비즈니스 로직"""
    
    @staticmethod
    def get_all_nodes() -> List[Dict]:
        """모든 노드 목록 조회"""
        refresh_docker_hosts()
        return [
            {"id": node_id, "label": info.get("label", node_id)}
            for node_id, info in DOCKER_HOSTS.items()
        ]
    
    @staticmethod
    def get_node(node_id: str) -> Dict:
        """노드 상세 정보 조회"""
        refresh_docker_hosts()
        if node_id not in DOCKER_HOSTS:
            raise ValueError(f"서버를 찾을 수 없습니다: {node_id}")
        
        info = DOCKER_HOSTS[node_id]
        return {
            "id": node_id,
            "label": info.get("label", node_id),
            "base_url": info.get("base_url", ""),
            "type": info.get("type", "remote"),
            "role": info.get("role", "client"),
            "tls": info.get("tls", False)
        }
    
    @staticmethod
    def add_node(server: ServerConfig) -> Dict:
        """노드 추가"""
        servers = load_servers()
        
        if server.id in servers:
            raise ValueError(f"서버 ID '{server.id}'가 이미 존재합니다")
        
        servers[server.id] = {
            "base_url": server.base_url,
            "label": server.label,
            "type": server.type,
            "role": server.role,
            "tls": server.tls
        }
        
        save_servers(servers)
        DOCKER_HOSTS.update(servers)
        
        return {"ok": True, "message": f"서버 '{server.label}'가 추가되었습니다"}
    
    @staticmethod
    def update_node(node_id: str, server: ServerConfig) -> Dict:
        """노드 수정"""
        servers = load_servers()
        
        if node_id not in servers:
            raise ValueError(f"서버를 찾을 수 없습니다: {node_id}")
        
        servers[node_id] = {
            "base_url": server.base_url,
            "label": server.label,
            "type": server.type,
            "role": server.role,
            "tls": server.tls
        }
        
        if server.id != node_id:
            if server.id in servers:
                raise ValueError(f"서버 ID '{server.id}'가 이미 존재합니다")
            servers[server.id] = servers.pop(node_id)
        
        save_servers(servers)
        DOCKER_HOSTS.update(servers)
        
        return {"ok": True, "message": f"서버 '{server.label}'가 수정되었습니다"}
    
    @staticmethod
    def delete_node(node_id: str) -> Dict:
        """노드 삭제"""
        servers = load_servers()
        
        if node_id not in servers:
            raise ValueError(f"서버를 찾을 수 없습니다: {node_id}")
        
        if node_id == "main":
            raise ValueError("중앙 서버는 삭제할 수 없습니다")
        
        label = servers[node_id].get("label", node_id)
        del servers[node_id]
        
        save_servers(servers)
        DOCKER_HOSTS.update(servers)
        
        return {"ok": True, "message": f"서버 '{label}'가 삭제되었습니다"}
    
    @staticmethod
    def get_nodes_status() -> List[Dict]:
        """모든 노드의 연결 상태 확인"""
        try:
            refresh_docker_hosts()
        except Exception as e:
            print(f"서버 설정 로드 오류: {e}")
            if not DOCKER_HOSTS:
                refresh_docker_hosts()
        
        status_list = []
        for node_id, info in DOCKER_HOSTS.items():
            try:
                client = docker.DockerClient(base_url=info["base_url"])
                client.ping()
                status_list.append({
                    "id": node_id,
                    "label": info.get("label", node_id),
                    "status": "online",
                    "type": info.get("type", "unknown"),
                    "role": info.get("role", "client"),
                    "base_url": info.get("base_url", ""),
                    "last_check": datetime.now().isoformat()
                })
            except Exception as e:
                status_list.append({
                    "id": node_id,
                    "label": info.get("label", node_id),
                    "status": "offline",
                    "type": info.get("type", "unknown"),
                    "role": info.get("role", "client"),
                    "base_url": info.get("base_url", ""),
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                })
        return status_list
    
    @staticmethod
    def test_connection(node_id: str) -> Dict:
        """노드 연결 테스트"""
        refresh_docker_hosts()
        
        if node_id not in DOCKER_HOSTS:
            raise ValueError(f"서버를 찾을 수 없습니다: {node_id}")
        
        info = DOCKER_HOSTS[node_id]
        try:
            client = docker.DockerClient(base_url=info["base_url"])
            client.ping()
            
            version = client.version()
            return {
                "ok": True,
                "status": "online",
                "version": version.get("Version", "unknown"),
                "api_version": version.get("ApiVersion", "unknown")
            }
        except Exception as e:
            return {
                "ok": False,
                "status": "offline",
                "error": str(e)
            }

