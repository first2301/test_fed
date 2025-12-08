"""
src 모듈 최소 테스트 코드
"""
from src import (
    normalize_id,
    compute_intersection,
    filter_by_ids,
    cross_join,
    vertical_merge,
    horizontal_merge
)


def test_normalize_id():
    """ID 정규화 테스트"""
    print("[1] ID 정규화 테스트")
    result = normalize_id("P-001", hash_it=True)
    print(f"  ✓ normalize_id('P-001'): {result[:16]}...")
    assert len(result) == 64  # SHA-256 해시 길이
    print("  ✓ 통과\n")


def test_compute_intersection():
    """교집합 계산 테스트"""
    print("[2] 교집합 계산 테스트")
    ids_a = ["P-001", "P-002", "P-003"]
    ids_b = ["P-003", "P-004", "P-005"]
    result = compute_intersection(ids_a, ids_b)
    print(f"  ✓ 교집합: {result}")
    assert result == ["P-003"]
    print("  ✓ 통과\n")


def test_filter_by_ids():
    """데이터 필터링 테스트"""
    print("[3] 데이터 필터링 테스트")
    data = [
        {"id": "P-001", "name": "Alice"},
        {"id": "P-002", "name": "Bob"},
        {"id": "P-003", "name": "Charlie"},
    ]
    ids = ["P-001", "P-003"]
    result = filter_by_ids(data, ids, "id")
    print(f"  ✓ 필터링 결과: {len(result)}개")
    assert len(result) == 2
    print("  ✓ 통과\n")


def test_cross_join():
    """Cross Join 테스트"""
    print("[4] Cross Join 테스트")
    data_a = [{"id": "P-001", "name": "Alice"}]
    data_b = [{"id": "P-002", "age": 25}]
    result = cross_join(data_a, data_b)
    print(f"  ✓ Cross Join 결과: {len(result)}개")
    assert len(result) == 1
    assert "a_id" in result[0] and "b_id" in result[0]
    print("  ✓ 통과\n")


def test_vertical_merge():
    """Vertical Merge 테스트"""
    print("[5] Vertical Merge 테스트")
    data_a = [{"id": "P-001", "value": 10}]
    data_b = [{"id": "P-002", "value": 20}]
    result = vertical_merge(data_a, data_b)
    print(f"  ✓ Vertical Merge 결과: {len(result)}개")
    assert len(result) == 2
    print("  ✓ 통과\n")


def test_horizontal_merge():
    """Horizontal Merge 테스트"""
    print("[6] Horizontal Merge 테스트")
    data_a = [{"id": "P-001", "name": "Alice"}]
    data_b = [{"id": "P-001", "age": 25}, {"id": "P-002", "age": 30}]
    
    # Inner Join
    result_inner = horizontal_merge(data_a, data_b, "id", "inner")
    print(f"  ✓ Inner Join 결과: {len(result_inner)}개")
    assert len(result_inner) == 1
    assert "name" in result_inner[0] and "age" in result_inner[0]
    
    # Left Join
    result_left = horizontal_merge(data_a, data_b, "id", "left")
    print(f"  ✓ Left Join 결과: {len(result_left)}개")
    assert len(result_left) == 1
    
    # Outer Join
    result_outer = horizontal_merge(data_a, data_b, "id", "outer")
    print(f"  ✓ Outer Join 결과: {len(result_outer)}개")
    assert len(result_outer) == 2
    print("  ✓ 통과\n")


def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("src 모듈 최소 테스트")
    print("=" * 60)
    print()
    
    try:
        test_normalize_id()
        test_compute_intersection()
        test_filter_by_ids()
        test_cross_join()
        test_vertical_merge()
        test_horizontal_merge()
        
        print("=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

