import os
import json
import tempfile

import unittest
from click.testing import CliRunner

from wagl_monitor.scripts.wagl_log_extract import cli
from .utils import recursive_regex_test


RAW_LOG_DIR = os.path.join(os.path.dirname(__file__), 'data', 'batchid-a06c27a7')


RAW_LOG_MATCH = {
    'task_results': [{
        'processing_status': 'FAILED',
        'level1': '/g/data/v10/reprocess/ls5/level1/2010/01/LS5_TM_OTH_P51_GALPGS01-002_089_082_20100129',
        'granule': 'LT50890822010029ASA00',
        'failed_task': 'Package',
        'batch_group_id': 'batchid-a06c27a7',
        'job_group_id': 'jobid-ca5b922',
        'exception': "'gqa'",
        'error_log': r'.*/data/batchid-a06c27a7/jobid-ca5b922/errors.log',
        'error_ts': '2018-09-20T15:48:06.543000+10:00'
    }],
    'batch_results': [{
        'group_id': 'batchid-a06c27a7',
        'submit_time': r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        'user': r'[\w\d]+'
    }]
}


class TestLogExtract(unittest.TestCase):

    def test_log_extract(self):
        runner = CliRunner()

        with tempfile.NamedTemporaryFile() as temp:
            result = runner.invoke(
                cli,
                ['--out-file', str(temp.name), str(RAW_LOG_DIR)]
            )

            if result.exit_code:  # not 0
                print(result.output)
                print(result.exception)

            self.assertEqual(result.exit_code, 0)
            temp.seek(0)
            results = json.loads(temp.read().decode('utf-8'))
            recursive_regex_test(results, RAW_LOG_MATCH)
