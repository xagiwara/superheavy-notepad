import asyncio
import os
import shutil
import zipfile
from tqdm import tqdm
from .env import CACHE_DIR, BUILD_DIR, BUILD_ARCHIVE
from .frontend import build_frontend
from .electron import build_electron
from .backend import build_backend
from .models import build_models
from .licenses import build_licenses


async def main():
    tqdm.write("preparing...")
    shutil.rmtree(BUILD_ARCHIVE, ignore_errors=True)
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(BUILD_DIR, exist_ok=True)

    tqdm.write("building...")
    await asyncio.gather(
        build_models(),
        build_frontend(),
        build_electron(),
        build_backend(),
    )

    await build_licenses()

    # scan files
    print("Scanning files...")
    all_files: list[str] = []
    for root, _, files in os.walk(BUILD_DIR):
        for file in files:
            all_files.append(os.path.relpath(os.path.join(root, file), BUILD_DIR))

    with zipfile.ZipFile(BUILD_ARCHIVE, "w") as archive:
        for file in tqdm(all_files):
            archive.write(
                os.path.join(BUILD_DIR, file), os.path.join("superheavy-notepad", file)
            )


if __name__ == "__main__":
    asyncio.run(main())
