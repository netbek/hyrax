from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, output_file, save
from vega_datasets import data
from pyramid.view import view_config


APP_DIR = 'app'
PLOTS_DIR = 'app/cache/plots'
CACHE = False


class BokehViews:
    def __init__(self, request):
        self.request = request


    @view_config(route_name='plots_bokeh', renderer='plots_bokeh.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        df = data('iris')
        source = ColumnDataSource(df)

        # colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
        # colors = [colormap[x] for x in flowers['species']]

        p = figure(title = "Iris Morphology")
        p.xaxis.axis_label = 'petalLength'
        p.yaxis.axis_label = 'sepalLength'

        p.circle(x='petalLength', y='sepalLength', fill_alpha=0.2, size=10, source=source)

        basename = 'iris_scatter'
        filename = '{}/{}.html'.format(PLOTS_DIR, basename)

        # https://bokeh.pydata.org/en/latest/docs/user_guide/embed.html
        save(p, filename)

        return {
            'plots': plots
        }
