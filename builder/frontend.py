from .env import FRONTEND_DIR, BUILD_DIR
import asyncio
import os
import shutil
from .copy import copy_dir


async def build_frontend():
    proc = await asyncio.create_subprocess_shell("npm ci", cwd=FRONTEND_DIR)
    await proc.wait()

    shutil.rmtree(os.path.join(FRONTEND_DIR, "dist"), ignore_errors=True)

    proc = await asyncio.create_subprocess_shell("npm run build", cwd=FRONTEND_DIR)
    await proc.wait()

    # copy all files
    src_dir = os.path.join(FRONTEND_DIR, "dist")
    dist_dir = os.path.join(BUILD_DIR, "data", "ui")
    await copy_dir(src_dir, dist_dir)
