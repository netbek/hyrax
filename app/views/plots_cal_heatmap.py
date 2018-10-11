import altair as alt
import numpy as np
import pandas as pd
import uuid

from pprint import pprint
from pyramid.view import view_config
from .helpers.plots import to_vega


class CalHeatmapViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='plots_cal_heatmap', renderer='plots_cal_heatmap.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        np.random.seed(24)
        all_days = pd.date_range('1/15/2016', periods=1200, freq='D')
        days = np.sort(np.random.choice(all_days, 50))

        # Year heatmap
        events = pd.Series(np.random.randint(0, 100, size=len(days)), index=days)

        # Get events in first year
        events = events.first('1A')

        full_index = pd.date_range(start=events.index.min() + pd.tseries.offsets.MonthBegin(-1),
                                   end=events.index.max() + pd.tseries.offsets.MonthEnd(0))

        events = events.resample('1D').sum().reindex(full_index).fillna(0)

        def mapper(index, value):
            iso = index.isocalendar()
            # x = 53 if iso[1] == 1 and index.month == 12 else iso[1]
            x = iso[1]
            y = iso[2]
            date = index.strftime('%-d %b %Y')

            return dict(x=x, y=y, value=value, date=date)

        values = [mapper(index, value) for index, value in events.items()]

        # Make a binned color scale
        domain = [0, 1, 10, events.max()]
        range = ['#eee', '#ffffcc', '#ff0000', '#006837']
        scale = alt.Scale(type='bin-linear', domain=domain, range=range)

        p = alt.Chart(alt.Data(values=values)).mark_rect().encode(
            alt.Color('value:Q', bin=True, scale=scale), x='x:N', y='y:N',
            tooltip=['date:N', 'value:Q']).configure_axis(grid=False).configure_view(strokeWidth=0)

        plots.append({
            'title': 'Year heatmap',
            'id': 'plot-{}'.format(uuid.uuid4()),
            'spec': to_vega(p)
        })

        return {
            'plots': plots
        }
