"""
데이터 병합 모듈 (Cross, Vertical, Horizontal)
"""
from typing import Any, Dict, List


def cross_join(
    data_a: List[Dict[str, Any]],
    data_b: List[Dict[str, Any]],
    prefix_a: str = "a_",
    prefix_b: str = "b_"
) -> List[Dict[str, Any]]:
    """
    Cross Join (핵심 로직)
    두 데이터셋의 모든 조합을 생성
    
    Args:
        data_a: 첫 번째 데이터 리스트
        data_b: 두 번째 데이터 리스트
        prefix_a: 첫 번째 데이터의 키에 붙일 접두사
        prefix_b: 두 번째 데이터의 키에 붙일 접두사
    
    Returns:
        모든 조합의 데이터 리스트
    """
    result = []
    for row_a in data_a:
        for row_b in data_b:
            combined = {}
            # 첫 번째 데이터의 키에 접두사 추가
            for key, value in row_a.items():
                combined[f"{prefix_a}{key}"] = value
            # 두 번째 데이터의 키에 접두사 추가
            for key, value in row_b.items():
                combined[f"{prefix_b}{key}"] = value
            result.append(combined)
    return result


def vertical_merge(
    data_a: List[Dict[str, Any]],
    data_b: List[Dict[str, Any]],
    ensure_same_keys: bool = True
) -> List[Dict[str, Any]]:
    """
    Vertical Merge (핵심 로직)
    두 데이터셋을 위아래로 합치기 (행 추가)
    
    Args:
        data_a: 첫 번째 데이터 리스트
        data_b: 두 번째 데이터 리스트
        ensure_same_keys: 모든 행이 동일한 키를 가져야 하는지 여부
    
    Returns:
        합쳐진 데이터 리스트
    """
    if not data_a and not data_b:
        return []
    
    if ensure_same_keys:
        # 모든 키가 동일한지 확인
        if data_a and data_b:
            keys_a = set(data_a[0].keys())
            keys_b = set(data_b[0].keys())
            if keys_a != keys_b:
                raise ValueError(
                    f"Key mismatch: data_a has {keys_a}, data_b has {keys_b}. "
                    "Set ensure_same_keys=False to allow different keys."
                )
    
    # 단순히 두 리스트를 합치기
    return data_a + data_b


def horizontal_merge(
    data_a: List[Dict[str, Any]],
    data_b: List[Dict[str, Any]],
    id_key: str,
    how: str = "inner"
) -> List[Dict[str, Any]]:
    """
    Horizontal Merge (핵심 로직)
    두 데이터셋을 좌우로 합치기 (공통 ID 기준)
    
    Args:
        data_a: 첫 번째 데이터 리스트
        data_b: 두 번째 데이터 리스트
        id_key: 공통 ID 키
        how: 병합 방법 ('inner', 'left', 'right', 'outer')
    
    Returns:
        병합된 데이터 리스트
    """
    if how not in ["inner", "left", "right", "outer"]:
        raise ValueError(f"Invalid 'how' parameter: {how}. Must be one of: inner, left, right, outer")
    
    # data_b를 ID를 키로 하는 딕셔너리로 변환
    dict_b = {row[id_key]: row for row in data_b if id_key in row}
    
    result = []
    
    if how == "inner":
        # 양쪽 모두에 있는 ID만
        for row_a in data_a:
            if id_key in row_a and row_a[id_key] in dict_b:
                merged = {**row_a, **dict_b[row_a[id_key]]}
                # ID 키는 하나만 유지
                if id_key in merged:
                    merged[id_key] = row_a[id_key]
                result.append(merged)
    
    elif how == "left":
        # data_a의 모든 ID (data_b에 없으면 None으로 채움)
        for row_a in data_a:
            if id_key in row_a:
                if row_a[id_key] in dict_b:
                    merged = {**row_a, **dict_b[row_a[id_key]]}
                    merged[id_key] = row_a[id_key]
                else:
                    merged = row_a.copy()
                result.append(merged)
    
    elif how == "right":
        # data_b의 모든 ID (data_a에 없으면 None으로 채움)
        # data_a를 딕셔너리로 변환
        dict_a = {row[id_key]: row for row in data_a if id_key in row}
        for id_val, row_b in dict_b.items():
            if id_val in dict_a:
                merged = {**dict_a[id_val], **row_b}
                merged[id_key] = id_val
            else:
                merged = row_b.copy()
            result.append(merged)
    
    elif how == "outer":
        # 양쪽 모든 ID
        all_ids = set()
        dict_a = {row[id_key]: row for row in data_a if id_key in row}
        for row in data_a:
            if id_key in row:
                all_ids.add(row[id_key])
        for row in data_b:
            if id_key in row:
                all_ids.add(row[id_key])
        
        for id_val in all_ids:
            merged = {}
            if id_val in dict_a:
                merged.update(dict_a[id_val])
            if id_val in dict_b:
                merged.update(dict_b[id_val])
            merged[id_key] = id_val
            result.append(merged)
    
    return result

