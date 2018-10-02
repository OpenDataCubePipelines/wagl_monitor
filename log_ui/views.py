import json

from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)


@views_bp.route('/', defaults={'model': 'WaglBatch', 'filter_attr': None, 'filter_value': None})
@views_bp.route('/dt/<string:model>/', defaults={'filter_attr': None, 'filter_value': None})
@views_bp.route('/dt/<string:model>/<string:filter_attr>/<string:filter_value>/')
def render_datatable(model, filter_attr, filter_value):
    api_endpoint = '/api/monitor/{}/'.format(model)
    if filter_attr:
        # Add pre-filter to api endpoint if configured
        api_endpoint = api_endpoint + filter_attr + '/' + filter_value + '/'

    column_config = '/static/config/{}.js'.format(model)

    return render_template(
        'monitor-view.html',
        model=model,
        api_endpoint=api_endpoint,
        column_config=column_config
    )
