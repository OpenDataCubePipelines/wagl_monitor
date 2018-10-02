#!/usr/bin/env python3

import logging
import sys
import json
import csv
import enum
import re
import os
from datetime import datetime
from contextlib import contextmanager
from pwd import getpwuid

from collections import defaultdict
from dateutil.tz import tzlocal
from pathlib import Path
import sqlite3
import click

from .utils import JSONEncoderPlus


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
_LOG = logging

TASK_DATABASE_NAME='luigi-task-hist.db'
ERRORS_FILE='errors.log'
TASK_REGEX = f'.*/(?P<batch_group_id>batchid-[a-z0-9]+)/(?P<job_group_id>jobid-[a-z0-9]+)/{TASK_DATABASE_NAME}$'
DB_ITERATION_COUNT = 200

QUERY__GET_TASKS = '''\
SELECT MAX(
    CASE event_name
    WHEN 'PENDING' then 0
    WHEN 'RUNNING' then 1
    WHEN 'FAILED'  then 2
    WHEN 'DONE'    then 3
    END
) as processing_status, tp.level1 as 'level1', tp.granule as 'granule', ft.name as 'failed_task'
FROM (
    -- Retrieve all package tasks
    SELECT id as task_id
    FROM tasks
    WHERE name='Package'
) as pt
-- Get the Status for each package task
JOIN task_events te ON te.task_id = pt.task_id
JOIN (
    -- Get the level1 and granule parameters for each task
    SELECT task_id,
        group_concat(CASE name WHEN 'level1' THEN value ELSE NULL END) as level1,
        group_concat(CASE name WHEN 'granule' THEN value ELSE NULL END) as granule
    FROM task_parameters
    WHERE name in ('level1', 'granule')
    GROUP BY task_id
) as tp ON pt.task_id = tp.task_id 
LEFT JOIN (
    -- Get which task the job failed at
    SELECT tt.name, tp.value as 'granule'
    FROM task_events te1
    LEFT JOIN task_events te2
        ON te1.task_id = te2.task_id AND te2.ts > te1.ts
    JOIN tasks tt ON tt.id = te1.task_id
    JOIN task_parameters tp ON tp.task_id = te1.task_id AND tp.name = 'granule'
    WHERE te2.id IS NULL and te1.event_name = 'FAILED'
) as ft ON ft.granule = tp.granule AND te.event_name != 'DONE'
GROUP BY tp.level1, tp.granule, ft.name;
'''


def dict_factory(cursor, row):
    """ Used to pull results from sqlite as a dictionary """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def database_iter(base_dir, filename=TASK_DATABASE_NAME):
    """ Find the database files from a base directory """
    for path in Path(base_dir).rglob('*/' + TASK_DATABASE_NAME):
        yield path


@contextmanager
def connect_sqlite(*args, **kwargs):
    """ Establish a sqlite connection; we're just reading task state """
    db = kwargs.pop('database', None)
    conn = None
    if not db and args:
        db = args[0]
    elif not db:
        raise ValueError("Please specify a database connection")
    
    try:
        _LOG.debug('Connecting to %s', str(db))
        _LOG.debug('Args: %s, Kwargs: %s', str(args), str(kwargs))
        conn = sqlite3.connect(db, *args, **kwargs)
        conn.row_factory = dict_factory
        yield conn
    finally:
        if conn:
            conn.close()


def parse_error_file(error_file, split_term='}\n', start_term='{'):
    """ Parses the error file to return a summary of events """
    raw_errors = []
    results = defaultdict(dict)

    with open(error_file, 'r') as fd:
        raw_errors = fd.read().split(split_term)

    for r_error in raw_errors:
        if not r_error:
            continue  # Skip the last line

        # Based on format being %Y-%m-%d %H:%M:%S,%f: ERROR: {
        *date_parts, r_json = r_error.split(':', 3)
        log_date = (
            datetime.strptime(':'.join(date_parts), '%Y-%m-%d %H:%M:%S,%f')
            .replace(tzinfo=tzlocal())
        )

        p_error = json.loads(r_json[r_json.index(start_term):] + split_term.strip())
        if 'params' in p_error and 'granule' in p_error['params']:
            result_ref = results[p_error['params']['granule']]

            # Records are broken up by granule to account for the sentinel-2 multi-granules
            # Records are broken up by task to account for luigi's retry behaviour
            # Timestamps are considered so we aren't dependent on serialisation method of runtime
            # If there are still duplicates take the later timestamp; there is further investigation
            # Required on luigi task retry behaviour
            if p_error['task'] not in result_ref or log_date > result_ref[p_error['task']]['error_ts']:
                result_ref[p_error['task']] = {
                    'exception': p_error['exception'],
                    'error_log': error_file,
                    'error_ts': log_date
                }
            else:
                _LOG.debug('Dropping duplicate %s:%s at time:%s', error_file, p_error['params']['granule'], log_date)
        else:
            _LOG.error('Unable to parse %s:%s', error_file, r_error.split('\n')[0])

    return results


@click.command()
@click.argument('base-dir', type=click.Path(exists=True, resolve_path=True))
@click.option('--out-file', type=click.Path(exists=False), default='wagl-processed-logs.json')
def entrypoint(base_dir, out_file):
    _LOG.debug('Starting application')
    results = {
        'task_results': [],
        'batch_results': {}
    }

    for _db in database_iter(base_dir):
        db_path = _db.resolve().as_posix()
        db_attrs = re.match(TASK_REGEX, db_path).groupdict()

        # Use batch directory modified time as a proxy for the job submit time
        # identify the directory by looking at the next delimiter after batchid
        batch_dir_stats = os.stat(db_path[:dp_path.index('/', db_path.index('batchid'))])
        batch_mtime = datetime.fromtimestamp(batch_dir_stats.mtime).replace(tzinfo=tzlocal())
        batch_user = getpwuid(batch_dir_stats.st_uid).pw_name

        if db_attrs['batch_group_id'] not in results['batch_results']:
            results['batch_results'][db_attrs['batch_group_id']] = {
                'group_id': db_attrs['batch_group_id'],
                'submit_time': batch_mtime.isoformat(),
                'user': batch_user
            }

        # Use a known offset to determine error file;
        errorfile = '/'.join(db_path.split('/')[:-1] + [ERRORS_FILE])
        errors = parse_error_file(errorfile)

        with connect_sqlite(database=db_path) as conn:
            cur = conn.cursor()
            cur.execute(QUERY__GET_TASKS)
            while True:
                tasks = cur.fetchmany(DB_ITERATION_COUNT)
                if not tasks:
                    break
                for task in tasks:
                    # Add in the job_group_id and batch_group_id fields
                    task.update(db_attrs)
                    # Add errors if the task did not complete and errors exist
                    # If the job exited without registering a fail the errors won't exist
                    if task['processing_status'] != 3 and task['failed_task'] in errors[task['granule']]:
                        task.update(errors[task['granule']][task['failed_task']])
                    else:
                        # Add null values for the csv
                        task.update({
                            'exception': None,
                            'error_log': None,
                            'error_ts': None
                        })
                    results['task_results'].append(task)

    results['batch_results'] = list(results['batch_results'].values())  # convert from dict to list
    with open(out_file, 'w') as fd:
        fd.write(json.dumps(results, cls=JSONEncoderPlus))


if __name__ == '__main__':
    entrypoint()
