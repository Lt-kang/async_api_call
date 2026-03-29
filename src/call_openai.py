from openai import AsyncOpenAI, AuthenticationError, RateLimitError, PermissionDeniedError
from pathlib import Path
import os
import json
import base64
import logging

from dotenv import load_dotenv
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def call_gpt(
    model: str,
    user_prompt: str,
    image_path,
    save_path: Path,
    kwargs: dict = {},
):
    if save_path.exists(): return
    os.makedirs(save_path.parent, exist_ok=True)

    system_prompt = kwargs.get("system_prompt", "")

    _system_content = [
        {"type": "input_text", "text": system_prompt}
    ]
    _user_content = [
        {"type": "input_text", "text": user_prompt},
    ]

    if image_path:
        base64_image = encode_image(image_path)
        suffix = str(image_path).split(".")[-1].lower()
        _user_content.append({
            "type": "input_image",
            "image_url": f"data:image/{suffix};base64,{base64_image}",
        })

    try:
        response = await openai_client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": _system_content},
                {"role": "user", "content": _user_content},
            ],
        )
    except AuthenticationError as e:
        logger.error(f"[OpenAI] [{save_path}] API 키가 없거나 유효하지 않습니다. OPENAI_API_KEY를 확인해주세요. ({e})")
        return False
    except PermissionDeniedError as e:
        logger.error(f"[OpenAI] [{save_path}] 접근 권한이 없습니다. 크레딧 또는 API 키 권한을 확인해주세요. ({e})")
        return False
    except RateLimitError as e:
        logger.error(f"[OpenAI] [{save_path}] 요청 한도 초과 또는 크레딧이 부족합니다. ({e})")
        return False
    except Exception as e:
        logger.error(f"[OpenAI] [{save_path}] 예상치 못한 오류가 발생했습니다. ({type(e).__name__}: {e})")
        return False

    results = response.model_dump()
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    return True
