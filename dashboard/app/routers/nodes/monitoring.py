# app/routers/nodes/monitoring.py
from fastapi import APIRouter, HTTPException
from app.services.node_service import NodeService

router = APIRouter(prefix="/api/nodes", tags=["nodes"])

@router.get("/status")
def get_nodes_status():
    """모든 서버의 연결 상태 확인"""
    try:
        return NodeService.get_nodes_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 상태 조회 실패: {str(e)}")

@router.post("/{node_id}/test")
def test_connection(node_id: str):
    """서버 연결 테스트"""
    try:
        return NodeService.test_connection(node_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

