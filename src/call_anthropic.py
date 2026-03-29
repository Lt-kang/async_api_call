from anthropic import AsyncAnthropic, AuthenticationError, RateLimitError, PermissionDeniedError
from pathlib import Path
import os
import json
import base64
import logging

from dotenv import load_dotenv
load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
claude_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
logger = logging.getLogger(__name__)


async def call_claude(
    model: str,
    user_prompt: str,
    image_path,
    save_path: Path,
    kwargs: dict = {},
):
    if save_path.exists(): return
    os.makedirs(save_path.parent, exist_ok=True)

    system_prompt = kwargs.get("system_prompt", "")

    content = [{"type": "text", "text": user_prompt}]

    if image_path:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        suffix = str(image_path).split(".")[-1].lower()
        media_type = f"image/{'jpeg' if suffix == 'jpg' else suffix}"
        content.insert(0, {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data,
            },
        })

    try:
        message = await claude_client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": content}],
        )
    except AuthenticationError as e:
        logger.error(f"[Anthropic] [{save_path}] API 키가 없거나 유효하지 않습니다. ANTHROPIC_API_KEY를 확인해주세요. ({e})")
        return False
    except PermissionDeniedError as e:
        logger.error(f"[Anthropic] [{save_path}] 접근 권한이 없습니다. 크레딧 또는 결제 정보를 확인해주세요. ({e})")
        return False
    except RateLimitError as e:
        logger.error(f"[Anthropic] [{save_path}] 요청 한도 초과 또는 크레딧이 부족합니다. ({e})")
        return False
    except Exception as e:
        logger.error(f"[Anthropic] [{save_path}] 예상치 못한 오류가 발생했습니다. ({type(e).__name__}: {e})")
        return False

    results = message.model_dump()
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    return True
