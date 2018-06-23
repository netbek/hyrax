# -*- coding: utf-8 -*-
"""Data table view."""
import json
from pyramid.response import Response
from pyramid.view import view_config
from .helpers.utils import to_csv

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


class DataTableViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='data_table_jquery', renderer='data_table_jquery.jinja2')
    def data_table_jquery(self):
        # fieldnames = ['name', 'count']
        # body = to_csv(data, fieldnames)
        # filename = 'data.csv'
        #
        # return Response(body=body, content_type='text/csv',
        #                 content_disposition='attachment; filename="{}"'.format(filename))

        return {
            'data': json.dumps(data)
        }

    @view_config(route_name='data_table_jquery_component', renderer='data_table_jquery_component.jinja2')
    def data_table_jquery_component(self):
        return {
            'data': json.dumps(data)
        }

    @view_config(route_name='data_table_react_component', renderer='data_table_react_component.jinja2')
    def data_table_react_component(self):
        return {
            'data': json.dumps(data)
        }
