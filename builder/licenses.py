import os
import asyncio
from .env import CACHE_DIR, BUILD_DIR
import json
from tqdm import tqdm
from typing import TypedDict
import httpx


class License(TypedDict):
    name: str
    author: str
    url: str
    license: str
    license_text: str


async def backend_licenses() -> list[License]:
    with open(os.path.join(CACHE_DIR, "requirements.txt"), "r") as f:
        requirements = [
            x.split("==")[0] for x in f.read().splitlines() if not x.startswith("-")
        ]

    proc = await asyncio.create_subprocess_shell(
        "pip-licenses --with-authors --with-urls --with-license-file --format=json --packages "
        + " ".join(requirements),
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    licenses = json.loads(stdout)

    return [
        {
            "name": x["Name"],
            "author": x["Author"],
            "url": x["URL"],
            "license": x["License"],
            "license_text": x["LicenseText"],
        }
        for x in licenses
    ]


async def npm_licenses(target: str) -> list[License]:
    proc = await asyncio.create_subprocess_shell(
        "npx -y license-checker --json --production --start " + target,
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    licenses: dict = json.loads(stdout)

    for a in tqdm(licenses.values(), desc=f"licenses({target})"):
        if "licenseFile" in a:
            with open(a["licenseFile"], "r", encoding="utf-8") as f:
                a["license_text"] = f.read()

    return [
        {
            "name": x,
            "author": a["publisher"] if "publisher" in a else None,
            "license": a["licenses"],
            "license_text": a["license_text"] if "license_text" in a else None,
            "url": a["repository"] if "repository" in a else None,
        }
        for x, a in licenses.items()
    ]


async def extra_licenses() -> list[License]:
    with open(os.path.join(os.path.dirname(__file__), "extra-packages.json"), "r") as f:
        data = json.load(f)

    license_urls: set[str] = {
        x["license_text_url"]
        for x in data
        if "license_text" not in x and "license_text_url" in x
    }
    license_texts: dict[str, str] = {}

    async with httpx.AsyncClient() as client:
        for url in tqdm(license_urls, desc="extra-licenses"):
            response = await client.get(url)
            license_texts[url] = response.text

    return [
        (
            x
            if "license_text" in x
            else {**x, "license_text": license_texts[x["license_text_url"]]}
        )
        for x in data
    ]


async def build_licenses():
    frontend = await npm_licenses("frontend")
    electron = await npm_licenses("electron")
    backend = await backend_licenses()
    extra = await extra_licenses()

    licenses = list(
        {x["name"]: x for x in [*frontend, *electron, *backend, *extra]}.values()
    )

    with open(os.path.join(BUILD_DIR, "licenses.html"), "w", encoding="utf-8") as f:
        f.write(
            """
            <html>
            <head>
                <title>Third-party Licenses</title>
            </head>
            <body>
            <h1>Third-party Licenses</h1>
            """
        )

        for license in licenses:
            f.write(
                f"""
                <details>
                    <summary><a href="{license["url"]}" target="_blank">{license["name"]}</a> by {license["author"]} ({license["license"]})</summary>
                    <pre>{license["license_text"]}</pre>
                </details>
                """
            )

        f.write(
            """
            </body>
            </html>
            """
        )
