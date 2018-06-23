# -*- coding: utf-8 -*-
"""Data table view."""
import json
from pyramid.response import Response
from pyramid.view import view_config
from .helpers.utils import to_csv


class DataTableViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='data_table', renderer='data_table.jinja2')
    def index(self):
        data = (
            {
                'name': 'Elené Sommerfield',
                'count': 4.6
            },
            {
                'name': 'Leah <Pagani> 🍍',
                'count': None
            },
            {
                'name': 'Lucie "drop \t tables" D\'Ekker',
                'count': -1
            }
        )

        # fieldnames = ['name', 'count']
        # body = to_csv(data, fieldnames)
        # filename = 'data.csv'
        #
        # return Response(body=body, content_type='text/csv',
        #                 content_disposition='attachment; filename="{}"'.format(filename))

        return {
            'data': json.dumps(data)
        }
