import json
import altair as alt
from vega_datasets import data
from pyramid.view import view_config


def to_spec(plot):
    return json.dumps(plot.to_dict(), indent=2)


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
        p = alt.Chart('/api/altair?dataset=iris').mark_circle().encode(
            x='petalLength:Q',
            y='sepalLength:Q',
            color='species:N'
        ).properties(
            width=200,
            height=200
        )

        plots.append({
            'title': 'Scatterplot',
            'spec': to_spec(p)
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
            'spec': to_spec(p)
        })

        # Scatterplot matrix
        # https://altair-viz.github.io/gallery/scatter_matrix.html
        p = alt.Chart('/api/altair?dataset=iris').mark_circle().encode(
            alt.X(alt.repeat('column'), type='quantitative'),
            alt.Y(alt.repeat('row'), type='quantitative'),
            color='species:N'
        ).properties(
            width=150,
            height=150
        ).repeat(
            row=['sepalLength', 'sepalWidth', 'petalLength', 'petalWidth'],
            column=['sepalLength', 'sepalWidth', 'petalLength', 'petalWidth']
        ).interactive()

        plots.append({
            'title': 'Scatterplot matrix',
            'spec': to_spec(p)
        })

        return {
            'plots': plots
        }
