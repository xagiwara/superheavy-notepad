from ..app import app
from typing import TypedDict
from ..model import get_tokenizer, get_model
import torch
from logging import getLogger

logger = getLogger("uvicorn.infer")


def generate_response(prompt, max_new_tokens=64, n_best=1, skip_special_tokens=True):
    tokenizer = get_tokenizer()
    model = get_model()

    tokenized_input = tokenizer.encode(
        prompt, return_tensors="pt", add_special_tokens=False
    ).to(get_model().device)
    with torch.no_grad():
        output = model.generate(
            tokenized_input,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            max_new_tokens=max_new_tokens,
            top_p=0.95,
            top_k=50,
            num_return_sequences=n_best,
            temperature=0.8,
            repetition_penalty=1.05,
        )
    return [
        tokenizer.decode(
            x[len(tokenized_input[0]) :], skip_special_tokens=skip_special_tokens
        )
        for x in output
    ]


class InferTextRequest(TypedDict):
    text: str
    tags: list[str]


class InferTextResponse(TypedDict):
    candidates: list[str]


@app.post("/api/infer/text")
async def infer_text(body: InferTextRequest) -> InferTextResponse:
    prompt = "本文の続きを生成する。\n\n"
    if len(body["tags"]) > 0:
        prompt += f"### タグ:\n{' '.join(body['tags'])}\n\n"
    prompt += "### 本文:\n" + body["text"]

    responses = generate_response(prompt, max_new_tokens=64, n_best=3)
    return {"candidates": responses}


class InferTagsRequest(TypedDict):
    text: str


class InferTagsResponse(TypedDict):
    tags: list[str]


@app.post("/api/infer/tags")
async def infer_tags(body: InferTagsRequest) -> InferTagsResponse:
    prompt = (
        "本文をもとに、タグを生成する。\n\n### 本文:\n"
        + body["text"]
        + "\n\n### タグ:\n"
    )

    responses = generate_response(prompt, max_new_tokens=64)[0]
    logger.info(responses)
    return {
        "tags": [
            y[1:] if y.startswith("#") else y
            for y in [x for x in responses.split("\n") if x.strip() != ""][0].split()
        ]
    }


class InferSummaryRequest(TypedDict):
    text: str


class InferSummaryResponse(TypedDict):
    summary: str
    complete: bool


@app.post("/api/infer/summary")
async def infer_summary(body: InferSummaryRequest) -> InferSummaryResponse:
    prompt = (
        "本文をもとに、あらすじを生成する。\n\n### 本文:\n"
        + body["text"]
        + "\n\n### あらすじ:\n"
    )

    responses = generate_response(
        prompt, max_new_tokens=512, skip_special_tokens=False
    )[0]
    complete = False

    if responses.endswith("</s>"):
        complete = True
        responses = responses[:-4]

    return {
        "summary": responses,
        "complete": complete,
    }


class InferInsertRequest(TypedDict):
    before: str
    after: str
    tags: list[str]


class InferInsertResponse(TypedDict):
    candidates: list[str]


@app.post("/api/infer/insert")
async def infer_insert(body: InferInsertRequest) -> InferInsertResponse:
    prompt = "続きの部分につながるように、本文を生成する。\n\n"
    if len(body["tags"]) > 0:
        prompt += f"### タグ:\n{' '.join(body['tags'])}\n\n"
    prompt += f"### 続きの部分:\n{body["after"]}\n\n### 本文:\n{body["before"]}"

    responses = generate_response(prompt, max_new_tokens=64, n_best=3)
    return {"candidates": responses}
