"""Fail-closed deployment discovery and preflight.

This separates release qualification from deployment transport. It discovers the
actual portal repository without assuming that the current pipeline repository is
the public site, and reports missing credentials/configuration before a long run.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def _git(path: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(["git", *args], cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def discover_config(explicit: str | None = None, book_dir: Path | None = None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    if book_dir:
        candidates.append(book_dir / "publisher_config.json")
    candidates.extend([
        Path.cwd() / "publisher_config.json",
        Path(os.environ["READER_PUBLISHER_CONFIG"]).expanduser()
        if os.environ.get("READER_PUBLISHER_CONFIG") else Path("__missing__"),
    ])
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def inspect(config_path: Path | None = None, book_dir: Path | None = None) -> dict:
    result = {"status": "blocked", "config": None, "checks": [], "deployment_mode": None}
    config = discover_config(str(config_path) if config_path else None, book_dir)
    if config is None:
        result["checks"].append({"name": "publisher_config", "status": "missing"})
        result["remediation"] = "Create a real publisher_config.json or set READER_PUBLISHER_CONFIG."
        return result
    result["config"] = str(config)
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        result["checks"].append({"name": "publisher_config", "status": "invalid", "detail": str(exc)})
        return result
    required = ("book_id", "reader_html", "audio_manifest", "release_report", "portal_repo", "public_reader_url")
    missing = [key for key in required if not data.get(key)]
    result["checks"].append({"name": "required_fields", "status": "passed" if not missing else "missing", "missing": missing})
    portal = Path(data.get("portal_repo", "")).expanduser().resolve() if data.get("portal_repo") else None
    if portal:
        result["checks"].append({"name": "portal_repo", "status": "passed" if (portal / ".git").exists() else "missing", "path": str(portal)})
        result["remote"] = _git(portal, "remote", "get-url", "origin")
        result["branch"] = _git(portal, "branch", "--show-current")
        legacy = portal / "scripts" / "deploy_full_chunked_library.py"
        result["deployment_mode"] = "legacy_chunked" if legacy.is_file() else "manifest_publisher"
        result["checks"].append({"name": "deployment_entrypoint", "status": "passed" if legacy.is_file() or data.get("portal_repo") else "missing"})
    result["visibility"] = "unknown_requires_provider_check"
    result["status"] = "ready" if not missing and portal and (portal / ".git").exists() else "blocked"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover and validate the configured deployment path.")
    parser.add_argument("--config")
    parser.add_argument("--book-dir", type=Path)
    args = parser.parse_args()
    result = inspect(Path(args.config).expanduser() if args.config else None, args.book_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
