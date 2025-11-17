# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import BASE_DIR
from app.routers import nodes, containers
from app.services.server_service import load_servers, DOCKER_HOSTS
from app.services.node_service import NodeService

app = FastAPI(title="FL Container Dashboard")

# 템플릿 / 정적 파일 설정
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 라우터 등록
app.include_router(nodes.router)
app.include_router(containers.router)

# 앱 시작 시 서버 설정 로드
DOCKER_HOSTS.update(load_servers())

@app.get("/")
def index(request: Request):
    """초기 페이지 렌더링"""
    nodes = NodeService.get_all_nodes()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "nodes": nodes,
        },
    )
