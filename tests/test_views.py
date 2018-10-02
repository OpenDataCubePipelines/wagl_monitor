import pytest
import unittest

import re


@pytest.mark.usefixtures("app")
class TestViews(unittest.TestCase):
    app = None  # Placeholder for the fixture

    def validate_dt_page(self, page, model, filters=None):
        client = self.app.test_client()

        resp = client.get(page, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        page_response = resp.get_data().decode('utf-8')

        page_title_results = re.search(
            '<title>(?P<title>.*)</title>', page_response
        )

        self.assertIsNotNone(page_title_results)
        self.assertIn(
            model,
            page_title_results.groupdict().get('title', '')
        )

        api_endpoint = r'/api/monitor/{}/'.format(model)
        if filters:
            for key, value in filters.items():
                api_endpoint += r'{}/{}/'.format(key, value)

        self.assertIn(api_endpoint, page_response)


    def test_root_page(self):
        self.validate_dt_page('/', 'WaglBatch')

    def test_model_view(self):
        models = ('WaglBatchItem', 'WaglBatch', )
        for m in models:
            self.validate_dt_page('/dt/' + m, m)

    def test_model_filter_view(self):
        self.validate_dt_page('/dt/WaglBatch/id/1/', 'WaglBatch', filters={'id': 1})


if __name__ == '__main__':
    unittest.main()
