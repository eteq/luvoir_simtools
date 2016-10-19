''' 
this is run by typing "bokeh serve --show myapp.py" on the command line 
'''
import numpy as np
import math 

from astropy.table import Table 
import copy  

from bokeh.io import output_file, gridplot 
from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.client import push_session
from bokeh.embed import components, file_html
from bokeh.models import ColumnDataSource, HoverTool, Range1d, Square, Circle 
from bokeh.layouts import Column, Row, WidgetBox
from bokeh.models.glyphs import Text 
from bokeh.models.widgets import Slider, TextInput
from bokeh.io import hplot, vplot, curdoc
from bokeh.models.callbacks import CustomJS


targets = Table.read('data/stark_multiplanet/run_12.0_1.00E-10_3.6_0.1_3.0.fits')  
col = copy.deepcopy(targets['TYPE'][0]) 
col[:] = 'black' 
col[np.where(targets['COMPLETENESS'][0] > 0.2*0.1)] = 'red' 
col[np.where(targets['COMPLETENESS'][0] > 0.5*0.1)] = 'yellow' 
col[np.where(targets['COMPLETENESS'][0] > 0.8*0.1)] = 'lightgreen' 

totyield = np.sum(targets['COMPLETENESS'][0] * 0.1) 

# x0,y0 = original positons, will not be changed 
# x,y = positions that will be modified to hide C = 0 stars in view 
star_points = ColumnDataSource(data=dict(x0=targets['X'][0], \
                                         y0=targets['Y'][0], \
                                         x =targets['X'][0], \
                                         y =targets['Y'][0], \
                                         r =targets['DISTANCE'][0], \
                                         stype=targets['TYPE'][0], \
                                         hip=targets['HIP'][0], \
                                         color=col, \
                                         complete=targets['COMPLETENESS'][0], \
                                         complete0=targets['MPCOMPLETENESS'][0][0], \
                                         complete1=targets['MPCOMPLETENESS'][0][1], \
                                         complete2=targets['MPCOMPLETENESS'][0][2], \
                                         complete3=targets['MPCOMPLETENESS'][0][3], \
                                         complete4=targets['MPCOMPLETENESS'][0][4], \
                                         complete5=targets['MPCOMPLETENESS'][0][5], \
                                         complete6=targets['MPCOMPLETENESS'][0][6], \
                                         complete7=targets['MPCOMPLETENESS'][0][7], \
                                         complete8=targets['MPCOMPLETENESS'][0][8]  \
                                         )) # end of the stars CDS 

rad_circles = ColumnDataSource(data=dict(x=np.array([0., 0., 0., 0.]), y=np.array([0., 0., 0., 0.]), cfrac=[0., 0., 0., 0.], fillcolor=['black', 'black','black','0.342']))

# Set up plot
plot1 = Figure(plot_height=800, plot_width=800, x_axis_type = None, y_axis_type = None,
              tools="pan,reset,resize,save,tap,box_zoom,wheel_zoom", outline_line_color='black', 
              x_range=[-50, 50], y_range=[-50, 50], toolbar_location='right')
hover = HoverTool(names=["star_points_to_hover"], mode='mouse', point_policy="snap_to_data",
     tooltips = """ 
        <div>
            <div>
                <img
                    src="http://www.stsci.edu/~tumlinso/earth_spec.jpg" height="150" alt="@imgs" width="271"
                    style="float: left; margin: 0px 15px 15px 0px;"
                    border="2"
                ></img>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">HIP</span>
                <span style="font-size: 20px; font-weight: bold; color: #696">@hip</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">@stype</span>
                <span style="font-size: 20px; font-weight: bold; color: #696">type</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">D = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@r</span>
                <span style="font-size: 20px; font-weight: bold; color: #696;"> pc</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">C = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete</span>
            </div>
            <span style="font-size: 25px; font-weight: bold; color: #696">-----Rocky-----</span>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Hot = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete0</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Warm = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete1</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Cold = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete2</span>
            </div>
            <span style="font-size: 25px; font-weight: bold; color: #696">-----Neptunes-----</span>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Hot = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete3</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Warm = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete4</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Cold = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete5</span>
            </div>
            <span style="font-size: 25px; font-weight: bold; color: #696">-----Jupiters-----</span>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Hot = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete6</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Warm = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete7</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: #696">Cold = </span>
                <span style="font-size: 20px; font-weight: bold; color: #696;">@complete8</span>
            </div>
        </div>
        """
    )
plot1.add_tools(hover) 
hover = plot1.select(dict(type=HoverTool))
plot1.x_range=Range1d(-50,50,bounds=(-50,50)) 
plot1.y_range=Range1d(-50,50,bounds=(-50,50)) 
plot1.background_fill_color = "black"
plot1.background_fill_alpha = 1.0
plot1.yaxis.axis_label = 'Yield' 
plot1.xaxis.axis_label = ' ' 
plot1.xaxis.axis_line_width = 0
plot1.yaxis.axis_line_width = 0 
plot1.xaxis.axis_line_color = 'black' 
plot1.yaxis.axis_line_color = 'black' 
plot1.border_fill_color = "black"
plot1.min_border_left = 80

# main glyphs for planet circles  
star_syms = plot1.circle('x', 'y', source=star_points, name="star_points_to_hover", \
      fill_color='color', line_color='color', radius=0.5, line_alpha=0.5, fill_alpha=0.7)
star_syms.selection_glyph = Circle(fill_alpha=0.8, fill_color="purple", radius=1.5, line_color='purple', line_width=3)

plot1.text(0.95*0.707*np.array([10., 20., 30., 40.]), 0.707*np.array([10., 20., 30., 40.]), \
     text=['10 pc', '20 pc', '30 pc', '40 pc'], text_color="white", text_font_style='bold', text_font_size='12pt', text_alpha=0.8) 
plot1.text([48.5], [47], ['Chance Of Detecting'], text_color="white", text_align="right", text_alpha=1.0) 
plot1.text([48.5], [44.5], ['an Earth Twin if Present'], text_color="white", text_align="right", text_alpha=1.0) 
plot1.text([48.5], [44.5], ['___________________'], text_color="white", text_align="right", text_alpha=1.0) 
plot1.text(np.array([48.5]), np.array([41.5]), ["80-100%"], text_color='lightgreen', text_align="right") 
plot1.text(np.array([48.5]), np.array([41.5-1*2.4]), ["50-80%"], text_color='yellow', text_align="right") 
plot1.text(np.array([48.5]), np.array([41.5-2*2.4]), ["20-50%"], text_color='red', text_align="right") 
plot1.text(np.array([48.5]), np.array([41.5-3*2.4]), ["Not Observed"], text_color='black', text_align="right") 
plot1.circle([0], [0], radius=0.1, fill_alpha=1.0, line_color='white', fill_color='white') 
plot1.circle([0], [0], radius=0.5, fill_alpha=0.0, line_color='white') 

sym = plot1.circle('x', 'y', source=rad_circles, fill_color='fillcolor', line_color='white', 
           line_width=4, radius=[40,30,20,10], line_alpha=0.8, fill_alpha=0.0) 
sym.glyph.line_dash = [6, 6]

junk_points = ColumnDataSource(data=dict(x=np.arange(21), y=np.zeros(21))) 
plot2 = Figure(plot_height=400, plot_width=450, tools="pan,resize, reset,save", outline_line_color='black', 
              x_range=[0, 20], y_range=[0, 1], toolbar_location='right', title='Detections of 10% Phenomena') 
plot2.title.text_font_size = '14pt' 
plot2.background_fill_color = "beige"
plot2.background_fill_alpha = 0.5 
plot2.yaxis.axis_label = 'Probability' 
plot2.xaxis.axis_label = 'Number of Detections' 
plot2.xaxis.axis_line_width = 2
plot2.yaxis.axis_line_width = 2 
plot2.xaxis.axis_line_color = 'black' 
plot2.yaxis.axis_line_color = 'black' 
plot2.border_fill_color = "white"
plot2.min_border_left = 0
plot2.circle('x', 'y', source=junk_points, \
      fill_color='purple', radius=0.1, line_alpha=0.5, fill_alpha=1.0)
plot2.line('x', 'y', source=junk_points, line_color='purple', line_alpha=0.5) 


#rect_points = ColumnDataSource(data=dict(top=[totyield/2.-50., 9000, 9000], bottom=[-49.8, 8800, 8800], left=[-49.8, 8800, 9000], strbag=' ', right=[-45, 8800, 9200])) 
       
#plot1.quad(top="top", bottom="bottom", left="left", right="right", source=rect_points, color="lightgreen", fill_alpha=0.5, line_alpha=0.) 
#plot1.quad(top=49.9, bottom=-49.9, left=-49.8, right=-45, line_color="lightgreen", line_width=3, fill_alpha=0.0) # open box 
#plot1.circle([-47.4], 'top',source=rect_points, radius=1.8, fill_alpha=0.5, fill_color='lightgreen')
#plot1.text([-47.5], [-50], ['0'], text_color="white", text_align="center") 
#plot1.text([-47.5], [-25], ['50'], text_color="white", text_align="center") 
#plot1.text([-47.5], [0], ['100'], text_color="white", text_align="center") 
#plot1.text([-47.5], [25], ['150'], text_color="white", text_align="center") 
#plot1.text([-47.5], [47], ['200'], text_color="white", text_align="center") 
#plot1.text([-42.5], [47], ['ExoEarth Yield'], text_color="white", text_align="left") 

      
def update_data(attrname, old, new):

    a = aperture.value 
    c = contrast.value 
    i = iwa.value 

    print 'APERTURE A = ', a, ' CONTRAST C = ', c, ' IWA I = ', i 
    apertures = {'4.0':'4.0','4':'4.0','6':'6.0','6.0':'6.0','8':'8.0','8.0':'8.0','10':'10.0','10.0':'10.0','12':'12.0','12.0':'12.0','14':'14.0','14.0':'14.0','16':'16.0'} 
    contrasts = {'-11':'1.00E-11','-10':'1.00E-10','-9':'1.00E-09'} 
    targets = Table.read('data/stark_multiplanet/'+'run_'+apertures[str(a)]+'_'+contrasts[str(c)]+'_3.6_0.1_3.0.fits') 
    star_points.data['complete'] = np.array(targets['COMPLETENESS'][0]) 

    # colors corresponding to yields are updated here 
    col = copy.deepcopy(targets['TYPE'][0]) 
    col[:] = 'black' 
    col[np.where(targets['COMPLETENESS'][0] < 0.2*0.1)] = 'black' 
    col[np.where(targets['COMPLETENESS'][0] > 0.2*0.1)] = 'red' 
    col[np.where(targets['COMPLETENESS'][0] > 0.5*0.1)] = 'yellow' 
    col[np.where(targets['COMPLETENESS'][0] > 0.8*0.1)] = 'lightgreen' 
    star_points.data['color'] = col

    # reset the positions and hide the low completion stars by shifting their X 
    star_points.data['x'] = star_points.data['x0'] 
    star_points.data['y'] = star_points.data['y0'] 
    x = copy.deepcopy(targets['X'][0]) 
    x[col == 'black'] = x[col == 'black'] + 2000. 
    star_points.data['x'] = x 
    
    yield_now = np.sum(targets['COMPLETENESS'][0]) * 0.1 
    rect_points.data['top'] = np.array([yield_now,a,a])/2. - 50. 
    rect_points.data['strbag'] = str(np.sum(np.array(targets['COMPLETENESS'][0]))) 

    # this is the binomial yield stuff 
    d = np.random.binomial(yield_now, 0.1, 10000)
    d0 = np.size(np.where(d == 0)) / 10000. 
    d1 = np.size(np.where(d == 1)) / 10000. 
    d2 = np.size(np.where(d == 2)) / 10000. 
    d3 = np.size(np.where(d == 3)) / 10000. 
    d4 = np.size(np.where(d == 4)) / 10000. 
    d5 = np.size(np.where(d == 5)) / 10000. 
    d6 = np.size(np.where(d == 6)) / 10000. 
    d7 = np.size(np.where(d == 7)) / 10000. 
    d8 = np.size(np.where(d == 8)) / 10000. 
    d9 = np.size(np.where(d == 9)) / 10000. 
    d10= np.size(np.where(d == 10)) / 10000. 
    d11= np.size(np.where(d == 11)) / 10000. 
    d12= np.size(np.where(d == 12)) / 10000. 
    d13= np.size(np.where(d == 13)) / 10000. 
    d14= np.size(np.where(d == 14)) / 10000. 
    d15= np.size(np.where(d == 15)) / 10000. 
    d16= np.size(np.where(d == 16)) / 10000. 
    d17= np.size(np.where(d == 17)) / 10000. 
    d18= np.size(np.where(d == 18)) / 10000. 
    d19= np.size(np.where(d == 19)) / 10000. 
    d20= np.size(np.where(d == 20)) / 10000. 
      
    junk_points.data['y'] = np.array([d0,d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15,d16,d17,d18,d19,d20]) 



source = ColumnDataSource(data=dict(value=[]))
source.on_change('data', update_data)
    
# Set up widgets
aperture= Slider(title="Aperture (meters)", value=12., start=4., end=16.0, step=2.0, callback_policy='mouseup')
aperture.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
contrast = Slider(title="Log (Contrast)", value=-10, start=-11.0, end=-9, step=1.0, callback_policy='mouseup')
contrast.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
iwa      = Slider(title="Inner Working Angle (l/D)", value=1.5, start=1.5, end=4.0, step=0.5, callback_policy='mouseup')
iwa.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
 

# iterate on changes to parameters 
#for w in [aperture, contrast]: 
#    w.on_change('value', update_data)
 
# Set up layouts and add to document
inputs = Column(children=[aperture, contrast, plot2]) 
curdoc().add_root(Row(children=[inputs, plot1], width=1800))
curdoc().add_root(source) 
