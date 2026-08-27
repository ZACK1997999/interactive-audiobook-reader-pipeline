import json
import unittest
from pathlib import Path


class FailureLedgerTests(unittest.TestCase):
    def test_every_ledger_entry_has_a_regression_test(self):
        path = Path(__file__).with_name("failure_ledger.json")
        ledger = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(ledger["schema_version"], 1)
        self.assertTrue(ledger["entries"])
        for entry in ledger["entries"]:
            self.assertRegex(entry["id"], r"^[A-Z]+-\d{3}$")
            self.assertTrue(entry["failure"].strip())
            self.assertTrue(entry["prevention"].strip())
            self.assertTrue(entry["regression_tests"])
            for test_ref in entry["regression_tests"]:
                test_file, test_name = test_ref.split("::")
                self.assertTrue(Path(__file__).with_name(test_file).exists())
                self.assertIn(f"def {test_name.split('.')[-1]}", Path(__file__).with_name(test_file).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
