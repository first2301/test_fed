# app/routers/nodes/__init__.py
from fastapi import APIRouter
from app.routers.nodes import crud, monitoring

router = APIRouter()

# CRUD 라우터 등록
router.include_router(crud.router)

# 모니터링 라우터 등록
router.include_router(monitoring.router)

