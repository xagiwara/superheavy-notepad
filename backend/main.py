import os
import sys

PYTHONHOME = os.environ.get("PYTHONHOME")
if PYTHONHOME is not None:
    sys.path.append(PYTHONHOME)
sys.path.append("")

import uvicorn
from app import app
import socket
import asyncio
from argparse import ArgumentParser


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--port-file", type=str)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    sock.listen()
    port = sock.getsockname()[1]

    print("port:", port)

    if args.port_file is not None:
        with open(args.port_file, "w", encoding="utf-8") as f:
            f.write(str(port))

    server = uvicorn.Server(uvicorn.Config(app))
    asyncio.run(server.serve([sock]))
