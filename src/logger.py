import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(log_dir: str = "./logs") -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
    log_path = os.path.join(log_dir, log_filename)

    logger = logging.getLogger("async_api_call")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # 콘솔 핸들러 (INFO 이상)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    # 파일 핸들러 (DEBUG 이상)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
