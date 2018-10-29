import altair as alt

from vega_datasets import data
from pyramid.view import view_config
from .helpers.constants import PNG, SVG
from .helpers.plots import alt_plot, to_vega
from .helpers.utils import get_function_source


def example_scatterplot():
    import altair as alt
    from vega_datasets import data

    df = data.iris()

    p = alt.Chart(df).mark_circle().encode(
        x='petalLength:Q',
        y='sepalLength:Q',
        color='species:N'
    ).properties(
        width=200,
        height=200
    )

    return p


def example_scatterplot_matrix():
    import altair as alt
    from vega_datasets import data

    df = data.iris()

    p = alt.Chart(df).mark_circle().encode(
        x=alt.X(alt.repeat('column'), type='quantitative'),
        y=alt.Y(alt.repeat('row'), type='quantitative'),
        color='species:N'
    ).properties(
        width=150,
        height=150
    ).repeat(
        row=['sepalLength', 'sepalWidth', 'petalLength', 'petalWidth'],
        column=['sepalLength', 'sepalWidth', 'petalLength', 'petalWidth']
    ).interactive()

    return p


@alt_plot
def plot_iris_scatter(data, width=400, height=300):
    p = alt.Chart(data).mark_circle().encode(
        x='petalLength:Q',
        y='sepalLength:Q',
        color='species:N'
    ).properties(
        width=width,
        height=height
    )

    return p, width, height


class AltairViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='api.altair', renderer='json')
    def api(self):
        """Data for the plots"""
        dataset = self.request.params.get('dataset')

        if not dataset:
            raise ValueError('"dataset" value must be given')

        if dataset not in data.list_datasets():
            raise ValueError('Dataset "{}" not found'.format(dataset))

        df = data(dataset)

        return df.to_dict(orient='records')

    @view_config(route_name='plots_altair', renderer='plots_altair.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        # Scatterplot
        plots.append({
            'title': 'Scatterplot',
            'spec': example_scatterplot().to_json(),
            'source': get_function_source(example_scatterplot)
        })

        # Histogram
        # https://altair-viz.github.io/user_guide/transform.html#bin-transforms
        p = alt.Chart('/api/altair?dataset=iris').mark_bar().encode(
            alt.X('binned_field:O', title='sepalLength (binned)'),
            y='count()',
        ).transform_bin(
            'binned_field', field='sepalLength'
        ).properties(
            width=200,
            height=200
        )

        plots.append({
            'title': 'Histogram',
            'spec': to_vega(p)
        })

        # Scatterplot matrix
        # https://altair-viz.github.io/gallery/scatter_matrix.html
        plots.append({
            'title': 'Scatterplot matrix',
            'spec': example_scatterplot_matrix().to_json(),
            'source': get_function_source(example_scatterplot_matrix)
        })

        return {
            'plots': plots
        }
