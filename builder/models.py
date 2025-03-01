import os
from transformers import AutoModelForCausalLM, AutoTokenizer, TRANSFORMERS_CACHE
import asyncio
from .env import BUILD_DIR, FINETUNED_DIR
from .copy import copy_dir


async def build_models():
    loop = asyncio.get_running_loop()
    [model, tokenizer] = await asyncio.gather(
        loop.run_in_executor(
            None, AutoModelForCausalLM.from_pretrained, "llm-jp/llm-jp-3-1.8b"
        ),
        loop.run_in_executor(
            None, AutoTokenizer.from_pretrained, "llm-jp/llm-jp-3-1.8b"
        ),
    )
    del model
    del tokenizer

    os.makedirs(
        os.path.join(
            BUILD_DIR, "data", "models", "hf", "models--llm-jp--llm-jp-3-1.8b"
        ),
        exist_ok=True,
    )
    os.makedirs(os.path.join(BUILD_DIR, "data", "models", "finetuned"), exist_ok=True)

    finetuned_list = os.listdir(FINETUNED_DIR)
    finetuned_list.sort()
    finetuned_model = finetuned_list[-1]

    await asyncio.gather(
        copy_dir(
            os.path.join(TRANSFORMERS_CACHE, "models--llm-jp--llm-jp-3-1.8b"),
            os.path.join(
                BUILD_DIR,
                "data",
                "models",
                "hf",
                "models--llm-jp--llm-jp-3-1.8b",
            ),
        ),
        copy_dir(
            os.path.join(FINETUNED_DIR, finetuned_model),
            os.path.join(BUILD_DIR, "data", "models", "finetuned", finetuned_model),
        ),
    )
