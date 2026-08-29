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
from typing import Optional


def _git(path: Path, *args: str) -> Optional[str]:
    try:
        return subprocess.check_output(["git", *args], cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def discover_config(explicit: Optional[str] = None, book_dir: Optional[Path] = None) -> Optional[Path]:
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


def inspect(config_path: Optional[Path] = None, book_dir: Optional[Path] = None) -> dict:
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
    required = (
        "book_id", "reader_html", "audio_manifest", "release_report", "intake_plan",
        "portal_repo", "public_reader_url", "git_branch", "hosting_provider",
    )
    missing = [key for key in required if not data.get(key)]
    result["checks"].append({"name": "required_fields", "status": "passed" if not missing else "missing", "missing": missing})
    portal = Path(data.get("portal_repo", "")).expanduser().resolve() if data.get("portal_repo") else None
    path_checks = []
    for key in ("reader_html", "audio_manifest", "release_report", "intake_plan"):
        path = Path(data.get(key, "")).expanduser() if data.get(key) else None
        path_checks.append({"name": key, "status": "passed" if path and path.is_file() else "missing"})
    result["checks"].extend(path_checks)
    if portal:
        result["checks"].append({"name": "portal_repo", "status": "passed" if (portal / ".git").exists() else "missing", "path": str(portal)})
        result["remote"] = _git(portal, "remote", "get-url", "origin")
        result["branch"] = _git(portal, "branch", "--show-current")
        expected_branch = data.get("git_branch")
        result["checks"].append({
            "name": "target_branch",
            "status": "passed" if result["branch"] == expected_branch else "mismatch",
            "expected": expected_branch,
            "actual": result["branch"],
        })
        legacy = portal / "scripts" / "deploy_full_chunked_library.py"
        result["deployment_mode"] = "legacy_chunked" if legacy.is_file() else "manifest_publisher"
        result["checks"].append({
            "name": "deployment_entrypoint",
            "status": "blocked_legacy" if legacy.is_file() else "passed",
            "path": str(legacy) if legacy.is_file() else None,
        })
    result["hosting_provider"] = data.get("hosting_provider")
    result["cloudflare_project"] = data.get("cloudflare_project")
    result["visibility"] = "unknown_requires_provider_check"
    has_missing_paths = any(item["status"] == "missing" for item in path_checks)
    branch_ok = bool(result.get("branch") and result.get("branch") == data.get("git_branch"))
    configured_mode = data.get("deployment_mode", "manifest_publisher")
    modern_entrypoint = configured_mode == "manifest_publisher"
    result["deployment_mode"] = configured_mode
    result["status"] = "ready" if (
        not missing and not has_missing_paths and portal and (portal / ".git").exists()
        and branch_ok and modern_entrypoint and data.get("hosting_provider") == "cloudflare_pages"
        and bool(data.get("cloudflare_project"))
    ) else "blocked"
    if result["status"] == "blocked" and "remediation" not in result:
        result["remediation"] = "Use the manifest-aware publisher and verify the configured Cloudflare Pages project before publishing."
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
