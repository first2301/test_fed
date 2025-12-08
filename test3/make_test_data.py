"""
src 모듈 테스트 데이터셋 생성
"""
import csv
from pathlib import Path
from typing import List, Dict, Any


def make_id_normalize_test_data() -> List[str]:
    """
    ID 정규화 테스트용 데이터 생성
    
    Returns:
        다양한 형식의 ID 리스트
    """
    return [
        "P-001",
        "P-002",
        "P-003",
        "P-004",
        "P-005",
        "P-001 ",  # 공백 포함
        "P-002-EXTRA",  # 특수문자 포함
        "p-003",  # 소문자
        "P_004",  # 언더스코어
        "P 005",  # 공백 포함
    ]


def make_intersection_test_data() -> tuple[List[str], List[str]]:
    """
    교집합 계산 테스트용 데이터 생성
    
    Returns:
        (ids_a, ids_b) 튜플
    """
    ids_a = ["P-001", "P-002", "P-003", "P-004", "P-005"]
    ids_b = ["P-003", "P-004", "P-005", "P-006", "P-007"]
    return ids_a, ids_b


def make_filter_test_data() -> tuple[List[Dict[str, Any]], List[str]]:
    """
    데이터 필터링 테스트용 데이터 생성
    
    Returns:
        (data, ids) 튜플
    """
    data = [
        {"id": "P-001", "name": "Alice", "age": 25},
        {"id": "P-002", "name": "Bob", "age": 30},
        {"id": "P-003", "name": "Charlie", "age": 35},
        {"id": "P-004", "name": "David", "age": 40},
        {"id": "P-005", "name": "Eve", "age": 45},
    ]
    ids = ["P-001", "P-003", "P-005"]
    return data, ids


def make_cross_join_test_data() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Cross Join 테스트용 데이터 생성
    
    Returns:
        (data_a, data_b) 튜플
    """
    data_a = [
        {"id": "P-001", "name": "Alice"},
        {"id": "P-002", "name": "Bob"},
    ]
    data_b = [
        {"id": "D-001", "diagnosis": "A"},
        {"id": "D-002", "diagnosis": "B"},
        {"id": "D-003", "diagnosis": "C"},
    ]
    return data_a, data_b


def make_vertical_merge_test_data() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Vertical Merge 테스트용 데이터 생성
    
    Returns:
        (data_a, data_b) 튜플 - 동일한 키 구조
    """
    data_a = [
        {"id": "P-001", "value": 10},
        {"id": "P-002", "value": 20},
    ]
    data_b = [
        {"id": "P-003", "value": 30},
        {"id": "P-004", "value": 40},
    ]
    return data_a, data_b


def make_horizontal_merge_test_data() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Horizontal Merge 테스트용 데이터 생성
    
    Returns:
        (data_a, data_b) 튜플 - 공통 ID 포함
    """
    data_a = [
        {"id": "P-001", "name": "Alice", "age": 25},
        {"id": "P-002", "name": "Bob", "age": 30},
        {"id": "P-003", "name": "Charlie", "age": 35},
    ]
    data_b = [
        {"id": "P-002", "diagnosis": "A", "cost": 1000},
        {"id": "P-003", "diagnosis": "B", "cost": 2000},
        {"id": "P-004", "diagnosis": "C", "cost": 3000},
    ]
    return data_a, data_b


def make_institution_data() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Federated Learning 시나리오용 기관 데이터 생성
    
    Returns:
        (institution_a, institution_b) 튜플
    """
    institution_a = [
        {"id": "P-001", "name": "Alice", "age": 25, "gender": "F"},
        {"id": "P-002", "name": "Bob", "age": 30, "gender": "M"},
        {"id": "P-003", "name": "Charlie", "age": 35, "gender": "M"},
        {"id": "P-004", "name": "David", "age": 40, "gender": "M"},
        {"id": "P-005", "name": "Eve", "age": 45, "gender": "F"},
    ]
    
    institution_b = [
        {"id": "P-003", "diagnosis": "A", "cost": 1000, "date": "2024-01-01"},
        {"id": "P-004", "diagnosis": "B", "cost": 2000, "date": "2024-01-02"},
        {"id": "P-005", "diagnosis": "C", "cost": 3000, "date": "2024-01-03"},
        {"id": "P-006", "diagnosis": "D", "cost": 4000, "date": "2024-01-04"},
        {"id": "P-007", "diagnosis": "E", "cost": 5000, "date": "2024-01-05"},
    ]
    
    return institution_a, institution_b


def make_large_dataset(size: int = 100) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    대용량 테스트 데이터셋 생성
    
    Args:
        size: 생성할 데이터 개수
    
    Returns:
        (data_a, data_b) 튜플
    """
    data_a = [
        {"id": f"P-{i:03d}", "name": f"Person_{i}", "value": i * 10}
        for i in range(1, size + 1)
    ]
    
    data_b = [
        {"id": f"P-{i:03d}", "score": i * 5, "category": chr(65 + (i % 26))}
        for i in range(size // 2, size + size // 2)
    ]
    
    return data_a, data_b


def ensure_data_directory() -> Path:
    """
    data 디렉토리 생성 및 경로 반환
    
    Returns:
        data 디렉토리 Path 객체
    """
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir


def save_data_to_csv(
    data: List[Dict[str, Any]],
    filepath: str,
    encoding: str = "utf-8-sig"  # Excel 호환을 위한 BOM 포함
) -> None:
    """
    딕셔너리 리스트를 CSV 파일로 저장
    
    Args:
        data: 저장할 데이터 리스트
        filepath: 저장할 파일 경로
        encoding: 파일 인코딩 (기본값: utf-8-sig)
    """
    if not data:
        print(f"  ⚠️  데이터가 비어있어 {filepath} 저장을 건너뜁니다.")
        return
    
    # 모든 키 수집
    fieldnames = set()
    for row in data:
        fieldnames.update(row.keys())
    fieldnames = sorted(fieldnames)
    
    with open(filepath, 'w', newline='', encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"  ✓ 저장 완료: {filepath} ({len(data)}행)")


def save_vertical_merge_csv(data_dir: Path) -> None:
    """
    Vertical Merge 테스트 데이터를 CSV로 저장
    
    Args:
        data_dir: 저장할 디렉토리 경로
    """
    print("\n[Vertical Merge CSV 저장]")
    data_a, data_b = make_vertical_merge_test_data()
    
    save_data_to_csv(data_a, str(data_dir / "vertical_merge_a.csv"))
    save_data_to_csv(data_b, str(data_dir / "vertical_merge_b.csv"))


def save_horizontal_merge_csv(data_dir: Path) -> None:
    """
    Horizontal Merge 테스트 데이터를 CSV로 저장
    
    Args:
        data_dir: 저장할 디렉토리 경로
    """
    print("\n[Horizontal Merge CSV 저장]")
    data_a, data_b = make_horizontal_merge_test_data()
    
    save_data_to_csv(data_a, str(data_dir / "horizontal_merge_a.csv"))
    save_data_to_csv(data_b, str(data_dir / "horizontal_merge_b.csv"))


def save_cross_join_csv(data_dir: Path) -> None:
    """
    Cross Join 테스트 데이터를 CSV로 저장
    
    Args:
        data_dir: 저장할 디렉토리 경로
    """
    print("\n[Cross Join CSV 저장]")
    data_a, data_b = make_cross_join_test_data()
    
    save_data_to_csv(data_a, str(data_dir / "cross_join_a.csv"))
    save_data_to_csv(data_b, str(data_dir / "cross_join_b.csv"))


def print_test_data_summary():
    """생성된 테스트 데이터 요약 출력"""
    print("=" * 60)
    print("src 모듈 테스트 데이터셋 생성")
    print("=" * 60)
    print()
    
    # ID 정규화 테스트 데이터
    id_data = make_id_normalize_test_data()
    print(f"[1] ID 정규화 테스트 데이터: {len(id_data)}개")
    print(f"    예시: {id_data[:3]}")
    print()
    
    # 교집합 테스트 데이터
    ids_a, ids_b = make_intersection_test_data()
    print(f"[2] 교집합 테스트 데이터:")
    print(f"    ids_a: {len(ids_a)}개 - {ids_a}")
    print(f"    ids_b: {len(ids_b)}개 - {ids_b}")
    print(f"    예상 교집합: {set(ids_a) & set(ids_b)}")
    print()
    
    # 필터링 테스트 데이터
    filter_data, filter_ids = make_filter_test_data()
    print(f"[3] 필터링 테스트 데이터:")
    print(f"    데이터: {len(filter_data)}개")
    print(f"    필터 ID: {filter_ids}")
    print(f"    예상 필터링 결과: {len(filter_ids)}개")
    print()
    
    # Cross Join 테스트 데이터
    cross_a, cross_b = make_cross_join_test_data()
    print(f"[4] Cross Join 테스트 데이터:")
    print(f"    data_a: {len(cross_a)}개")
    print(f"    data_b: {len(cross_b)}개")
    print(f"    예상 결과: {len(cross_a) * len(cross_b)}개")
    print()
    
    # Vertical Merge 테스트 데이터
    vert_a, vert_b = make_vertical_merge_test_data()
    print(f"[5] Vertical Merge 테스트 데이터:")
    print(f"    data_a: {len(vert_a)}개")
    print(f"    data_b: {len(vert_b)}개")
    print(f"    예상 결과: {len(vert_a) + len(vert_b)}개")
    print()
    
    # Horizontal Merge 테스트 데이터
    horz_a, horz_b = make_horizontal_merge_test_data()
    print(f"[6] Horizontal Merge 테스트 데이터:")
    print(f"    data_a: {len(horz_a)}개")
    print(f"    data_b: {len(horz_b)}개")
    common_ids = set(row["id"] for row in horz_a) & set(row["id"] for row in horz_b)
    print(f"    공통 ID: {common_ids}")
    print()
    
    # 기관 데이터
    inst_a, inst_b = make_institution_data()
    print(f"[7] 기관 데이터:")
    print(f"    Institution A: {len(inst_a)}개")
    print(f"    Institution B: {len(inst_b)}개")
    print()
    
    # 대용량 데이터
    large_a, large_b = make_large_dataset(100)
    print(f"[8] 대용량 데이터 (100개):")
    print(f"    data_a: {len(large_a)}개")
    print(f"    data_b: {len(large_b)}개")
    print()
    
    print("=" * 60)
    print("✅ 테스트 데이터 생성 함수 준비 완료!")
    print("=" * 60)


def main():
    """메인 함수"""
    print("=" * 60)
    print("src 모듈 테스트 데이터셋 CSV 생성")
    print("=" * 60)
    
    # data 디렉토리 생성
    data_dir = ensure_data_directory()
    print(f"\n📁 저장 경로: {data_dir.absolute()}")
    
    # CSV 저장 실행
    save_vertical_merge_csv(data_dir)
    save_horizontal_merge_csv(data_dir)
    save_cross_join_csv(data_dir)
    
    print("\n" + "=" * 60)
    print("✅ 모든 CSV 파일 생성 완료!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())

