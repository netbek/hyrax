from pyramid.view import view_config


class HomeViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='home.jinja2')
    def index(self):
        return {}
