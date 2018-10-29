from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response


def main(global_config, **settings):
    config = Configurator(settings=settings)

    # Jinja2
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path('templates/')

    # Static files
    config.add_static_view(name='cache', path='cache')
    config.add_static_view(name='node_modules', path='../node_modules')

    # Routes
    config.add_route('home', '/')

    config.add_route('plots_altair', '/altair')
    config.add_route('api.altair', '/api/altair')

    config.add_route('plots_bokeh', '/bokeh')
    config.add_route('api.bokeh', '/api/bokeh')

    config.add_route('plots_ggplot2', '/ggplot2')

    config.add_route('plots_seaborn', '/seaborn')

    config.add_route('data_table_jquery', '/data-table-jquery')
    config.add_route('data_table_jquery_component', '/data-table-jquery-component')
    config.add_route('data_table_react_component', '/data-table-react-component')

    # Views
    config.scan()

    return config.make_wsgi_app()
