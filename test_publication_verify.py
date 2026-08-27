import unittest
from unittest.mock import patch

from publication_verify import check_audio_url


class _Headers:
    def get(self, key, default=""):
        return {
            "Content-Type": "audio/mpeg",
            "Content-Range": "bytes 0-15/100",
        }.get(key, default)


class _Response:
    status = 206
    headers = _Headers()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, amount):
        return b"x" * min(amount, 16)


class PublicationVerificationTests(unittest.TestCase):
    @patch("publication_verify.urlopen", return_value=_Response())
    def test_verifier_uses_audio_range_probe(self, opener):
        result = check_audio_url("https://cdn.example/chapter_01.mp3")
        self.assertTrue(result.ok)
        request = opener.call_args.args[0]
        self.assertEqual(request.get_header("Range"), "bytes=0-15")


if __name__ == "__main__":
    unittest.main()
