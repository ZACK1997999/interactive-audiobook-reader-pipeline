import json
import os
import tempfile
import time
import unittest
from pathlib import Path

from key_pool import KeyPool


class KeyPoolTests(unittest.TestCase):
    def test_empty_pool(self):
        pool = KeyPool([])
        self.assertEqual(pool.total_keys, 0)
        self.assertIsNone(pool.get_active_key())

    def test_load_from_env_comma_and_semicolon(self):
        os.environ["TEST_KEYS"] = "key_aaa, key_bbb; key_ccc"
        pool = KeyPool.from_env(env_var="TEST_KEYS", provider="test")
        self.assertEqual(pool.total_keys, 3)
        self.assertEqual(pool.keys, ["key_aaa", "key_bbb", "key_ccc"])
        self.assertEqual(pool.get_active_key(), "key_aaa")

    def test_load_from_config_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg = Path(tmp_dir) / "config.json"
            cfg.write_text(json.dumps({"api_keys": ["key_1", "key_2", "key_3"]}), encoding="utf-8")
            pool = KeyPool.from_config_file(cfg)
            self.assertEqual(pool.total_keys, 3)
            self.assertEqual(pool.get_active_key(), "key_1")

    def test_key_masking(self):
        pool = KeyPool(["AIzaSyD123456789X"])
        self.assertEqual(pool.mask_key("AIzaSyD123456789X"), "AIza...789X")
        self.assertEqual(pool.mask_key("short"), "***")

    def test_failover_rotation_and_cooldown(self):
        pool = KeyPool(["key_a", "key_b", "key_c"], default_cooldown=5)
        self.assertEqual(pool.get_active_key(), "key_a")

        # Report key_a exhausted
        next_key = pool.report_exhausted("key_a", reason="429 Rate Limit")
        self.assertEqual(next_key, "key_b")
        self.assertEqual(pool.get_active_key(), "key_b")

        # Report key_b exhausted
        next_key = pool.report_exhausted("key_b", reason="Quota Exceeded")
        self.assertEqual(next_key, "key_c")
        self.assertEqual(pool.get_active_key(), "key_c")

        # Report key_c exhausted
        next_key = pool.report_exhausted("key_c", reason="429 Rate Limit")
        self.assertIsNone(next_key)
        self.assertIsNone(pool.get_active_key())

    def test_cooldown_expiry(self):
        pool = KeyPool(["key_fast"], default_cooldown=1)
        self.assertEqual(pool.get_active_key(), "key_fast")
        pool.report_exhausted("key_fast", cooldown_seconds=1)
        self.assertIsNone(pool.get_active_key())

        # Wait for cooldown to expire
        time.sleep(1.1)
        self.assertEqual(pool.get_active_key(), "key_fast")


if __name__ == "__main__":
    unittest.main()
