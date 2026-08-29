"""Single, fail-closed entry point for reader publication.

The command intentionally separates a read-only preflight from the existing
journaled publisher.  A release can proceed only when the configured modern
manifest publisher is selected and all local release inputs are present.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from deployment_preflight import inspect
from publisher import publish


def load_config(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Cannot read release configuration: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Release configuration must be a JSON object")
    return data


def run(config_path: Path, *, journal: Optional[Path] = None, dry_run: bool = False) -> dict:
    config_path = config_path.expanduser().resolve()
    config = load_config(config_path)
    result = inspect(config_path, Path(config.get("reader_html")).expanduser().parent if config.get("reader_html") else None)
    if result["status"] != "ready":
        raise RuntimeError("release preflight blocked: " + json.dumps(result, ensure_ascii=False))
    if dry_run:
        return {"status": "preflight-passed", "preflight": result}
    journal_result = publish(config, journal)
    return {"status": journal_result.get("status"), "preflight": result, "journal": journal_result}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validated, journaled reader release")
    parser.add_argument("config", type=Path)
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Run all local preflight checks without upload, commit, push, or public verification")
    args = parser.parse_args()
    try:
        result = run(args.config, journal=args.journal, dry_run=args.dry_run)
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"BLOCKED: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
