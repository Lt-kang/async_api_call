import pandas as pd

REQUIRED_COLUMNS = {"model", "save_path", "user_prompt"}


def validate_csv(df: pd.DataFrame, images_mapping: dict) -> bool:
    """
    CSV 데이터를 API 호출 전에 검사합니다.
    문제가 있으면 한국어 오류 메시지를 출력하고 False를 반환합니다.
    문제가 없으면 True를 반환합니다.
    """
    errors = []

    # 1. 필수 컬럼 확인
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        errors.append(f"[오류] CSV에 필수 컬럼이 없습니다: {', '.join(missing_cols)}")
        _print_errors(errors)
        return False

    # 2. 행별 검사
    for idx, row in df.iterrows():
        row_num = idx + 2  # 헤더 제외, 1-based

        image_path = str(row.get("image_path", "")).strip()
        if image_path and image_path not in images_mapping:
            errors.append(
                f"[오류] {row_num}행: 이미지 파일 '{image_path}'을 이미지 폴더에서 찾을 수 없습니다."
            )

    if errors:
        _print_errors(errors)
        return False

    return True


def _print_errors(errors: list):
    print("\n" + "=" * 50)
    print("입력 검증 실패 — 아래 오류를 확인해주세요.")
    print("=" * 50)
    for err in errors:
        print(err)
    print("=" * 50 + "\n")
