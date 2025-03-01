from .app import app
from fastapi.staticfiles import StaticFiles
import os

WEBUI_PATH = os.environ.get("WEBUI_PATH")

if WEBUI_PATH is not None:
    app.mount(
        "/",
        StaticFiles(directory=WEBUI_PATH),
    )
