"""Small portability helpers shared by command-line entry points."""

from pathlib import Path
import os
from typing import Optional


def path_arg(value: Optional[str], env_name: str, *, required: bool = True) -> Optional[Path]:
    """Resolve a CLI value, then an environment variable, without machine defaults."""
    raw = value or os.environ.get(env_name)
    if not raw:
        if required:
            raise SystemExit(f"Missing path: pass the CLI option or set {env_name}.")
        return None
    return Path(raw).expanduser().resolve()
