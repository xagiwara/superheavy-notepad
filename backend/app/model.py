from transformers import PreTrainedTokenizer, AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os
from logging import getLogger
import asyncio
import torch
from typing import Literal

logger = getLogger("uvicorn.lifespan")

data = {}

base_model_id = "llm-jp/llm-jp-3-1.8b"
FINETUNED_DIR = os.environ["FINETUNED_DIR"]


def get_model():
    return data["model"]


def get_tokenizer() -> PreTrainedTokenizer:
    return data["tokenizer"]


LoadingStatus = Literal[
    "loading_base_model",
    "loading_peft_model",
    "loading_tokenizer",
    "warming_up",
    "done",
]


def get_loading_status():
    return data["loading"]


def load_model():
    global tokenizer

    logger.info("Loading base model...")

    data["loading"] = "loading_base_model"

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        # quantization_config=bnb_config,
        device_map="auto",
    )

    dirs = os.listdir(FINETUNED_DIR)
    dirs.sort()

    logger.info(f"loading peft model from {dirs[-1]}")

    data["loading"] = "loading_peft_model"

    # LoRA を適用
    model = PeftModel.from_pretrained(base_model, os.path.join(FINETUNED_DIR, dirs[-1]))
    model.eval()

    logger.info("loading tokenizer")

    data["loading"] = "loading_tokenizer"

    tokenizer = AutoTokenizer.from_pretrained(base_model_id)

    data["model"] = model
    data["tokenizer"] = tokenizer

    data["loading"] = "warming_up"

    tokenized_input = tokenizer.encode(
        "\u3000", return_tensors="pt", add_special_tokens=False
    ).to(get_model().device)

    with torch.no_grad():
        output = model.generate(
            tokenized_input,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            max_new_tokens=10,
            top_p=0.95,
            top_k=50,
            num_return_sequences=1,
            temperature=0.8,
            repetition_penalty=1.05,
        )
    logger.info("warming up:" + tokenizer.decode(output[0], skip_special_tokens=True))

    data["loading"] = "done"


async def start_load_model():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_model)
