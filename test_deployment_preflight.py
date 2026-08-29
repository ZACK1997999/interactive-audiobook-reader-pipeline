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
            for name in ("reader.html", "audio.json", "report.json", "intake.json"):
                (root / name).write_text("{}")
            config = root / "publisher_config.json"
            config.write_text(json.dumps({"book_id":"demo","reader_html":str(root/"reader.html"),"audio_manifest":str(root/"audio.json"),"release_report":str(root/"report.json"),"intake_plan":str(root/"intake.json"),"portal_repo":str(portal),"public_reader_url":"https://example.test","git_branch":"main","hosting_provider":"cloudflare_pages"}))
            result = inspect(config)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["deployment_mode"], "legacy_chunked")


if __name__ == "__main__":
    unittest.main()
