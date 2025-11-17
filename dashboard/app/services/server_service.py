# app/services/server_service.py
import yaml
from fastapi import HTTPException
from app.config import SERVERS_FILE

# 전역 변수 (메모리 캐시)
DOCKER_HOSTS = {}

def load_servers():
    """서버 설정 로드"""
    if SERVERS_FILE.exists():
        try:
            with open(SERVERS_FILE, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except (yaml.YAMLError, IOError) as e:
            print(f"서버 설정 파일 로드 오류: {e}")
            default = {
                "main": {
                    "base_url": "unix://var/run/docker.sock",
                    "label": "중앙 서버",
                    "type": "local",
                    "role": "central"
                }
            }
            save_servers(default)
            return default
    else:
        default = {
            "main": {
                "base_url": "unix://var/run/docker.sock",
                "label": "중앙 서버",
                "type": "local",
                "role": "central"
            }
        }
        save_servers(default)
        return default

def save_servers(servers: dict):
    """서버 설정 저장"""
    try:
        with open(SERVERS_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(servers, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    except IOError as e:
        print(f"서버 설정 파일 저장 오류: {e}")
        raise HTTPException(status_code=500, detail=f"서버 설정 저장 실패: {e}")

def refresh_docker_hosts():
    """파일에서 최신 설정 로드하여 메모리 업데이트"""
    servers = load_servers()
    DOCKER_HOSTS.update(servers)
    return DOCKER_HOSTS

