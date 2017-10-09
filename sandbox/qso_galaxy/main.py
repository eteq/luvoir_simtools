# coding: utf-8
# # Investigating QSOs near Cen A (NGC 5128)
# [Simbad Information for NGC 5128](http://simbad.u-strasbg.fr/simbad/sim-basic?Ident=cen+a&submit=SIMBAD+search)
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import QTable
import astropy.units as u
from astropy.coordinates import SkyCoord # AstroPy treatment of coordinates
from astroquery.simbad import Simbad # SIMBAD query functionality 
import copy 
import os 

from bokeh.plotting import figure, gridplot, output_file, show
from bokeh.models import ColumnDataSource, HoverTool,Paragraph, Range1d
from bokeh.models.widgets import Panel, Tabs, Slider, Div, Button, DataTable, DateFormatter, TableColumn 
from bokeh.io import curdoc
from bokeh.models.widgets import Select 

import cenA_model as q 
import gal_model as g 

cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')

xqso, yqso, mags = q.cenA_model() 
qso_points = ColumnDataSource(data={'xqso':xqso, 'yqso':-1.*yqso, 'x':xqso, 'y':-1.*yqso, 'mag':mags}) 

image1 = "http://www.stsci.edu/~tumlinso/cenA-Fermi-noLabel.jpg" 
p1 = figure(x_range=[0, 586], y_range=[-786, 0], title='Cen A', \
    tools="pan,resize,save,box_zoom,wheel_zoom,reset",toolbar_location='right') 
    
p1.background_fill_color = "white"
p1.image_url(url=[image1], x=[0], y=[0], w=586, h=795, global_alpha=0.95)
p1.x_range = Range1d(0, 586, bounds=(0, 586))  
p1.y_range = Range1d(-795, 0, bounds=(-795,0))
p1.circle('x', 'y', source=qso_points, fill_color='#FFCC66', size=8)

# second panel, arbitrary galaxy 
galaxy, qso = g.gal_model('M87')
galaxy, qso = g.gal_model('M51')
qso_catalog = ColumnDataSource(data={'ra_qso':qso['RA'][0,:], 'dec_qso':qso['DEC'][0,:], 'ra':qso['RA'][0,:], 'dec':qso['DEC'][0,:], \
                                 'redshift':qso['Z'][0,:], 'name':qso['NAME'][0,:], 'fuvmag':qso['FUV_MAG'][0,:], 'nuvmag':qso['NUV_MAG'][0,:] }) 
p2 = figure(x_range=[galaxy['ra'].value-2, galaxy['ra'].value+2.], y_range=[galaxy['dec'].value-2., galaxy['dec'].value+2], title=galaxy['name'], \
    tools="pan,resize,save,box_zoom,wheel_zoom,reset",toolbar_location='right') 
p2.image_url(url=[galaxy['url']], x=[galaxy['ra'].value-2.], y=[galaxy['dec'].value+2], w=4, h=4, global_alpha=0.95)

p2.circle(qso['RA'][0,:], qso['DEC'][0,:], fill_color='#FFCC66', size=8) 
p2.circle('ra_qso', 'dec_qso', source=qso_catalog, fill_color='#FFCC66', size=8, name="qso_points_to_hover")

angular_size_of_150kpc = 150 * 1000. * 206265. / (galaxy['distance'].value * 1e6) / 3600. 
angular_size_of_300kpc = 300 * 1000. * 206265. / (galaxy['distance'].value * 1e6) / 3600. 
rad = p2.circle([galaxy['ra'].value, galaxy['ra'].value], [galaxy['dec'].value, galaxy['dec'].value], fill_color='black', line_color='white',
           line_width=4, radius=[angular_size_of_150kpc, angular_size_of_300kpc], line_alpha=0.8, fill_alpha=0.0)
rad.glyph.line_dash = [6, 6]
hover = HoverTool(names=["qso_points_to_hover"], mode='mouse', tooltips = """ 
            <div>
                <span style="font-size: 20px; font-weight: bold; color:@color">SDSS J</span>
                <span style="font-size: 20px; font-weight: bold; color:@color">@name</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color:@color">z = @redshift</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color:@color">FUV = @fuvmag</span>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color:@color">NUV = @nuvmag</span>
            </div>
              """) 
p2.add_tools(hover)

print(qso.keys()) 
# second panel, arbitrary galaxy 

lookup = {'3.0':18.0, '3':18.0, '6.0':19.2, '6':19.2, '9.0':20.1, '9':20.1, '12':21.0, '12.0':21.0, '15.0':21.8, '15':21.8} 

def update_image(attr,old,new): 
    imag = (qso_points.data['mag'] > lookup[str(aperture.value)])  
    xx = copy.deepcopy(xqso) 
    xx[imag] = xx[imag] + 10000. 
    qso_points.data['x'] = xx 

aperture= Slider(title="Aperture (meters)", value=15., start=3., end=15.0, step=3.0, callback_policy='mouseup', width=550)
aperture.on_change('value', update_image) 

plot1_tab = Panel(child=p1, title='CenA', width=550, height=800)
plot2_tab = Panel(child=p2, title=galaxy['name'], width=550, height=800)

tabs = Tabs(tabs=[plot1_tab,plot2_tab], width=550)  
adf = gridplot([aperture], [tabs]) 

curdoc().add_root(adf)

