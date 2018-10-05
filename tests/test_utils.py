import unittest

from datetime import datetime

from wagl_monitor.models import WaglBatch
from wagl_monitor.utils import JSONEncoderPlus


class TestJSONEncoder(unittest.TestCase):
    def test_json_encoder(self):
        obj = {
            'test': {
                'batch': WaglBatch(
                    id=5,
                    group_id='abc123',
                    submit_time=datetime(2018, 1, 17),
                    user='test-user',
                ),
                'default': [1, 2, 3]
            }
        }
        json_enc = JSONEncoderPlus()

        data = json_enc.encode(obj)
        expected = (
            '{"test": {"batch": {"id": 5, "group_id": "abc123", '
            '"submit_time": "2018-01-17T00:00:00", "user":'
            ' "test-user", "summary": null}, "default": [1, 2, 3]}}'
        )

        self.assertEqual(data, expected)
        assert data == expected

    def test_unencodable(self):
        class Unencodable:
            pass
        json_enc = JSONEncoderPlus()
        with self.assertRaises(TypeError):
            json_enc.encode(Unencodable())
