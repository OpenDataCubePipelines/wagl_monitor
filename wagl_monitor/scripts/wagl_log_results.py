import json
import logging
import click
import webbrowser
import random
import threading

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
@click.option(
    '--settings',
    default='wagl_monitor.settings.DefaultConfig',
    help='Settings file to use for monitor tool'
)
@click.pass_context
def cli(ctx, settings):
    """
    Scripts to manage the monitoring tool
    """
    if not hasattr(ctx, 'obj') or not ctx.obj:
        ctx.obj = dict()
    ctx.obj['settings'] = settings


@cli.command('add-logs', help='Sync processed log file to monitoring database')
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


@cli.command('init-db', help='Create database schema')
@click.confirmation_option(help='Are you sure you want to create the schema?')
@click.pass_context
def init_db(ctx):
    with create_app(ctx.obj['settings']).app_context():
        create_db()
    click.echo("Initialised the database")


@cli.command('drop-db', help='Teardown database')
@click.confirmation_option(help='Are you sure you want to drop the database?')
@click.pass_context
def drop_db(ctx):
    with create_app(ctx.obj['settings']).app_context():
        drop_db()
    click.echo("Dropped the database")


@cli.command('start-server', help='Start webserver')
@click.option('--no-browser', is_flag=True)
@click.pass_context
def start_server(ctx, no_browser):
    port = None
    if not no_browser:
        port = 5000 + random.randint(0, 999)
        threading.Timer(
            1.25, 
            lambda: webbrowser.open('http://localhost:'+ str(port))
        ).start()
    # bind engine
    app = create_app(ctx.obj['settings'])
    # Configure the session
    get_engine(app.config.get('DATABASE_URI'))

    app.run(port=port)


if __name__ == '__main__':
    cli(obj={})
