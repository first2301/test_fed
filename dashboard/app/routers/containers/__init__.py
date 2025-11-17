# app/routers/containers/__init__.py
from fastapi import APIRouter
from app.routers.containers import query, actions

router = APIRouter()

# 조회 라우터 등록
router.include_router(query.router)

# 액션 라우터 등록
router.include_router(actions.router)

