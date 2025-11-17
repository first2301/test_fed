# app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import docker
import yaml

app = FastAPI(title="FL Container Dashboard")

# 템플릿 / 정적 파일 설정
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)
SERVERS_FILE = CONFIG_DIR / "servers.yaml"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# 서버 설정 파일 관리 함수
def load_servers():
    """서버 설정 로드"""
    if SERVERS_FILE.exists():
        try:
            with open(SERVERS_FILE, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                # YAML이 None을 반환할 수 있음
                return data if data is not None else {}
        except (yaml.YAMLError, IOError) as e:
            print(f"서버 설정 파일 로드 오류: {e}")
            # 기본값 반환
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
        # 기본값 생성
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


# 앱 시작 시 서버 설정 로드
DOCKER_HOSTS = load_servers()


def get_docker_client(node_id: str) -> docker.DockerClient:
    if node_id not in DOCKER_HOSTS:
        raise HTTPException(status_code=404, detail="Unknown node")

    cfg = DOCKER_HOSTS[node_id]
    return docker.DockerClient(base_url=cfg["base_url"])


@app.get("/")
def index(request: Request):
    # 초기 페이지 렌더링 (JS가 /api 호출해서 데이터 채움)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "nodes": [
                {"id": node_id, "label": info["label"]}
                for node_id, info in DOCKER_HOSTS.items()
            ],
        },
    )


@app.get("/api/nodes")
def list_nodes():
    """서버 목록 조회"""
    # clear() 후 update()로 전체 교체 - 삭제된 항목도 제거됨
    latest_servers = load_servers()
    DOCKER_HOSTS.clear()
    DOCKER_HOSTS.update(latest_servers)
    return [
        {"id": node_id, "label": info.get("label", node_id)}
        for node_id, info in DOCKER_HOSTS.items()
    ]


@app.get("/api/nodes/status")
def get_nodes_status():
    """모든 서버의 연결 상태 확인"""
    try:
        # 최신 설정 로드 (전체 교체하여 삭제된 서버도 제거)
        try:
            latest_servers = load_servers()
            # clear() 후 update()로 전체 교체 - 삭제된 항목도 제거됨
            DOCKER_HOSTS.clear()
            DOCKER_HOSTS.update(latest_servers)
        except Exception as e:
            print(f"서버 설정 로드 오류: {e}")
            # 기존 설정 유지하거나 기본값 사용
            if not DOCKER_HOSTS:
                latest_servers = load_servers()
                DOCKER_HOSTS.clear()
                DOCKER_HOSTS.update(latest_servers)
        
        status_list = []
        for node_id, info in DOCKER_HOSTS.items():
            try:
                client = docker.DockerClient(base_url=info["base_url"])
                client.ping()  # 연결 테스트
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
    except Exception as e:
        # 전체 함수 레벨 에러 처리
        print(f"서버 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"서버 상태 조회 실패: {str(e)}")


@app.get("/api/nodes/{node_id}")
def get_node(node_id: str):
    """서버 상세 정보 조회"""
    # clear() 후 update()로 전체 교체 - 삭제된 항목도 제거됨
    latest_servers = load_servers()
    DOCKER_HOSTS.clear()
    DOCKER_HOSTS.update(latest_servers)
    
    if node_id not in DOCKER_HOSTS:
        raise HTTPException(status_code=404, detail="서버를 찾을 수 없습니다")
    
    info = DOCKER_HOSTS[node_id]
    return {
        "id": node_id,
        "label": info.get("label", node_id),
        "base_url": info.get("base_url", ""),
        "type": info.get("type", "remote"),
        "role": info.get("role", "client"),
        "tls": info.get("tls", False)
    }


class ServerConfig(BaseModel):
    id: str
    label: str
    base_url: str
    type: str = "remote"
    role: str = "client"  # "client" 또는 "central"
    tls: bool = False


@app.post("/api/nodes")
def add_node(server: ServerConfig):
    """서버 추가"""
    servers = load_servers()
    
    # ID 중복 확인
    if server.id in servers:
        raise HTTPException(status_code=400, detail=f"서버 ID '{server.id}'가 이미 존재합니다")
    
    # 서버 정보 추가
    servers[server.id] = {
        "base_url": server.base_url,
        "label": server.label,
        "type": server.type,
        "role": server.role,
        "tls": server.tls
    }
    
    save_servers(servers)
    # clear() 후 update()로 전체 교체 - 일관성 유지
    DOCKER_HOSTS.clear()
    DOCKER_HOSTS.update(servers)
    
    return {"ok": True, "message": f"서버 '{server.label}'가 추가되었습니다"}


@app.put("/api/nodes/{node_id}")
def update_node(node_id: str, server: ServerConfig):
    """서버 수정"""
    servers = load_servers()
    
    if node_id not in servers:
        raise HTTPException(status_code=404, detail="서버를 찾을 수 없습니다")
    
    # 서버 정보 업데이트
    servers[node_id] = {
        "base_url": server.base_url,
        "label": server.label,
        "type": server.type,
        "role": server.role,
        "tls": server.tls
    }
    
    # ID가 변경된 경우
    if server.id != node_id:
        if server.id in servers:
            raise HTTPException(status_code=400, detail=f"서버 ID '{server.id}'가 이미 존재합니다")
        servers[server.id] = servers.pop(node_id)
    
    save_servers(servers)
    # clear() 후 update()로 전체 교체 - 일관성 유지
    DOCKER_HOSTS.clear()
    DOCKER_HOSTS.update(servers)
    
    return {"ok": True, "message": f"서버 '{server.label}'가 수정되었습니다"}


@app.delete("/api/nodes/{node_id}")
def delete_node(node_id: str):
    """서버 삭제"""
    servers = load_servers()
    
    if node_id not in servers:
        raise HTTPException(status_code=404, detail="서버를 찾을 수 없습니다")
    
    # 중앙 서버는 삭제 불가
    if node_id == "main":
        raise HTTPException(status_code=400, detail="중앙 서버는 삭제할 수 없습니다")
    
    label = servers[node_id].get("label", node_id)
    del servers[node_id]
    
    save_servers(servers)
    # clear() 후 update()로 전체 교체 - 삭제된 항목도 제거됨
    DOCKER_HOSTS.clear()
    DOCKER_HOSTS.update(servers)
    
    return {"ok": True, "message": f"서버 '{label}'가 삭제되었습니다"}


@app.post("/api/nodes/{node_id}/test")
def test_connection(node_id: str):
    """서버 연결 테스트"""
    # clear() 후 update()로 전체 교체 - 삭제된 항목도 제거됨
    latest_servers = load_servers()
    DOCKER_HOSTS.clear()
    DOCKER_HOSTS.update(latest_servers)
    
    if node_id not in DOCKER_HOSTS:
        raise HTTPException(status_code=404, detail="서버를 찾을 수 없습니다")
    
    info = DOCKER_HOSTS[node_id]
    try:
        client = docker.DockerClient(base_url=info["base_url"])
        client.ping()  # 연결 테스트
        
        # 추가 정보 가져오기
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


class ContainerAction(BaseModel):
    node_id: str
    container_id: str


@app.get("/api/containers")
def list_containers(node_id: str, all: bool = True):
    """
    특정 노드의 컨테이너 목록 조회
    """
    client = get_docker_client(node_id)
    containers = client.containers.list(all=all)

    result = []
    for c in containers:
        # 포트 정보 간단 정리
        ports = []
        if c.ports:
            for k, v in c.ports.items():
                if v:
                    for m in v:
                        host = m.get("HostIp")
                        port = m.get("HostPort")
                        ports.append(f"{host}:{port}->{k}")
                else:
                    ports.append(k)

        result.append(
            {
                "id": c.short_id,
                "name": c.name,
                "image": ", ".join(c.image.tags) if c.image.tags else c.image.id,
                "status": c.status,
                "ports": ", ".join(ports),
            }
        )
    return result


@app.post("/api/containers/start")
def start_container(action: ContainerAction):
    client = get_docker_client(action.node_id)
    container = client.containers.get(action.container_id)
    container.start()
    return {"ok": True}


@app.post("/api/containers/stop")
def stop_container(action: ContainerAction):
    client = get_docker_client(action.node_id)
    container = client.containers.get(action.container_id)
    container.stop()
    return {"ok": True}


@app.post("/api/containers/restart")
def restart_container(action: ContainerAction):
    client = get_docker_client(action.node_id)
    container = client.containers.get(action.container_id)
    container.restart()
    return {"ok": True}
