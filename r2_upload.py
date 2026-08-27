"""Manifest-driven R2 upload with environment-only credentials.

Required environment variables:
  CLOUDFLARE_R2_ACCOUNT_ID
  CLOUDFLARE_R2_ACCESS_KEY_ID
  CLOUDFLARE_R2_SECRET_ACCESS_KEY
  CLOUDFLARE_R2_BUCKET
"""

import argparse
import json
import os
from pathlib import Path


ENV_NAMES = (
    "CLOUDFLARE_R2_ACCOUNT_ID",
    "CLOUDFLARE_R2_ACCESS_KEY_ID",
    "CLOUDFLARE_R2_SECRET_ACCESS_KEY",
    "CLOUDFLARE_R2_BUCKET",
)


def _settings():
    missing = [name for name in ENV_NAMES if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing R2 environment configuration: " + ", ".join(missing))
    return {name: os.environ[name] for name in ENV_NAMES}


def upload_manifest(manifest_path: Path, dry_run: bool = False) -> int:
    """Upload exactly the manifest entries; never infer or silently skip files."""
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Audio manifest must contain a non-empty entries list")
    settings = _settings()
    if dry_run:
        for entry in entries:
            source = Path(entry["source_path"])
            if not source.is_file():
                raise FileNotFoundError(source)
            print(f"DRY-RUN {entry['object_key']}")
        return len(entries)

    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("Install deployment support with: pip install -e '.[deployment]'") from exc
    client = boto3.client(
        "s3",
        endpoint_url=f"https://{settings['CLOUDFLARE_R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=settings["CLOUDFLARE_R2_ACCESS_KEY_ID"],
        aws_secret_access_key=settings["CLOUDFLARE_R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )
    uploaded = 0
    for entry in entries:
        source = Path(entry["source_path"])
        if not source.is_file():
            raise FileNotFoundError(source)
        client.upload_file(str(source), settings["CLOUDFLARE_R2_BUCKET"], entry["object_key"], ExtraArgs={"ContentType": "audio/mpeg"})
        uploaded += 1
        print(f"uploaded {uploaded}/{len(entries)} {entry['object_key']}")
    return uploaded


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload an explicit audio manifest to Cloudflare R2")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(f"processing {args.manifest}")
    print(f"entries: {upload_manifest(args.manifest, dry_run=args.dry_run)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
