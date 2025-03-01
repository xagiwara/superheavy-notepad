import torch.version
from ..app import app
from typing import TypedDict
from ..model import LoadingStatus, get_loading_status, get_model
import torch


class GetReadyResponse(TypedDict):
    done: bool
    status: LoadingStatus


@app.get("/api/ready")
async def get_ready() -> GetReadyResponse:
    status = get_loading_status()
    return {
        "done": status == "done",
        "status": status,
    }


class GetStatusResponseCuda(TypedDict):
    version: str
    device_name: str | None


class GetStatusResponse(TypedDict):
    torch: str
    cuda: GetStatusResponseCuda | None


@app.get("/api/status")
async def get_status() -> GetStatusResponse:
    status = get_loading_status()
    return {
        "torch": torch.__version__,
        "cuda": (
            {
                "version": torch.version.cuda,
                "device_name": (
                    torch.cuda.get_device_name(get_model().device)
                    if status == "done"
                    else None
                ),
            }
            if torch.cuda.is_available()
            else None
        ),
    }
