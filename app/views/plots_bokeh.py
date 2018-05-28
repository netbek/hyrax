from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from lxml import etree
from vega_datasets import data
from pyramid.view import view_config


APP_DIR = 'app'
PLOTS_DIR = 'app/cache/plots'
CACHE = False


def to_url(filename):
    if filename.startswith(APP_DIR + '/'):
        return filename[len(APP_DIR):]
    return filename


class BokehViews:
    def __init__(self, request):
        self.request = request


    @view_config(route_name='plots_bokeh', renderer='plots_bokeh.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        # Build plot
        df = data('iris')
        source = ColumnDataSource(df)

        species = df['species'].unique()
        fill_color = factor_cmap('species', palette=Category10[len(species)], factors=species)

        hover = HoverTool(tooltips=[
            ('index', '$index'),
            ('petalLength', '@petalLength{0.0}'),
            ('sepalLength', '@sepalLength{0.0}'),
            ('species', '@species'),
        ])

        p = figure(title='Iris Morphology', tools=[hover, 'pan', 'wheel_zoom', 'reset'], active_scroll='wheel_zoom')

        p.xaxis.axis_label = 'petalLength'
        p.yaxis.axis_label = 'sepalLength'

        p.circle(x='petalLength', y='sepalLength', color=fill_color, fill_alpha=0.5, size=10, source=source)

        # Save plot
        script, div = components(p)

        basename = 'iris_scatter'
        filename = '{}/{}.js'.format(PLOTS_DIR, basename)
        url = to_url(filename)

        file = open(filename, 'w')
        file.write(etree.fromstring(script).text)
        file.close()

        plots.append({
            'title': 'Scatterplot',
            'div': div,
            'script_url': url
        })

        return {
            'plots': plots
        }
