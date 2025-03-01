from fastapi import FastAPI
from contextlib import asynccontextmanager
from .model import start_load_model
from logging import getLogger
import asyncio

logger = getLogger("uvicorn.lifespan")


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    asyncio.create_task(start_load_model())
    try:
        yield
    finally:
        pass
