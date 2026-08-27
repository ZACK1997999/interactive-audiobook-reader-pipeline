"""API Key Failover Pool with automatic rotation and rate-limit cooldown.

Supports rotating multiple API keys across LLM/API workers (Gemini, OpenAI, etc.)
when encountering 429 Too Many Requests, QuotaExceeded, or RateLimit errors.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import List, Optional


class KeyPool:
    """Manages a pool of API keys with intelligent failover and cooldown."""

    def __init__(
        self,
        keys: Optional[List[str]] = None,
        provider: str = "generic",
        default_cooldown: int = 60,
    ):
        self.provider = provider
        self.default_cooldown = default_cooldown
        # Clean and deduplicate keys while preserving order
        raw_keys = [k.strip() for k in (keys or []) if k and k.strip()]
        seen = set()
        self.keys: List[str] = []
        for k in raw_keys:
            if k not in seen:
                seen.add(k)
                self.keys.append(k)

        self._active_index: int = 0
        # Map key -> cooldown expiry timestamp (epoch float)
        self._cooldowns: dict[str, float] = {}

    @classmethod
    def from_env(
        cls,
        env_var: str = "GEMINI_API_KEYS",
        fallback_env: str = "GEMINI_API_KEY",
        provider: str = "gemini",
        default_cooldown: int = 60,
    ) -> KeyPool:
        """Load keys from a comma-separated env var or fallback single key."""
        keys_str = os.environ.get(env_var) or os.environ.get(fallback_env) or ""
        keys = [k.strip() for k in keys_str.replace(";", ",").split(",") if k.strip()]
        return cls(keys=keys, provider=provider, default_cooldown=default_cooldown)

    @classmethod
    def from_config_file(
        cls,
        config_path: Path | str,
        key_field: str = "api_keys",
        fallback_field: str = "api_key",
        provider: str = "gemini",
    ) -> KeyPool:
        """Load keys from a JSON config file."""
        p = Path(config_path)
        if not p.is_file():
            return cls([], provider=provider)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return cls([], provider=provider)
            keys = data.get(key_field)
            if isinstance(keys, list):
                return cls(keys=[str(k) for k in keys], provider=provider)
            single_key = data.get(fallback_field)
            if single_key and isinstance(single_key, str):
                return cls(keys=[single_key], provider=provider)
        except Exception:
            pass
        return cls([], provider=provider)

    @property
    def total_keys(self) -> int:
        return len(self.keys)

    def mask_key(self, key: str) -> str:
        """Return a safe masked version of the key for logging."""
        if not key or len(key) < 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"

    def get_active_key(self) -> Optional[str]:
        """Return the current active key that is not in cooldown, or None if all are cooling down."""
        if not self.keys:
            return None

        now = time.time()
        # Clean expired cooldowns
        self._cooldowns = {k: exp for k, exp in self._cooldowns.items() if exp > now}

        # Check from current index forward
        for i in range(len(self.keys)):
            idx = (self._active_index + i) % len(self.keys)
            key = self.keys[idx]
            if key not in self._cooldowns:
                self._active_index = idx
                return key

        return None

    def report_exhausted(
        self,
        key: str,
        cooldown_seconds: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Optional[str]:
        """Mark a key as rate-limited/exhausted, advance to next key, and return the new active key."""
        cd = cooldown_seconds if cooldown_seconds is not None else self.default_cooldown
        now = time.time()
        self._cooldowns[key] = now + cd

        # Advance active index
        if self.keys:
            self._active_index = (self._active_index + 1) % len(self.keys)

        next_key = self.get_active_key()
        masked_old = self.mask_key(key)
        if next_key:
            masked_new = self.mask_key(next_key)
            print(
                f"[{self.provider.upper()}_KEY_POOL] Key {masked_old} rate-limited/exhausted ({reason or '429'}). "
                f"Failing over to Key {masked_new} (available keys: {len(self.keys) - len(self._cooldowns)}/{len(self.keys)})."
            )
        else:
            earliest_exp = min(self._cooldowns.values()) if self._cooldowns else now + cd
            wait_time = max(1.0, earliest_exp - now)
            print(
                f"[{self.provider.upper()}_KEY_POOL] All {len(self.keys)} keys are cooling down. "
                f"Earliest key will recover in {wait_time:.1f}s."
            )
        return next_key

    def wait_for_available_key(self, max_wait: float = 300.0) -> Optional[str]:
        """Block until at least one key comes out of cooldown or max_wait is exceeded."""
        key = self.get_active_key()
        if key:
            return key

        if not self.keys:
            return None

        start_time = time.time()
        while time.time() - start_time < max_wait:
            now = time.time()
            if not self._cooldowns:
                return self.get_active_key()
            earliest_exp = min(self._cooldowns.values())
            wait_secs = max(0.5, min(5.0, earliest_exp - now + 0.1))
            time.sleep(wait_secs)
            key = self.get_active_key()
            if key:
                return key

        return None
