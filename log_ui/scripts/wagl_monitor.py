import json
import logging
import click

from ..models import WaglBatchItem, Session
from ..models import create_db, drop_db, get_engine
from ..utils import create_app, parse_batches

#logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
LOG_FMT = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
root = logging.getLogger('root')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter(LOG_FMT))
root.addHandler(ch)
logging.basicConfig(level=logging.DEBUG, format=LOG_FMT)
_LOG = logging


@click.group()
@click.option('--settings', default='log_ui.settings.Default')
@click.pass_context
def cli(ctx, settings):
    ctx.obj['settings'] = settings


@cli.command('add-logs')
@click.argument('json-file', type=click.Path(exists=True))
@click.pass_context
def add_logs(ctx, json_file):
    session = None

    app = create_app(ctx.obj['settings'])
    try:
        with app.app_context():
            engine = get_engine()  # binds it to the session
            session = Session()

            with open(json_file, 'r') as fd:
                results = json.loads(fd.read())

            batches = parse_batches(results['batch_results'], session)
            for task in results['task_results']:
                # Swap the batch id recorded on the system with an orm reference
                batch_group_id = task.pop('batch_group_id')
                task['batch'] = batches[batch_group_id]
                session.add(WaglBatchItem(**task))
            
            session.commit()
    except Exception as e:
        _LOG.error(str(e))
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()


@cli.command('init-db')
@click.pass_context
def initdb(ctx):
    with create_app(ctx.obj['settings']).app_context():
        create_db()


@cli.command('destroy-db')
@click.pass_context
def destroydb(ctx):
    with create_app(ctx.obj['settings']).app_context():
        drop_db()


@cli.command('start-server')
@click.pass_context
def start_server(ctx):
    app = create_app(ctx.obj['settings'])
    app.run()


if __name__ == '__main__':
    cli(obj={})
