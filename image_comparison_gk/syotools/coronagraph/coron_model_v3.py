# Import some standard python packages
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from astropy.io import fits, ascii 
from matplotlib import gridspec
from matplotlib import rc
import pdb
import sys
import os 
from astropy.table import Table, Column
mpl.rc('font', family='Times New Roman')
mpl.rcParams['font.size'] = 25.0

from bokeh.themes import Theme 
import yaml 
from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HBox, VBoxForm, HoverTool, Paragraph, Range1d, Label, DataSource
from bokeh.models.glyphs import Text
from bokeh.layouts import column, row, WidgetBox 
from bokeh.models.widgets import Slider, Panel, Tabs, Div, TextInput, RadioButtonGroup, Select
from bokeh.io import hplot, vplot, curdoc, output_file, show, vform
from bokeh.models.callbacks import CustomJS
from bokeh.embed import components, autoload_server 

import coronagraph as cg  # Import coronagraph model

cwd = os.getenv('LUVOIR_SIMTOOLS_DIR') 

################################
# PARAMETERS
################################

# Integration time (hours)
Dt = 20.0 # - SLIDER

# Telescopes params
diam = 10. # mirror diameter - SLIDER
Res = 70. # resolution - SLIDER
Tsys = 150. # system temperature - SLIDER
owa = 30. #OWA scaling factor - SLIDER
iwa = 2. #IWA scaling factor - SLIDER

# Planet params
alpha = 90.     # phase angle at quadrature
Phi   = 1.      # phase function at quadrature (already included in SMART run)
Rp    = 1.0     # Earth radii - SLIDER 
r     = 1.0     # semi-major axis (AU) - SLIDER 

# Stellar params
Teff  = 5780.   # Sun-like Teff (K)
Rs    = 1.      # star radius in solar radii

# Planetary system params
d    = 10.     # distance to system (pc)  - SLIDER 
Nez  = 1.      # number of exo-zodis  - SLIDER

# Template
template = ''
global template
global Teff
global Ts

################################
# READ-IN DATA
################################

#spec_dict = get_pysynphot_spectra.add_spectrum_to_library() 
#template_to_start_with = 'Earth' 
#spec_dict[template_to_start_with].wave 
#spec_dict[template_to_start_with].flux # <---- these are the variables you need 
#sn = (spec_dict[template_to_start_with].flux * 1.e15 * 36. ) ** 0.5
#junkf = spec_dict[template_to_start_with].flux 
#junkf[spec_dict[template_to_start_with].wave < 1100.] = -999.  
#junkf[spec_dict[template_to_start_with].wave > 1800.] = -999.  
#new_spectrum = ColumnDataSource(data=dict(w=spec_dict[template_to_start_with].wave, f=spec_dict[t#emplate_to_start_with].flux, \
 #                                  w0=spec_dict[template_to_start_with].wave, f0=spec_dict[template_to_start_with].flux, junkf=junkf, sn=sn)) 
#spectrum_template = new_spectrum

# Read-in Earth spectrum file to start 
whichplanet = 'Earth'
if whichplanet == 'Earth':
   fn = 'planets/earth_quadrature_radiance_refl.dat'
   model = np.loadtxt(fn, skiprows=8)
   lamhr = model[:,0]
   radhr = model[:,1]
   solhr = model[:,2]
# Calculate hi-resolution reflectivity
   Ahr   = np.pi*(np.pi*radhr/solhr)
   lammin = min(lamhr)
   lammax = max(lamhr)
   planet_label = ['Synthetic spectrum generated by T. Robinson (Robinson et al. 2011)']



Ahr_ = Ahr
lamhr_ = lamhr
solhr_ = solhr
Teff_ = Teff
Rs_ = Rs


################################
# RUN CORONAGRAPH MODEL
################################

# Run coronagraph with default LUVOIR telescope (aka no keyword arguments)
lam, dlam, A, q, Cratio, cp, csp, cz, cez, cD, cR, cth, DtSNR = \
    cg.count_rates(Ahr, lamhr, alpha, Phi, Rp, Teff, Rs, r, d, Nez, diam, Res, Tsys, iwa, owa,solhr=solhr)
# Calculate background photon count rates
cb = (cz + cez + csp + cD + cR + cth)
# Convert hours to seconds
Dts = Dt * 3600.
# Calculate signal-to-noise assuming background subtraction (the "2")
SNR  = cp*Dts/np.sqrt((cp + 2*cb)*Dts)
# Calculate 1-sigma errors
sig= Cratio/SNR
# Add gaussian noise to flux ratio
spec = Cratio + np.random.randn(len(Cratio))*sig

planet = ColumnDataSource(data=dict(lam=lam, cratio=Cratio*1e9, spec=spec*1e9, downerr=(spec-sig)*1e9, uperr=(spec+sig)*1e9))
textlabel = ColumnDataSource(data=dict(label = planet_label))


################################
# BOKEH PLOTTING
################################

#fixed y axis is bad
snr_ymax = np.max(Cratio)*1e9
snr_plot = Figure(plot_height=400, plot_width=750, 
              tools="crosshair,pan,reset,resize,save,box_zoom,wheel_zoom",
              x_range=[0.2, 3.5], y_range=[-0.2, 2.], toolbar_location='right')
snr_plot.x_range = Range1d(0.2, 3.5, bounds=(0.2, 3.5)) 
snr_plot.y_range = Range1d(-0.2, 2., bounds=(-0.2, 5.0)) 
snr_plot.background_fill_color = "beige"
snr_plot.background_fill_alpha = 0.5
snr_plot.yaxis.axis_label='F_p/F_s (x10^9)' 
snr_plot.xaxis.axis_label='Wavelength [micron]'
snr_plot.title.text = 'Planet Spectrum'

#citation = Label(x=70, y=70, x_units='screen', y_units='screen',
#                 text='label', render_mode='css',
#                 border_line_color='black', border_line_alpha=1.0,
#                 background_fill_color='white', background_fill_alpha=1.0)


snr_plot.line('lam','cratio',source=planet,line_width=2.0, color="green", alpha=0.7)
snr_plot.circle('lam', 'spec', source=planet, fill_color='red', line_color='black', size=8) 
snr_plot.segment('lam', 'downerr', 'lam', 'uperr', source=planet, line_width=1, line_color='grey', line_alpha=0.5) 

#rectangle behind annotation:
snr_plot.quad(top = [-0.1], left=[0.2], right=[3.5], bottom=[-0.2], color="white")

glyph = Text(x=0.25, y=-0.19, text="label", text_font_size='9pt')
textlabel = ColumnDataSource(data=dict(label = 'label'))
snr_plot.add_glyph(textlabel, glyph)

def change_filename(attrname, old, new): 
   format_button_group.active = None 


instruction0 = Div(text="""Specify a filename here:
                           (no special characters):""", width=300, height=15)
text_input = TextInput(value="filename", title=" ", width=100)
instruction1 = Div(text="""Then choose a file format here:""", width=300, height=15)
format_button_group = RadioButtonGroup(labels=["txt", "fits"])
instruction2 = Div(text="""The link to download your file will appear here:""", width=300, height=15)
link_box  = Div(text=""" """, width=300, height=15)


def i_clicked_a_button(new): 
    filename=text_input.value + {0:'.txt', 1:'.fits'}[format_button_group.active]
    print "Your format is   ", format_button_group.active, {0:'txt', 1:'fits'}[format_button_group.active] 
    print "Your filename is: ", filename 
    fileformat={0:'txt', 1:'fits'}[format_button_group.active]
    link_box.text = """Working""" 
 
    t = Table(planet.data)
    t = t['lam', 'spec','cratio','uperr','downerr'] 

    if (format_button_group.active == 1): t.write(filename, overwrite=True) 
    if (format_button_group.active == 0): ascii.write(t, filename)
 
    os.system('gzip -f ' +filename) 
    os.system('cp -rp '+filename+'.gz /home/jtastro/jt-astro.science/outputs') 
    print    """Your file is <a href='http://jt-astro.science/outputs/"""+filename+""".gz'>"""+filename+""".gz</a>. """

    link_box.text = """Your file is <a href='http://jt-astro.science/outputs/"""+filename+""".gz'>"""+filename+""".gz</a>. """


  

def update_data(attrname, old, new):
   #how do I make it so that it will update the spectrum file here but only if it CHANGES?
    print 'Updating model for exptime = ', exptime.value, ' for planet with R = ', radius.value, ' at distance ', distance.value, ' parsec '
    print '                   exozodi = ', exozodi.value, 'diameter (m) = ', diameter.value, 'resolution = ', resolution.value
    print '                   temperature (K) = ', temperature.value, 'IWA = ', inner.value, 'OWA = ', outer.value
    print 'You have chosen planet spectrum: ', template.value
    
    try:
       lasttemplate
    except NameError:
       lasttemplate = 'Earth' #default first spectrum
    global lasttemplate
    global Ahr_
    global lamhr_
    global solhr_
    global Teff_
    global Rs_
    
# Read-in new spectrum file only if changed
#'BBody' variable some of these have in place of solhr is
# because not all of these read in a stellar spectrum from their files
# so the coronagraph model can use a blackbody instead (note: update so that
# it's self-consistently done for stellar types once we get planets around other
# stars if that becomes important, which I think it will)
    if template.value != lasttemplate:
       if template.value == 'Earth':
          fn = cwd+'coronagraph-master/planets/earth_quadrature_radiance_refl.dat'
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          radhr = model[:,1]
          solhr_ = model[:,2]
          Ahr_   = np.pi*(np.pi*radhr/solhr_)
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by T. Robinson (Robinson et al. 2011)']

       if template.value == 'Venus':
          fn = cwd+'coronagraph-master/planets/Venus_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = model[:,2]
          semimajor.value = 0.72
          radius.value = 0.94
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by T. Robinson']


       if template.value =='Archean Earth':
          fn = cwd+'coronagraph-master/planets/ArcheanEarth_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = model[:,2]
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']
          
       if template.value =='Hazy Archean Earth':
          fn = cwd+'coronagraph-master/planets/Hazy_ArcheanEarth_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = model[:,2]
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']


       if template.value =='1% PAL O2 Proterozoic Earth':
          fn = cwd+'coronagraph-master/planets/proterozoic_hi_o2_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = "BBody"
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']
          

       if template.value =='0.1% PAL O2 Proterozoic Earth':
          fn = cwd+'coronagraph-master/planets/proterozoic_low_o2_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = "BBody"
          semimajor.value = 1.
          radius.value = 1.
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by G. Arney (Arney et al. 2016)']

          
       if template.value =='Early Mars':
          fn = cwd+'coronagraph-master/planets/EarlyMars_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = model[:,2]
          semimajor.value = 1.52
          radius.value = 0.53
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by G. Arney based on Smith et al. 2014']

          
       if template.value =='Mars':
          fn = cwd+'coronagraph-master/planets/Mars_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=8)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = 'Bbody'
          semimajor.value = 1.52
          radius.value = 0.53         
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by T. Robinson']

          
       if template.value =='Jupiter':
          fn = cwd+'coronagraph-master/planets/Jupiter_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = 'Bbody'
          semimajor.value = 5.46
          radius.value = 10.97
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
       if template.value =='Saturn':
          fn = cwd+'coronagraph-master/planets/Saturn_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = 'Bbody'
          semimajor.value = 9.55
          radius.value = 9.14
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
       if template.value =='Uranus':
          fn = cwd+'coronagraph-master/planets/Uranus_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = 'Bbody'
          semimajor.value = 19.21
          radius.value = 3.98
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']

          
       if template.value =='Neptune':
          fn = cwd+'coronagraph-master/planets/Neptune_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = 'Bbody'
          semimajor.value = 29.8
          radius.value = 3.86
          Teff_  = 5780.   # Sun-like Teff (K)
          Rs_    = 1.      # star radius in solar radii
          planet_label = ['0.9-0.3 microns observed by Karkoschka et al. (1998); 0.9-2.4 microns observed by Rayner et al. (2009)']


       if template.value =='False O2 Planet (F2V star)':
          fn = cwd+'coronagraph-master/planets/fstarcloudy_geo_albedo.txt'
          model = np.loadtxt(fn, skiprows=0)
          lamhr_ = model[:,0]
          Ahr_ = model[:,1]
          solhr_ = "Bbody"
          semimajor.value = 1.72 #Earth equivalent distance for F star
          radius.value = 1.
          Teff_  = 7050.   # F2V Teff (K)
          Rs_    = 1.3     # star radius in solar radii
          planet_label = ['Synthetic spectrum generated by S. Domagal-Goldman (Domagal-Goldman et al. 2014)']

          
          
       global lammin
       global lammax
       global planet_label
       lammin=min(lamhr_)
       lammax=max(lamhr_)-0.2 #this fixes a weird edge issue

         

          
          
   # if template.value == lasttemplate:
   #    Ahr_ = Ahr
   #    lamhr_ = lamhr
   #    solhr_ = solhr
       #semimajor_ = semimajor.value
       #radius_ = radius.value
       

    # Run coronagraph 
    lam, dlam, A, q, Cratio, cp, csp, cz, cez, cD, cR, cth, DtSNR = \
        cg.count_rates(Ahr_, lamhr_, alpha, Phi, radius.value, Teff_, Rs_, semimajor.value, distance.value, exozodi.value, diameter.value, resolution.value, temperature.value, inner.value, outer.value,  solhr=solhr_, lammin=lammin, lammax=lammax)
    print "ran coronagraph noise model"

    # Calculate background photon count rates
    cb = (cz + cez + csp + cD + cR + cth)
    # Convert hours to seconds
    Dts = exptime.value * 3600.
    # Calculate signal-to-noise assuming background subtraction (the "2")
    SNR  = cp*Dts/np.sqrt((cp + 2*cb)*Dts)
    # Calculate 1-sigma errors
    sig= Cratio/SNR
    # Add gaussian noise to flux ratio
    spec = Cratio + np.random.randn(len(Cratio))*sig
    
    planet.data = dict(lam=lam, cratio=Cratio*1e9, spec=spec*1e9, downerr=(spec-sig)*1e9, uperr=(spec+sig)*1e9)
    textlabel.data = dict(label=planet_label)

    format_button_group.active = None
    lasttemplate = template.value

    print "lam, Cratio, spec, sig"
    for i in range(0, len(lam)):
       print lam[i], ',', Cratio[i], ',', spec[i], ',', sig[i]


######################################
# SET UP ALL THE WIDGETS AND CALLBACKS 
######################################

source = ColumnDataSource(data=dict(value=[]))
source.on_change('data', update_data)
exptime  = Slider(title="Integration Time (hours)", value=20., start=1., end=300.0, step=1.0, callback_policy='mouseup')
exptime.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
distance = Slider(title="Distance (parsec)", value=10., start=1.28, end=50.0, step=0.2, callback_policy='mouseup') 
distance.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
radius   = Slider(title="Planet Radius (R_Earth)", value=1.0, start=0.5, end=20., step=0.1, callback_policy='mouseup') 
radius.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
semimajor= Slider(title="Semi-major axis of orbit (AU)", value=1.0, start=0.1, end=20., step=0.1, callback_policy='mouseup') 
semimajor.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
exozodi  = Slider(title="Number of Exozodi", value = 1.0, start=1.0, end=10., step=1., callback_policy='mouseup') 
exozodi.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
diameter  = Slider(title="Mirror Diameter (meters)", value = 10.0, start=1.0, end=50., step=1., callback_policy='mouseup') 
diameter.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
resolution  = Slider(title="Telescope Resolution (R)", value = 70.0, start=10.0, end=200., step=5., callback_policy='mouseup') 
resolution.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
temperature  = Slider(title="Telescope Temperature (K)", value = 150.0, start=90.0, end=400., step=10., callback_policy='mouseup') 
temperature.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
inner  = Slider(title="Inner Working Angle factor", value = 2.0, start=1.22, end=4., step=0.2, callback_policy='mouseup') 
inner.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")
outer  = Slider(title="Outer Working Angle factor", value = 30.0, start=20, end=100., step=1, callback_policy='mouseup') 
outer.callback = CustomJS(args=dict(source=source), code="""
    source.data = { value: [cb_obj.value] }
""")                                
#select menu for planet
template = Select(title="Planet Spectrum", value="Earth", options=["Earth",  "Archean Earth", "Hazy Archean Earth", "1% PAL O2 Proterozoic Earth", "0.1% PAL O2 Proterozoic Earth","Venus", "Early Mars", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune","False O2 Planet (F2V star)"])


oo = column(children=[exptime, diameter, resolution, temperature, inner, outer]) 
pp = column(children=[template, distance, radius, semimajor, exozodi]) 
qq = column(children=[instruction0, text_input, instruction1, format_button_group, instruction2, link_box]) 

observation_tab = Panel(child=oo, title='Observation')
planet_tab = Panel(child=pp, title='Planet')
download_tab = Panel(child=qq, title='Download')

for w in [text_input]: 
    w.on_change('value', change_filename)
format_button_group.on_click(i_clicked_a_button)

#gna - added this
for ww in [template]: 
    ww.on_change('value', update_data) #changed from update_data to new_template


inputs = Tabs(tabs=[ planet_tab, observation_tab, download_tab ])
curdoc().add_root(row(children=[inputs, snr_plot])) 

#curdoc().theme = Theme(json=yaml.load("""
#attrs:
#    Figure:
#        background_fill_color: '#2F2F2F'
#        border_fill_color: '#2F2F2F'
#        outline_line_color: '#444444'
#    Axis:
#        axis_line_color: "white"
#        axis_label_text_color: "white"
#        major_label_text_color: "green"
#        major_tick_line_color: "white"
#        minor_tick_line_color: "white"
#        minor_tick_line_color: "white"
#    Grid:
#        grid_line_dash: [6, 4]
#        grid_line_alpha: .9
#    Title:
#        text_color: "green"
#""")) 


curdoc().add_root(source) 
