import time
import json
import re
from functools import lru_cache

from flask import Flask, jsonify, abort, request, send_from_directory, Blueprint
from flask.views import MethodView

from .models import get_engine, Session, WaglBatch, WaglBatchItem


DEFAULT_LENGTH = 25


def create_datatables_response(model, query, request_args):
    """ Crafts a datatables response from a request """
    limit = request_args.get('length', DEFAULT_LENGTH)
    offset = request_args.get('start', 0)

    try:
        records_before_filter = query.count()
        # Request args are a little cumbersome to read
        for arg in request_args.keys():
            matches = re.match(r'columns\[(?P<idx>[0-9]+)\]\[search\]\[value\]', arg)
            if not matches or not request_args[arg]:
                continue
            column_attr = request_args['columns[{}][data]'.format(matches.groupdict()['idx'])]
            query = (
                query.filter(getattr(model, column_attr).contains(request_args[arg]))
            )

        order_stmts = len(list(filter(lambda s: s.find('order') is 0, request_args.keys()))) // 2
        for i in range(order_stmts):
            order_col_id = request_args['order[{}][column]'.format(i)]
            order_attr = request_args['columns[{}][data]'.format(order_col_id)] 
            order_dir = request_args['order[{}][dir]'.format(i)]

            # TRANSLATED: query = query.order_by(model.order_attr.order_dir())
            query = query.order_by(getattr(getattr(model, order_attr), order_dir)())

        datatable_records = query.count()

        results = (
            query
            .limit(limit)
            .offset(offset)
            .all()
        )

        response = {
            'draw': request_args.get('draw'),
            'recordsTotal': records_before_filter,
            'recordsFiltered': datatable_records,
            'data': results
        }
    except Exception as e:
        response = {
            'error': str(e)
        }

    return jsonify(response)


class DataTableAPI(MethodView):
    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def get(self, filter_attr=None, filter_val=None):
        args = request.args
        session = Session()
        query = session.query(self.model)

        # Apply url filter if requested
        if filter_attr:
            if hasattr(self.model, filter_attr):
                query = query.filter(getattr(self.model, filter_attr)==filter_val)
            else:
                abort(404)

        res = create_datatables_response(self.model, query, args)
        session.close()
        return res


class WaglBatchAPI(DataTableAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(WaglBatch, *args, **kwargs)


class WaglBatchItemAPI(DataTableAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(WaglBatchItem, *args, **kwargs)


def register_api(bp, view, endpoint, url):
    """ Helper function to register initial view and downstream views """
    view_func = view.as_view(endpoint)
    bp.add_url_rule(url, view_func=view_func)
    bp.add_url_rule(
        url + '<string:filter_attr>/<string:filter_val>/',
        view_func=view_func
    )


# TODO add base template
api_bp = Blueprint('api', __name__)
register_api(api_bp, WaglBatchAPI, 'monitor_wagl_batch', '/WaglBatch/')
register_api(api_bp, WaglBatchItemAPI, 'monitor_wagl_batchitem', '/WaglBatchItem/')
