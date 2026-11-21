import unittest
from backend.api.server import valid_upload, allowed_post, POST_LIMIT

class SecurityTests(unittest.TestCase):
    def test_image_signature_validation(self):
        self.assertTrue(valid_upload('.png', b'\x89PNG\r\n\x1a\n' + b'0' * 20))
        self.assertFalse(valid_upload('.png', b'not really a png'))

    def test_audio_signature_validation(self):
        self.assertTrue(valid_upload('.ogg', b'OggS' + b'0' * 20))
        self.assertFalse(valid_upload('.mp3', b'fake audio'))

    def test_srt_requires_utf8_and_timestamp(self):
        good=b'1\n00:00:01,000 --> 00:00:02,000\nHello\n'
        self.assertTrue(valid_upload('.srt', good))
        self.assertFalse(valid_upload('.srt', b'just text'))

    def test_post_rate_limit(self):
        client='unit-test-client'
        # Isolated IP key; allow exactly the configured number of requests.
        for _ in range(POST_LIMIT):
            self.assertTrue(allowed_post(client))
        self.assertFalse(allowed_post(client))

if __name__ == '__main__':
    unittest.main()
