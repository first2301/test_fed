"""
데이터 연산 모듈 (교집합, 필터링)
"""
from typing import Any, Dict, List


def compute_intersection(ids_a: List[str], ids_b: List[str]) -> List[str]:
    """
    교집합 계산 (핵심 로직)
    
    Args:
        ids_a: 첫 번째 ID 리스트
        ids_b: 두 번째 ID 리스트
    
    Returns:
        교집합 ID 리스트
    """
    set_a = set(ids_a)
    set_b = set(ids_b)
    return sorted(list(set_a & set_b))  # 정렬하여 일관성 유지


def filter_by_ids(
    data: List[Dict[str, Any]],
    ids: List[str],
    id_key: str
) -> List[Dict[str, Any]]:
    """
    데이터 필터링 (핵심 로직)
    교집합 ID에 해당하는 데이터만 반환
    
    Args:
        data: 필터링할 데이터 리스트
        ids: 필터링할 ID 리스트
        id_key: ID를 나타내는 키
    
    Returns:
        필터링된 데이터 리스트
    """
    id_set = set(ids)
    return [row for row in data if row.get(id_key) in id_set]

