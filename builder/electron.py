from .env import ELECTRON_DIR, BUILD_DIR
import asyncio
import os
import shutil


async def build_electron():
    loop = asyncio.get_event_loop()

    proc = await asyncio.create_subprocess_shell("npm ci", cwd=ELECTRON_DIR)
    await proc.wait()

    shutil.rmtree(os.path.join(ELECTRON_DIR, "dist"), ignore_errors=True)
    shutil.rmtree(os.path.join(ELECTRON_DIR, "out"), ignore_errors=True)

    proc = await asyncio.create_subprocess_shell("npm run build", cwd=ELECTRON_DIR)
    await proc.wait()

    # copy all files
    src_dir = os.path.join(
        ELECTRON_DIR, "out", os.listdir(os.path.join(ELECTRON_DIR, "out"))[0]
    )
    for root, dirs, files in os.walk(src_dir):
        for d in dirs:
            filepath = os.path.relpath(os.path.join(root, d), src_dir)
            os.makedirs(os.path.join(BUILD_DIR, filepath), exist_ok=True)

        for file in files:
            filepath = os.path.relpath(os.path.join(root, file), src_dir)
            os.link(
                os.path.join(src_dir, filepath),
                os.path.join(BUILD_DIR, filepath),
            )
