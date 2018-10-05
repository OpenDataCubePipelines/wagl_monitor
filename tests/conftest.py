import pytest

from datetime import datetime

from wagl_monitor.models import create_db, drop_db, WaglBatch, WaglBatchItem, Session
from wagl_monitor.utils import create_app


TEST_SETTINGS = 'wagl_monitor.settings.TestConfig'


TEST_DATA = {
    'batches': [
        WaglBatch(id=1, group_id='batchid-e879499e', submit_time=datetime(2018, 6, 12, 5, 12), user='user1'),
        WaglBatch(id=2, group_id='batchid-64dadec', submit_time=datetime(2018, 4, 25, 8, 26), user='user1'),
        WaglBatch(id=3, group_id='batchid-f0859b6', submit_time=datetime(2018, 9,1, 17, 4), user='user2')
    ]
}

TEST_DATA['items'] = [
    WaglBatchItem(
        id=1, granule='TEST01', processing_status='FAIL',
        failed_task='DataStandardisation', batch=TEST_DATA['batches'][0],
        job_group_id='jobid-e879499e', exception='Exception', error_ts=TEST_DATA['batches'][0].submit_time
    ),
    WaglBatchItem(
        id=2, granule='TEST02', processing_status='SUCCESS', batch=TEST_DATA['batches'][0],
        job_group_id='jobid-e879499e'
    ),
    WaglBatchItem(
        id=3, granule='TEST03', processing_status='PENDING', batch=TEST_DATA['batches'][0],
        job_group_id='jobid-e879499e'
    ),
    WaglBatchItem(
        id=4, granule='TEST01', processing_status='SUCCESS', batch=TEST_DATA['batches'][1],
        job_group_id='jobid-e8794992'
    ),
    WaglBatchItem(
        id=5, granule='TEST04', processing_status='FAIL',
        failed_task='Packaging', batch=TEST_DATA['batches'][2],
        job_group_id='jobid-e8794997', exception='Exception', error_ts=TEST_DATA['batches'][2].submit_time
    )
]


@pytest.fixture(scope="class")
def app(request):
    """ Create and configure new app instance for each test """
    app = create_app(TEST_SETTINGS)
    with app.app_context():
        engine = create_db()

    request.cls.app = app
    yield app
    with app.app_context():
        drop_db()


@pytest.fixture(scope="class")
def app_with_datasets(request):
    _generator = app(request)
    _app = next(_generator)
    with _app.app_context():
        session = Session()
        for _, object_list in TEST_DATA.items():
            for obj in object_list:
                session.add(obj)
        session.commit()

    yield
    try:
        next(_generator)
    except StopIteration:
        pass
