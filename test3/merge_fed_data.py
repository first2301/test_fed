"""
Federated Learning 데이터 통합 모듈
vertical, horizontal, cross 데이터 통합
"""
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

from src import vertical_merge, horizontal_merge, cross_join


def load_csv_data(filepath: str) -> List[Dict[str, Any]]:
    """
    CSV 파일을 읽어서 딕셔너리 리스트로 반환
    
    Args:
        filepath: CSV 파일 경로
    
    Returns:
        딕셔너리 리스트
    """
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        print(f"  ⚠️  파일을 찾을 수 없습니다: {filepath}")
    except Exception as e:
        print(f"  ❌ 파일 읽기 오류 ({filepath}): {e}")
    
    return data


def save_merged_data(
    data: List[Dict[str, Any]],
    filepath: str,
    encoding: str = "utf-8-sig"
) -> None:
    """
    통합된 데이터를 CSV 파일로 저장
    
    Args:
        data: 저장할 데이터 리스트
        filepath: 저장할 파일 경로
        encoding: 파일 인코딩
    """
    if not data:
        print(f"  ⚠️  데이터가 비어있어 {filepath} 저장을 건너뜁니다.")
        return
    
    # 모든 키 수집
    fieldnames = set()
    for row in data:
        fieldnames.update(row.keys())
    fieldnames = sorted(fieldnames)
    
    try:
        with open(filepath, 'w', newline='', encoding=encoding) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"  ✓ 저장 완료: {filepath} ({len(data)}행)")
    except Exception as e:
        print(f"  ❌ 파일 저장 오류 ({filepath}): {e}")


def merge_vertical_data(
    data_dir: Path,
    output_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Vertical Merge 데이터 통합
    
    Args:
        data_dir: 데이터 디렉토리 경로
        output_dir: 결과 저장 디렉토리 (None이면 저장 안함)
    
    Returns:
        통합된 데이터 리스트
    """
    print("\n[Vertical Merge 통합]")
    
    # CSV 파일 읽기
    file_a = data_dir / "vertical_merge_a.csv"
    file_b = data_dir / "vertical_merge_b.csv"
    
    data_a = load_csv_data(str(file_a))
    data_b = load_csv_data(str(file_b))
    
    if not data_a or not data_b:
        print("  ⚠️  데이터가 없어 통합을 건너뜁니다.")
        return []
    
    print(f"  ✓ 데이터 A: {len(data_a)}건")
    print(f"  ✓ 데이터 B: {len(data_b)}건")
    
    # Vertical Merge 통합
    merged = vertical_merge(data_a, data_b)
    print(f"  ✓ 통합 결과: {len(merged)}건")
    
    # 결과 저장
    if output_dir:
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "vertical_merge_result.csv"
        save_merged_data(merged, str(output_file))
    
    return merged


def merge_horizontal_data(
    data_dir: Path,
    id_key: str = "id",
    how: str = "inner",
    output_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Horizontal Merge 데이터 통합
    
    Args:
        data_dir: 데이터 디렉토리 경로
        id_key: 공통 ID 키
        how: 병합 방법 ('inner', 'left', 'right', 'outer')
        output_dir: 결과 저장 디렉토리 (None이면 저장 안함)
    
    Returns:
        통합된 데이터 리스트
    """
    print(f"\n[Horizontal Merge 통합 - {how} join]")
    
    # CSV 파일 읽기
    file_a = data_dir / "horizontal_merge_a.csv"
    file_b = data_dir / "horizontal_merge_b.csv"
    
    data_a = load_csv_data(str(file_a))
    data_b = load_csv_data(str(file_b))
    
    if not data_a or not data_b:
        print("  ⚠️  데이터가 없어 통합을 건너뜁니다.")
        return []
    
    print(f"  ✓ 데이터 A: {len(data_a)}건")
    print(f"  ✓ 데이터 B: {len(data_b)}건")
    
    # Horizontal Merge 통합
    merged = horizontal_merge(data_a, data_b, id_key, how)
    print(f"  ✓ 통합 결과: {len(merged)}건")
    
    # 결과 저장
    if output_dir:
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"horizontal_merge_{how}.csv"
        save_merged_data(merged, str(output_file))
    
    return merged


def merge_cross_join_data(
    data_dir: Path,
    prefix_a: str = "a_",
    prefix_b: str = "b_",
    output_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Cross Join 데이터 통합
    
    Args:
        data_dir: 데이터 디렉토리 경로
        prefix_a: 첫 번째 데이터 접두사
        prefix_b: 두 번째 데이터 접두사
        output_dir: 결과 저장 디렉토리 (None이면 저장 안함)
    
    Returns:
        통합된 데이터 리스트
    """
    print("\n[Cross Join 통합]")
    
    # CSV 파일 읽기
    file_a = data_dir / "cross_join_a.csv"
    file_b = data_dir / "cross_join_b.csv"
    
    data_a = load_csv_data(str(file_a))
    data_b = load_csv_data(str(file_b))
    
    if not data_a or not data_b:
        print("  ⚠️  데이터가 없어 통합을 건너뜁니다.")
        return []
    
    print(f"  ✓ 데이터 A: {len(data_a)}건")
    print(f"  ✓ 데이터 B: {len(data_b)}건")
    
    # Cross Join 통합
    merged = cross_join(data_a, data_b, prefix_a, prefix_b)
    print(f"  ✓ 통합 결과: {len(merged)}건")
    
    # 결과 저장
    if output_dir:
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "cross_join_result.csv"
        save_merged_data(merged, str(output_file))
    
    return merged


def main():
    """
    메인 함수 - 모든 통합 작업 실행
    """
    print("=" * 60)
    print("Federated Learning 데이터 통합")
    print("=" * 60)
    
    # 디렉토리 설정
    data_dir = Path("data")
    output_dir = data_dir / "merged"
    
    print(f"\n📁 데이터 경로: {data_dir.absolute()}")
    print(f"📁 결과 저장 경로: {output_dir.absolute()}")
    
    # 1. Vertical Merge 통합
    vertical_result = merge_vertical_data(data_dir, output_dir)
    
    # 2. Horizontal Merge 통합 (각 join 타입별)
    for join_type in ["inner", "left", "right", "outer"]:
        merge_horizontal_data(data_dir, id_key="id", how=join_type, output_dir=output_dir)
    
    # 3. Cross Join 통합
    cross_result = merge_cross_join_data(data_dir, output_dir=output_dir)
    
    # 최종 요약
    print("\n" + "=" * 60)
    print("✅ 모든 데이터 통합 완료!")
    print("=" * 60)
    print(f"\n생성된 결과 파일:")
    print(f"  - vertical_merge_result.csv: {len(vertical_result)}건")
    print(f"  - horizontal_merge_inner.csv")
    print(f"  - horizontal_merge_left.csv")
    print(f"  - horizontal_merge_right.csv")
    print(f"  - horizontal_merge_outer.csv")
    print(f"  - cross_join_result.csv: {len(cross_result)}건")
    
    return 0


if __name__ == "__main__":
    exit(main())

