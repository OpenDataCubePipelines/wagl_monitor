from datetime import datetime

from flask import Flask
from flask.json import JSONEncoder

from .models import WaglBatch
from .web_api import api_bp
from .views import views_bp


class JSONEncoderPlus(JSONEncoder):
    """ Adds model serialisation to jsonify """
    def default(self, obj):
        if hasattr(obj, 'to_dict') and callable(obj.to_dict):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(self, obj)


def create_app(config='log_ui.settings.Default'):
    app = Flask(__name__)
    app.config.from_object(config)
    app.json_encoder = JSONEncoderPlus
    app.register_blueprint(api_bp, url_prefix='/api/monitor')
    app.register_blueprint(views_bp, url_prefix='/')

    return app


def parse_batches(batch_list, session):
    """ Returns a list of batch objects from a list """
    batches = {}

    for batch_args in batch_list:
        batch = session.query(WaglBatch).filter(
            WaglBatch.group_id==batch_args['group_id'],
            WaglBatch.submit_time==batch_args['submit_time']
        ).first()
        if not batch:
            batch = WaglBatch(
                group_id=batch_args['group_id'],
                submit_time=batch_args['submit_time'],
                user=batch_args['user']
            )
        batches[batch_args['group_id']] = batch

    return batches
