
# define a telescope class 

import numpy as np 

class Telescope: 

    def __init__(self, aperture,temperature,diff_limit_wavelength):
        self.aperture = 10. # aperture in meters 
        self.temperature = 270. # temperature in Kelvin 
        self.ota_emissivity = 0.09 # emissivity factor for a TMA 
        self.diff_limit_wavelength = 500. # in nanometers 
        diff_limit_in_arcsec = 1.22*(self.diff_limit_wavelength*0.000000001)*206264.8062/self.aperture
    

class Camera(): 

    def __init__(self): 

        self.pivotwave = np.array([155., 228., 360., 440., 550., 640., 790., 1260., 1600., 2220.])
        self.bandnames = ['FUV', 'NUV', 'U','B','V','R','I', 'J', 'H', 'K'] 
        self.R_effective = np.array([5., 5., 5., 5., 5., 5., 5., 5., 5., 5.])

        self.ab_zeropoint = np.array([35548., 24166., 15305., 12523., 10018., 8609., 6975., 4373., 3444., 2482.])

        self.total_qe = np.array([0.1, 0.1, 0.15, 0.45, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6])
        self.aperture_correction = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])
        self.bandpass_r = np.array([5., 5., 5., 5., 5., 5., 5., 5., 5., 5.])
        self.derived_bandpass = self.pivotwave / self.bandpass_r
        self.dark_current = np.array([0.0005, 0.0005, 0.001, 0.001, 0.001, 0.001, 0.001, 0.002, 0.002, 0.002])
        self.detector_read_noise = np.array([3., 3., 3., 3., 3., 3., 3., 4., 4., 4.])

        self.pixel_size = np.array([0.016, 0.016, 0.016, 0.016, 0.016, 0.016, 0.016, 0.04, 0.04, 0.04])

        
    def set_pixel_sizes(self, telescope): 

        self.pixel_size = 1.22*(self.pivotwave*0.000000001)*206264.8062/telescope.aperture / 2. 

        # this enforces the rule that the pixel sizes are set at the shortest wavelength in each channel 

        self.pixel_size[0:2] = 1.22*(self.pivotwave[2]*0.000000001)*206264.8062/telescope.aperture / 2.   # UV set at U 
        self.pixel_size[2:-3] = 1.22*(self.pivotwave[2]*0.000000001)*206264.8062/telescope.aperture / 2.   # Opt set at U 
        self.pixel_size[-3:] = 1.22*(self.pivotwave[7]*0.000000001)*206264.8062/telescope.aperture / 2.   # NIR set at J 