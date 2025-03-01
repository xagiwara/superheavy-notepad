import os
from typing import Callable


async def copy_dir(
    src_dir: str,
    dist_dir: str,
    file_filter: Callable[[str], bool] = lambda x: True,
):
    for root, _, files in os.walk(src_dir):
        for file in files:
            filepath = os.path.relpath(os.path.join(root, file), src_dir)
            if not file_filter(filepath):
                continue
            os.makedirs(
                os.path.dirname(os.path.join(dist_dir, filepath)), exist_ok=True
            )
            os.link(
                os.path.join(src_dir, filepath),
                os.path.join(dist_dir, filepath),
            )
            print(filepath)
