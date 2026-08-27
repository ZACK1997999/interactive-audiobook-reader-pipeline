"""Verify published audio using the byte-range request made by HTML5 audio."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class AudioCheck:
    url: str
    status: int
    content_type: str
    content_range: str
    bytes_read: int

    @property
    def ok(self) -> bool:
        return self.status in (200, 206) and self.bytes_read > 0 and self.content_type.startswith("audio/")


def check_audio_url(url: str, probe_bytes: int = 16) -> AudioCheck:
    """Perform a browser-compatible ranged GET; HEAD is intentionally not used."""
    request = Request(
        url,
        headers={
            "Range": f"bytes=0-{probe_bytes - 1}",
            "User-Agent": "immersive-reader-release-verifier/1.0",
        },
    )
    with urlopen(request, timeout=30) as response:
        body = response.read(probe_bytes)
        return AudioCheck(
            url=url,
            status=response.status,
            content_type=response.headers.get("Content-Type", ""),
            content_range=response.headers.get("Content-Range", ""),
            bytes_read=len(body),
        )


def verify_audio_urls(urls: Iterable[str]) -> List[AudioCheck]:
    results = []
    for url in urls:
        try:
            results.append(check_audio_url(url))
        except Exception:
            results.append(AudioCheck(url, 0, "", "", 0))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify published audio byte-range streaming")
    parser.add_argument("urls", nargs="*", help="Public audio URLs to verify")
    parser.add_argument("--manifest", type=Path, help="JSON file containing an 'audio_urls' list")
    args = parser.parse_args()
    urls = list(args.urls)
    if args.manifest:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        urls.extend(data.get("audio_urls", []))
    if not urls:
        parser.error("provide URLs or --manifest")
    results = verify_audio_urls(urls)
    for result in results:
        status = "OK" if result.ok else "FAIL"
        print(f"{status} {result.status} {result.content_type} {result.content_range} {result.url}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
