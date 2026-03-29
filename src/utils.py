from pathlib import Path
import pandas as pd

from src.call_openai import call_gpt
from src.call_google import call_gemini
from src.call_anthropic import call_claude


async def add_task(
    model: str,
    user_prompt: str,
    image_path,
    save_path: Path,
    kwargs: dict,
):
    model_lower = model.lower()
    if "gpt" in model_lower:
        return await call_gpt(model=model, user_prompt=user_prompt, image_path=image_path, save_path=save_path, kwargs=kwargs)
    elif "claude" in model_lower:
        return await call_claude(model=model, user_prompt=user_prompt, image_path=image_path, save_path=save_path, kwargs=kwargs)
    else:
        return await call_gemini(model=model, user_prompt=user_prompt, image_path=image_path, save_path=save_path, kwargs=kwargs)


def add_tasks(
    df: pd.DataFrame,
    output_path: str,
    images_mapping: dict,
    kwargs: dict,
):
    unit_tasks = []
    for idx, row in df.iterrows():
        save_path = Path(output_path) / Path(row["save_path"])

        if save_path.exists():
            continue

        model = row["model"]
        user_prompt = row["user_prompt"]
        image_path = row["image_path"]
        image_path = None if image_path.strip() == "" else images_mapping.get(image_path)

        unit_tasks.append(
            add_task(
                model=model,
                user_prompt=user_prompt,
                image_path=image_path,
                save_path=save_path,
                kwargs=kwargs,
            )
        )

    return unit_tasks
