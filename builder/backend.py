from .env import BACKEND_DIR, CACHE_DIR, BUILD_DIR
import asyncio
import os
import shutil
import httpx
from .copy import copy_dir
from tqdm import tqdm


PYTHON_URL = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-embed-amd64.zip"


async def download_python():
    if not os.path.exists(os.path.join(CACHE_DIR, "python.zip")):
        async with httpx.AsyncClient() as client:
            response = await client.get(PYTHON_URL)
            with open(os.path.join(CACHE_DIR, "python.zip"), "wb") as f:
                f.write(response.content)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        shutil.unpack_archive,
        os.path.join(CACHE_DIR, "python.zip"),
        os.path.join(BUILD_DIR, "data", "python"),
    )

    with open(
        os.path.join(BUILD_DIR, "data", "python", "python313._pth"),
        "a",
        encoding="utf-8",
    ) as f:
        f.write("import site\nsite-packages\n")


async def create_requirements():
    proc = await asyncio.create_subprocess_shell(
        "pipenv requirements",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    with open(os.path.join(CACHE_DIR, "requirements.txt"), "wb") as f:
        f.write(stdout)


async def install_packages():
    proc = await asyncio.create_subprocess_shell(
        f"pip install",
        env={
            **os.environ,
            "PIP_CACHE_DIR": os.path.join(CACHE_DIR, "pip"),
            "PIP_TARGET": os.path.join(CACHE_DIR, "site-packages"),
            "PIP_REQUIREMENT": os.path.join(CACHE_DIR, "requirements.txt"),
        },
    )
    await proc.wait()

    src_dir = os.path.join(CACHE_DIR, "site-packages")
    dist_dir = os.path.join(BUILD_DIR, "data", "python", "site-packages")
    await copy_dir(
        src_dir,
        dist_dir,
        lambda x: os.path.basename(os.path.dirname(x)) != "__pycache__",
    )


async def build_backend():
    await asyncio.gather(
        download_python(),
        create_requirements(),
    )
    await install_packages()
    await copy_dir(
        os.path.join(BACKEND_DIR),
        os.path.join(BUILD_DIR, "data", "server"),
        lambda x: os.path.basename(os.path.dirname(x)) != "__pycache__",
    )
