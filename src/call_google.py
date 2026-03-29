from google import genai
from google.genai import types, errors
from pathlib import Path
import os
import json
import base64
import logging

from dotenv import load_dotenv
load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
logger = logging.getLogger(__name__)


async def call_gemini(
    model: str,
    user_prompt: str,
    image_path,
    save_path: Path,
    kwargs: dict = {},
):
    if save_path.exists(): return
    os.makedirs(save_path.parent, exist_ok=True)

    system_prompt = kwargs.get("system_prompt", "")

    contents = [user_prompt]

    if image_path:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        suffix = str(image_path).split(".")[-1].lower()
        mime_type = f"image/{'jpeg' if suffix == 'jpg' else suffix}"
        contents.append(
            types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes))
        )

    try:
        response = await gemini_client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
    except errors.ClientError as e:
        if e.code == 401:
            logger.error(f"[Google] [{save_path}] API 키가 없거나 유효하지 않습니다. GOOGLE_API_KEY를 확인해주세요. ({e})")
        elif e.code == 429:
            logger.error(f"[Google] [{save_path}] 요청 한도 초과 또는 크레딧이 부족합니다. ({e})")
        else:
            logger.error(f"[Google] [{save_path}] 요청 오류가 발생했습니다. (HTTP {e.code}: {e})")
        return False
    except errors.ServerError as e:
        logger.error(f"[Google] [{save_path}] 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요. ({e})")
        return False
    except Exception as e:
        logger.error(f"[Google] [{save_path}] 예상치 못한 오류가 발생했습니다. ({type(e).__name__}: {e})")
        return False

    results = {
        "model": model,
        "text": response.text,
        "usage_metadata": str(response.usage_metadata) if response.usage_metadata else None,
    }
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    return True
