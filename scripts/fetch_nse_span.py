#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        "https://nsearchives.nseindia.com/archives/nsccl/span/",
        "https://www.archive.nseclearing.in/marketreports/",
        "https://www.archive.nseclearing.in/marketreports/derivatives/",
        "https://www.archive.nseclearing.in/marketreports/FO/",
        "https://www.archive.nseclearing.in/marketreports/NFO/",
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
        r = requests.get(
            url,
            stream=True,
            timeout=(4, 8),
            allow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/octet-stream,*/*;q=0.8",
                "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
                "Referer": "https://www.nseindia.com/",
            },
        )
        ok = r.status_code in (200, 206)
        r.close()
        return ok
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
    ap.add_argument('--date', required=True, help='YYYY-MM-DD')
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()

    date_token = args.date.replace('-', '')
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept': 'application/octet-stream,*/*;q=0.8',
        'Accept-Language': 'en-IN,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://www.nseindia.com/',
    }
    base = 'https://nsearchives.nseindia.com/archives/nsccl/span/'
    tried = []
    for version in range(5, 0, -1):
        url = f'{base}nsccl.{date_token}.i{version}.zip'
        tried.append(url)
        try:
            r = requests.get(url, headers=headers, timeout=(6, 45), stream=True)
            content_type = str(r.headers.get('Content-Type') or '').lower()
            status = r.status_code
            if status == 200 and 'text/html' not in content_type:
                payload = r.content
                name = url.rsplit('/', 1)[-1]
                extracted = extract_span_payload(payload, name)
                r.close()
                if extracted is not None:
                    name, data = extracted
                    target = out / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                    print(f'SPAN_FILE={target}')
                    print(f'SOURCE_URL={url}')
                    print(f'BYTES={len(data)}')
                    return
            print(f'SPAN_PROBE status={status} type={content_type} url={url}')
            r.close()
        except Exception as exc:
            print(f'SPAN_PROBE_ERROR url={url} error={type(exc).__name__}:{exc}')

    raise RuntimeError('Could not retrieve an NSE SPAN i1-i5 archive for ' + date_token + '. Tried: ' + ', '.join(tried))


if __name__ == '__main__':
    main()
