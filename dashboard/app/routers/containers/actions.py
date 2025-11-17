# app/routers/containers/actions.py
from fastapi import APIRouter, HTTPException
from app.models import ContainerAction
from app.services.container_service import ContainerService

router = APIRouter(prefix="/api/containers", tags=["containers"])

@router.post("/start")
def start_container(action: ContainerAction):
    """컨테이너 시작"""
    try:
        return ContainerService.start_container(action.node_id, action.container_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"컨테이너 시작 실패: {str(e)}")

@router.post("/stop")
def stop_container(action: ContainerAction):
    """컨테이너 중지"""
    try:
        return ContainerService.stop_container(action.node_id, action.container_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"컨테이너 중지 실패: {str(e)}")

@router.post("/restart")
def restart_container(action: ContainerAction):
    """컨테이너 재시작"""
    try:
        return ContainerService.restart_container(action.node_id, action.container_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"컨테이너 재시작 실패: {str(e)}")

