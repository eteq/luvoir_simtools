import dask.dataframe as dd
import holoviews as hv
import geoviews as gv
import parambokeh
import param

from colorcet import cm

from bokeh.models import Slider, Button
from bokeh.layouts import layout
from bokeh.io import curdoc
from bokeh.models import WMTSTileSource

from holoviews.operation.datashader import datashade, aggregate, shade
from holoviews.plotting.util import fire
shade.cmap = fire

hv.extension('bokeh')
renderer = hv.renderer('bokeh').instance(mode='server')

# Load data
ddf = dd.read_parquet('/Users/tumlinson/Dropbox/LUVOIR/SYOTools/luvoir_simtools/data/nyc_taxi_hours.parq/').persist()

from bokeh.models import WMTSTileSource
#url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg'
url = 'http://jt-astro.science/PHATZoom/phat_0pix_blur/{Z}/{X}/{Y}.png'
url = 'http://jt-astro.science/PHATZoom/phat_0pix_padded/{Z}/{X}/{Y}.png'
wmts = gv.WMTS(WMTSTileSource(url=url)) # can look at this class to understand details. 

stream = hv.streams.Stream.define('HourSelect', hour=0)()
points = hv.Points(ddf, kdims=['dropoff_x', 'dropoff_y'])
dmap = hv.util.Dynamic(points, operation=lambda obj, hour: obj.select(dropoff_hour=hour).relabel('PHAT 5 pixel blur'),
                       streams=[stream])

# Apply aggregation
aggregated = aggregate(dmap, link_inputs=True, streams=[hv.streams.RangeXY], width=1200, height=600)

# Shade the data
class ColormapPicker(hv.streams.Stream):
    colormap   = param.ObjectSelector(default=cm["fire"],
                                      objects=[cm[k] for k in cm.keys() if not '_' in k])

cmap_picker = ColormapPicker(rename={'colormap': 'cmap'}, name='')
shaded = shade(aggregated, link_inputs=True, streams=[cmap_picker])

# Define PointerX stream, attach to points and declare DynamicMap for cross-section and VLine
pointer = hv.streams.PointerX(x=ddf.dropoff_x.loc[0].compute().iloc[0], source=points)
section = hv.util.Dynamic(aggregated, operation=lambda obj, x: obj.sample(dropoff_x=x),
                          streams=[pointer], link_inputs=False).relabel('')
vline = hv.DynamicMap(lambda x: hv.VLine(x), streams=[pointer])

# Define options
hv.opts("RGB [width=1200 height=600 xaxis=None yaxis=None fontsize={'title': '14pt'}] VLine (color='white' line_width=2)")
hv.opts("Curve [width=150 yaxis=None show_frame=False] (color='black') {+framewise} Layout [shared_axes=False]")

hvobj = (wmts * shaded) #<< section  # Combine it all into a complex layout

### Pass the HoloViews object to the renderer
plot = renderer.get_plot(hvobj, doc=curdoc())

# Combine the bokeh plot on plot.state with the widgets
layout = layout([plot.state], sizing_mode='fixed')
curdoc().add_root(layout)
