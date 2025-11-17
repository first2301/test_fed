# app/routers/nodes/crud.py
from fastapi import APIRouter, HTTPException
from app.models import ServerConfig
from app.services.node_service import NodeService

router = APIRouter(prefix="/api/nodes", tags=["nodes"])

@router.get("")
def list_nodes():
    """서버 목록 조회"""
    return NodeService.get_all_nodes()

@router.get("/{node_id}")
def get_node(node_id: str):
    """서버 상세 정보 조회"""
    try:
        return NodeService.get_node(node_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("")
def add_node(server: ServerConfig):
    """서버 추가"""
    try:
        return NodeService.add_node(server)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{node_id}")
def update_node(node_id: str, server: ServerConfig):
    """서버 수정"""
    try:
        return NodeService.update_node(node_id, server)
    except ValueError as e:
        if "이미 존재합니다" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{node_id}")
def delete_node(node_id: str):
    """서버 삭제"""
    try:
        return NodeService.delete_node(node_id)
    except ValueError as e:
        if "삭제할 수 없습니다" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))

