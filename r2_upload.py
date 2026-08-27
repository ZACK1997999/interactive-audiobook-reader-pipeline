"""Manifest-driven R2 upload with environment-only credentials.

Required environment variables:
  R2_ACCESS_KEY_ID
  R2_SECRET_ACCESS_KEY
"""

import argparse
import hashlib
import json
import os
from pathlib import Path


ACCOUNT_ID = "0e3d13022383dca5cd8d30e077ecb593"
BUCKET_NAME = "audible-audio"
ENV_NAMES = ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")
CACHE_CONTROL = "public, max-age=31536000, immutable"


def _settings():
    missing = [name for name in ENV_NAMES if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing R2 environment configuration: " + ", ".join(missing))
    return {name: os.environ[name] for name in ENV_NAMES}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _client(settings):
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("Install deployment support with: pip install -e '.[deployment]'") from exc
    return boto3.client(
        "s3",
        endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=settings["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )


def _is_missing_object(exc: Exception) -> bool:
    response = getattr(exc, "response", {}) or {}
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    code = str(response.get("Error", {}).get("Code", ""))
    return status == 404 or code in {"404", "NoSuchKey", "NotFound"}


def sync_manifest(manifest_path: Path, dry_run: bool = False, client=None) -> dict:
    """Upload only objects whose stored SHA-256 metadata does not match."""
    """Upload exactly the manifest entries; never infer or silently skip files."""
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Audio manifest must contain a non-empty entries list")
    settings = _settings()
    if client is None and not dry_run:
        client = _client(settings)
    uploaded = 0
    skipped = 0
    for entry in entries:
        source = Path(entry["source_path"])
        if not source.is_file():
            raise FileNotFoundError(source)
        actual_hash = _sha256(source)
        expected_hash = entry.get("source_sha256")
        if expected_hash and actual_hash != expected_hash:
            raise RuntimeError(f"audio source changed since manifest creation: {source}")
        if dry_run:
            print(f"DRY-RUN {entry['object_key']}")
            continue
        try:
            remote = client.head_object(Bucket=BUCKET_NAME, Key=entry["object_key"])
        except Exception as exc:
            if not _is_missing_object(exc):
                raise
            remote = None
        remote_hash = (remote or {}).get("Metadata", {}).get("sha256")
        if remote_hash == actual_hash:
            skipped += 1
            print(f"skipped {entry['object_key']} (sha256 match)")
            continue
        client.upload_file(str(source), BUCKET_NAME, entry["object_key"], ExtraArgs={
            "ContentType": "audio/mpeg",
            "CacheControl": CACHE_CONTROL,
            "Metadata": {"sha256": actual_hash},
        })
        uploaded += 1
        print(f"uploaded {uploaded}/{len(entries)} {entry['object_key']}")
    return {"total": len(entries), "uploaded": uploaded, "skipped": skipped, "dry_run": dry_run}


def upload_manifest(manifest_path: Path, dry_run: bool = False) -> int:
    """Backward-compatible count-returning wrapper around SHA-aware sync."""
    receipt = sync_manifest(manifest_path, dry_run=dry_run)
    return receipt["total"] if dry_run else receipt["uploaded"]


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
