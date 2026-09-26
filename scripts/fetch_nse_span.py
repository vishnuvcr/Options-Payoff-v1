#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import re
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import requests

ARCHIVE_URL = "https://www.archive.nseclearing.in/marketreports/"
LANDING_URL = "https://www.nseclearing.in/resources/marketreports"

DATE_FORMATS = ("%Y%m%d", "%d%m%Y", "%Y-%m-%d", "%d-%m-%Y")


def fetch_text(url: str) -> str:
    r = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Options-Payoff-v1 research bot/1.0"},
    )
    r.raise_for_status()
    return r.text



def direct_candidates(date_token: str) -> list[str]:
    # NSE Clearing's daily derivatives reports use names such as
    # nsccl.YYYYMMDD.s.spn and nsccl.YYYYMMDD.i01.spn.
    # Try common archive locations before falling back to page discovery.
    names = [
        f"nsccl.{date_token}.s.spn",
        f"nsccl.{date_token}.i01.spn",
        f"nsccl.{date_token}.i02.spn",
        f"nsccl.{date_token}.i03.spn",
        f"nsccl.{date_token}.i04.spn",
        f"nsccl.{date_token}.i05.spn",
    ]
    roots = [
        "https://www.archive.nseclearing.in/marketreports/",
    ]
    return [base + name for base in roots for name in names]


def candidate_urls(date_token: str) -> set[str]:
    pages = []
    for url in (ARCHIVE_URL, LANDING_URL):
        try:
            pages.append((url, fetch_text(url)))
        except Exception:
            continue

    urls: set[str] = set()
    for base, html in pages:
        for raw in re.findall(r'''(?:href|src)=["']([^"']+)["']''', html, re.I):
            u = urljoin(base, raw)
            low = u.lower()
            if ".spn" in low or ".zip" in low or ".bz2" in low or ".gz" in low:
                urls.add(u)

    # Also include direct-looking URLs embedded in scripts/JSON.
    for base, html in pages:
        for raw in re.findall(r'https?://[^\s"\'<>]+', html):
            low = raw.lower()
            if ".spn" in low or ".zip" in low or ".bz2" in low or ".gz" in low:
                urls.add(raw)

    # Prefer links whose filename contains the requested date.
    preferred = {u for u in urls if date_token.lower() in u.lower()}
    return preferred or urls


def probe_url(url: str) -> bool:
    try:
        r = requests.head(
            url,
            timeout=8,
            allow_redirects=True,
            headers={"User-Agent": "Options-Payoff-v1 research bot/1.0"},
        )
        return r.status_code == 200
    except Exception:
        return False


def download_bytes(url: str) -> bytes:
    r = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Options-Payoff-v1 research bot/1.0"},
    )
    r.raise_for_status()
    return r.content


def extract_span_payload(payload: bytes, name: str) -> tuple[str, bytes] | None:
    if payload[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            for member in z.namelist():
                if member.lower().endswith(".spn"):
                    return member, z.read(member)
    if payload[:3] == b"BZh" or payload[:2] == b"\x1f\x8b":
        # Leave compressed single-file handling to the runner; archive names are
        # recorded so a future format-specific decoder can be added safely.
        return None
    if b"<fileFormat" in payload[:5000] or b"<futPf" in payload[:5000]:
        return name, payload
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-candidates", type=int, default=50)
    args = ap.parse_args()

    date_token = args.date.replace("-", "")
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    direct = direct_candidates(date_token)
    urls = [u for u in direct if probe_url(u)]
    if not urls:
        try:
            urls.extend(sorted(candidate_urls(date_token)))
        except Exception as exc:
            print(f"Archive discovery failed: {type(exc).__name__}: {exc}")
    if not urls:
        raise RuntimeError(
            "No SPAN-like links discovered from NSE Clearing market-report archive."
        )

    tried = []
    seen = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        if len(seen) > args.max_candidates:
            break
        tried.append(url)
        try:
            payload = download_bytes(url)
            extracted = extract_span_payload(payload, Path(url.split("?")[0]).name)
            if extracted is None:
                continue
            name, data = extracted
            target = out / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            print(f"SPAN_FILE={target}")
            print(f"SOURCE_URL={url}")
            print(f"BYTES={len(data)}")
            return
        except Exception as exc:
            print(f"SKIP {url}: {type(exc).__name__}: {exc}")

    raise RuntimeError(
        "Could not download/extract a usable .spn file. Tried:\n" + "\n".join(tried)
    )


if __name__ == "__main__":
    main()
