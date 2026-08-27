import unittest
from unittest.mock import patch

from publication_verify import check_audio_url, probe_audio_ranges


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


class _RangeResponse(_Response):
    def __init__(self, content_range):
        self.headers = _Headers()
        self.headers.get = lambda key, default="": {
            "Content-Type": "audio/mpeg", "Content-Range": content_range,
        }.get(key, default)


class PublicationVerificationTests(unittest.TestCase):
    @patch("publication_verify.urlopen", return_value=_Response())
    def test_verifier_uses_audio_range_probe(self, opener):
        result = check_audio_url("https://cdn.example/chapter_01.mp3")
        self.assertTrue(result.ok)
        request = opener.call_args.args[0]
        self.assertEqual(request.get_header("Range"), "bytes=0-15")

    def test_strict_three_position_probe(self):
        seen = []
        def opener(request, timeout):
            raw = request.get_header("Range")
            seen.append(raw)
            start, end = (int(value) for value in raw.removeprefix("bytes=").split("-"))
            return _RangeResponse(f"bytes {start}-{end}/100")
        results = probe_audio_ranges("https://cdn.example/chapter.mp3", 100, opener=opener)
        self.assertEqual(seen, ["bytes=0-15", "bytes=42-57", "bytes=84-99"])
        self.assertEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()
