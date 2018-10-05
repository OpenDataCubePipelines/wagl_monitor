import pytest
import unittest
import mock

from urllib.parse import urlencode

from .conftest import TEST_DATA


@pytest.mark.usefixtures("app_with_datasets")
class TestApiResults(unittest.TestCase):
    app = None  # Placeholder for fixtures

    def test_results_length(self):
        client = self.app.test_client()
        test_length = 2
        query_string = urlencode({
            'length': test_length,
            'draw': 1
        })
        resp = client.get(
            '/api/monitor/WaglBatch',
            query_string=query_string, 
            follow_redirects=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)

        results = resp.get_json()
        self.assertEqual(len(results['data']), test_length)
        self.assertEqual(results['draw'], '1')

    def test_results_offset(self):
        client = self.app.test_client()

        query_string = urlencode({
            'start': 2,
            'draw': 100
        })
        resp = client.get(
            '/api/monitor/WaglBatch',
            query_string=query_string, 
            follow_redirects=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)
        results = resp.get_json()
        self.assertEqual(results['data'][0]['id'], 3)
        self.assertEqual(results['draw'], '100')

    def test_get_wagl_batches(self):
        client = self.app.test_client()
        resp = client.get('/api/monitor/WaglBatch', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)

        results = resp.get_json()

        self.assertEqual(len(results['data']), len(TEST_DATA['batches']))

    def test_get_wagl_items(self):
        client = self.app.test_client()
        resp = client.get('/api/monitor/WaglBatchItem', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)

        results = resp.get_json()

        self.assertEqual(len(results['data']), len(TEST_DATA['items']))

    def test_missing_model(self):
        client = self.app.test_client()
        resp = client.get(
            '/api/monitor/DoesNotExist',
            follow_redirects=True
        )

        self.assertEqual(resp.status_code, 404)
        self.assertFalse(resp.is_json)

    def test_missing_model_attr_filter(self):
        client = self.app.test_client()
        resp = client.get(
            '/api/monitor/WaglBatchItem/room/15',
            follow_redirects=True
        )

        self.assertEqual(resp.status_code, 404)
        self.assertFalse(resp.is_json)

    def test_attr_filter(self):
        client = self.app.test_client()
        resp = client.get(
            '/api/monitor/WaglBatch/id/1',
            follow_redirects=True
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)

        results = resp.get_json()
        self.assertEqual(len(results['data']), 1)
        self.assertEqual(results['recordsFiltered'], 1)
        self.assertEqual(results['recordsTotal'], 1)

    def test_datatable_filter(self):
        client = self.app.test_client()
        query_string = urlencode({
            'columns[0][data]': 'user',
            'columns[1][data]': 'id',
            'columns[0][search][value]': 'user1',
            'columns[1][search][value]': '',  # test skipping null entry
            'order[0][column]': '1',
            'order[0][dir]': 'desc'
        })

        resp = client.get(
            '/api/monitor/WaglBatch/',
            query_string=query_string,
            follow_redirects=True
        )

        results = resp.get_json()
        self.assertEqual(len(results['data']), 2)
        self.assertTrue(results['data'][0]['id'] > results['data'][1]['id'])
        self.assertEqual(results['recordsFiltered'], 2)
        self.assertEqual(results['recordsTotal'], 3)

    def test_exception_in_results(self):
        with mock.patch('wagl_monitor.web_api.Session', autospec=True) as session_fact:
            # Mock sqlalchemy query
            session_obj = session_fact.return_value
            query_obj = session_obj.query.return_value
            query_obj.count.side_effect = IndexError('Attribute not found')
            client = self.app.test_client()
            resp = client.get(
                '/api/monitor/WaglBatch/',
                follow_redirects=True
            )

            results = resp.get_json()
            self.assertEqual(results['error'], 'Attribute not found')


if __name__ == '__main__':
    unittest.main()
