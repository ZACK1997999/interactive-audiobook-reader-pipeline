import json
import tempfile
import unittest
from pathlib import Path

from deployment_preflight import inspect


class DeploymentPreflightTests(unittest.TestCase):
    def test_missing_config_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            result = inspect(book_dir=Path(d))
        self.assertEqual(result["status"], "blocked")

    def test_discovers_legacy_portal_entrypoint(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); portal = root / "portal"; (portal / ".git").mkdir(parents=True)
            (portal / "scripts").mkdir(); (portal / "scripts" / "deploy_full_chunked_library.py").write_text("# fixture")
            config = root / "publisher_config.json"
            config.write_text(json.dumps({"book_id":"demo","reader_html":"x","audio_manifest":"x","release_report":"x","portal_repo":str(portal),"public_reader_url":"https://example.test"}))
            result = inspect(config)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["deployment_mode"], "legacy_chunked")


if __name__ == "__main__":
    unittest.main()
