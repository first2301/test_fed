# app/routers/containers/query.py
from fastapi import APIRouter, HTTPException
from app.services.container_service import ContainerService

router = APIRouter(prefix="/api/containers", tags=["containers"])

@router.get("")
def list_containers(node_id: str, all: bool = True):
    """특정 노드의 컨테이너 목록 조회"""
    try:
        return ContainerService.list_containers(node_id, all)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"컨테이너 목록 조회 실패: {str(e)}")

