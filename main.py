import argparse
from pathlib import Path
import pandas as pd
import yaml
from tqdm import tqdm
import asyncio

from src import add_tasks
from src.validator import validate_csv
from src.logger import setup_logger


async def run(df, output_path, images_mapping, model_default_kwargs, BATCH_SIZE, logger):
    tasks = []
    if len(df) <= BATCH_SIZE:
        unit_tasks = add_tasks(df=df, output_path=output_path, images_mapping=images_mapping, kwargs=model_default_kwargs)
        tasks.extend(unit_tasks)
    else:
        for idx in tqdm(range(0, len(df), BATCH_SIZE), desc="배치 처리 중"):
            batch = df.iloc[idx:idx + BATCH_SIZE]
            unit_tasks = add_tasks(df=batch, output_path=output_path, images_mapping=images_mapping, kwargs=model_default_kwargs)
            tasks.extend(unit_tasks)

            if len(tasks) >= BATCH_SIZE:
                await asyncio.gather(*tasks)
                tasks = []

    if tasks:
        await asyncio.gather(*tasks)

    logger.info("모든 요청이 완료되었습니다.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CSV 파일을 입력으로 LLM API 비동기 배치 요청을 실행합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python main.py
  python main.py --config settings/config.yaml
        """,
    )
    parser.add_argument(
        "--config",
        default="settings/config.yaml",
        help="설정 파일 경로 (기본값: settings/config.yaml)",
    )
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    input_path = config["path"]["input"]
    system_prompt_path = config["path"]["system_prompt"]
    file_path = config["path"]["file_path"]
    output_path = config["path"]["output"]
    BATCH_SIZE = config["settings"]["request"]["batch_size"]
    target_suffixes = config["settings"]["image_file"]["suffix"]

    logger = setup_logger()
    logger.info(f"설정 파일: {Path(args.config).absolute()}")
    logger.info(f"입력 CSV: {Path(input_path).absolute()}")
    logger.info(f"시스템 프롬프트: {Path(system_prompt_path).absolute()}")
    logger.info(f"이미지 폴더: {Path(file_path).absolute()}")
    logger.info(f"배치 크기: {BATCH_SIZE}")

    model_default_kwargs = {
        "system_prompt": Path(system_prompt_path).read_text(encoding="utf-8").strip(),
    }

    images_mapping = {
        f.name: f
        for f in Path(file_path).rglob("*.*")
        if f.suffix.lower() in target_suffixes
    }

    try:
        df = pd.read_csv(input_path) # utf-8
    except UnicodeDecodeError:
        df = pd.read_csv(input_path, encoding="cp949") # cp949
    except Exception as e:
        logger.error(f"입력 CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
        exit(1)

    df.fillna("", inplace=True)

    logger.info(f"총 {len(df)}개 행을 읽었습니다.")

    if not validate_csv(df, images_mapping):
        logger.error("입력 검증 실패. 실행을 중단합니다.")
        exit(1)

    asyncio.run(run(df, output_path, images_mapping, model_default_kwargs, BATCH_SIZE, logger))
