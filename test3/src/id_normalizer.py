"""
ID 정규화 모듈
"""
import hashlib


def normalize_id(id_value: str, hash_it: bool = True) -> str:
    """
    ID 정규화 (핵심 로직)
    
    Args:
        id_value: 정규화할 ID 값
        hash_it: SHA-256 해싱 여부
    
    Returns:
        정규화된 ID 값
    """
    # 소문자 변환
    normalized = id_value.lower()
    
    # 공백 제거
    normalized = normalized.strip()
    
    # 특수문자 제거 (알파벳과 숫자만)
    normalized = ''.join(c for c in normalized if c.isalnum())
    
    # 해싱
    if hash_it:
        normalized = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    return normalized

