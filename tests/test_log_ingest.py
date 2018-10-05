import os

import unittest
import mock
import pytest
import sys

from click.testing import CliRunner

from wagl_monitor.scripts.wagl_log_results import cli
from wagl_monitor.models import Session, WaglBatch, WaglBatchItem

from .conftest import TEST_SETTINGS

PROCESSED_LOG = os.path.join(os.path.dirname(__file__), 'data', 'processed-logs.json')


# TODO tests for log extraction; sqlite:memory + logs

@pytest.mark.usefixtures("app")
class TestLogIngest(unittest.TestCase):
    app = None  # placeholder for fixtures

    def test_log_ingest(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['--settings', TEST_SETTINGS, 'add-logs', str(PROCESSED_LOG)],
            obj=dict()
        )
        if result.exit_code:  # not 0
            print(result.output)
            print(result.exception)
        self.assertEqual(result.exit_code, 0)

        session = Session()
        batch_count = session.query(WaglBatch).count()
        item_count = session.query(WaglBatchItem).count()
        session.query(WaglBatch).delete()
        session.query(WaglBatchItem).delete()
        session.commit()
        session.close()

        self.assertEqual(batch_count, 1)
        self.assertEqual(item_count, 3)


if __name__ == '__main__':
    unittest.main()
