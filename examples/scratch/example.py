# Built-in imports
import os

# 3rd-party imports
import numpy as np

# Local imports
import disort
from pyRT_DISORT.preprocessing.model.model_atmosphere import ModelAtmosphere
from pyRT_DISORT.preprocessing.model.aerosol import Aerosol
from pyRT_DISORT.preprocessing.model.atmosphere import Layers
from pyRT_DISORT.preprocessing.model.aerosol_column import Column, Conrath, GCMProfile
from pyRT_DISORT.preprocessing.observation import Observation
from pyRT_DISORT.preprocessing.controller.output import Output
from pyRT_DISORT.preprocessing.model.phase_function import StaticEmpiricalPhaseFunction, HyperradialHyperspectralEmpiricalPhaseFunction
from pyRT_DISORT.preprocessing.controller.size import Size
from pyRT_DISORT.preprocessing.controller.unsure import Unsure
from pyRT_DISORT.preprocessing.controller.control import Control
from pyRT_DISORT.preprocessing.model.boundary_conditions import BoundaryConditions
from pyRT_DISORT.preprocessing.model.rayleigh import RayleighCo2
from pyRT_DISORT.data.get_data import get_data_path
from pyRT_DISORT.preprocessing.model.surface import HapkeHG2Roughness
from pyRT_DISORT.preprocessing.model.phsfn import PhaseFunction
from pyRT_DISORT.preprocessing.model.phsfn1 import HenyeyGreenstein, EmpiricalPhaseFunction

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make the model atmosphere
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define some files I'll need

phase = os.path.join(get_data_path(), 'planets/mars/aux/dust_phase_functions.npy')
phase_radii = os.path.join(get_data_path(), 'planets/mars/aux/dust_phase_function_radii.npy')
phase_wavs = os.path.join(get_data_path(), 'planets/mars/aux/dust_phase_function_wavelengths.npy')
ice_coeff = os.path.join(get_data_path(), 'planets/mars/aux/legendre_coeff_h2o_ice.npy')
dustfile = os.path.join(get_data_path(), 'planets/mars/aux/dust.npy')
icefile = os.path.join(get_data_path(), 'planets/mars/aux/ice.npy')
#atm = os.path.join(get_data_path(), 'planets/mars/aux/mars_atm.npy')
atm = os.path.join(get_data_path(), 'planets/mars/aux/mars_atm_copy.npy')
altitude_map = os.path.join(get_data_path(), 'planets/mars/aux/altitude_map.npy')
solar_spec = os.path.join(get_data_path(), 'aux/solar_spectrum.npy')
albedo_map = os.path.join(get_data_path(), 'planets/mars/aux/albedo_map.npy')

# Make an aerosol that was observed at these wavelengths
wavs = np.array([1, 9.3])
dust = Aerosol(dustfile, wavs, 9.3)     # 9.3 is the wavelength reference
ice = Aerosol(icefile, wavs, 12.1)

# Get the atmospheric layers
lay = Layers(atm)

# Make a Conrath dust profile, then make a column of dust with that profile
dust_conrath = Conrath(lay, 10, 0.5)   # 10 = scale height, 0.5 = Conrath nu
dust_column = Column(dust, lay, dust_conrath, np.array([1, 1.1, 1.2]), np.array([0.8, 0.2, 0.05]))  # r_eff = 1, column OD = 0.8
# Make a custom ice profile, then make a column of ice with that profile
iceprof = np.where((25 < lay.altitude_layers) & (75 > lay.altitude_layers), 1, 0)   # This is a somewhat cryptic way of making a constant profile at altitudes between 25--75 km
ice_profile = GCMProfile(lay, iceprof)
ice_column = Column(ice, lay, ice_profile, np.array([2]), np.array([5]))

# Make the phase functions. For dust I have phsfn(particle size, wavelengths) but for ice I just have a 1D array of moments
n_moments = 20
dust_hhpf = HyperradialHyperspectralEmpiricalPhaseFunction(phase, dust_column, n_moments, phase_radii, phase_wavs)
ice_pf = StaticEmpiricalPhaseFunction(ice_coeff, ice_column, n_moments)

# TEST: HG
#hg = HenyeyGreenstein(dust_column, 0.5)
#p = PhaseFunction('hg', dust_column, asymmetry=0.5, hg_moments=1000)

# TEST: 1D phase function
#ice_phase = PhaseFunction('epf', ice_column, phase_function_file=ice_coeff)
#ice_new = EmpiricalPhaseFunction(ice_column, phase_function_file=ice_coeff)

# Test 2D: phase function (incomplete)
#p = PhaseFunction('epf', dust_column, phase_function_file=phase, wavelengths_file=dust_phase_wavs)

# Test: 3D phase function
dust_phase = PhaseFunction('epf', dust_column, phase_function_file=phase, particle_sizes_file=phase_radii, wavelengths_file=phase_wavs)
dust_new = EmpiricalPhaseFunction(dust_column, phase_function_file=phase, particle_sizes_file=phase_radii, wavelengths_file=phase_wavs)

print(dust_phase.final_thing.shape)
print(dust_new.coefficients.shape)
print(np.array_equal(dust_phase.final_thing, dust_new.coefficients))







raise SystemExit(42)

# Make Rayleigh stuff
rco2 = RayleighCo2(wavs, lay, n_moments)

# Make the model
model = ModelAtmosphere()
#dust_info = (dust_column.hyperspectral_total_optical_depths, dust_column.hyperspectral_scattering_optical_depths,
#             dust_hhpf.hyperspectral_expanded_pf)
dust_info = (dust_column.hyperspectral_total_optical_depths, dust_column.hyperspectral_scattering_optical_depths,
             dust_phase.final_thing)
#ice_info = (ice_column.hyperspectral_total_optical_depths, ice_column.hyperspectral_scattering_optical_depths,
#            ice_pf.phase_function)
ice_info = (ice_column.hyperspectral_total_optical_depths, ice_column.hyperspectral_scattering_optical_depths,
            ice_phase.final_thing)
rayleigh_info = (rco2.hyperspectral_optical_depths, rco2.hyperspectral_optical_depths, rco2.hyperspectral_layered_phase_function)

# Add dust and ice and Rayleigh scattering to the model
model.add_constituent(dust_info)
model.add_constituent(ice_info)
model.add_constituent(rayleigh_info)

# Once everything is in the model, compute the model. Then, slice off the wavelength dimension
model.compute_model()
optical_depths = model.hyperspectral_total_optical_depths[:, 1]
ssa = model.hyperspectral_total_single_scattering_albedos[:, 1]
polynomial_moments = model.hyperspectral_legendre_moments[:, :, 1]

# Test case 0: Only Rayleigh scattering. Just comment out line 51: model.add_constituent(dust_info) and 88: raise SystemExit
# All I'll say is that at many wavelengths UU matched disort_multi to at least 3 decimal places

# Test case 1.1: Rayleigh scattering is negligible (such as at 9.3 microns) so dust should dominate the ODs
#print(rco2.hyperspectral_optical_depths[:, 1])
#print(dust_column.hyperspectral_total_optical_depths[:, 1])
#print(model.hyperspectral_total_optical_depths[:, 1])

# Test case 1.2: Rayleigh scattering is negligible (such as at 9.3 microns) so dust should dominate the SSAs
#print(model.hyperspectral_total_single_scattering_albedos[:, 1])
#print(dust.hyperspectral_single_scattering_albedos[1])

# Test case 2.1: Rayleigh scattering is significant (such as at 150 nm) so dust + Rayleigh should contribute to the ODs
#print(rco2.hyperspectral_optical_depths[:, 0])
#print(dust_column.hyperspectral_total_optical_depths[:, 0])
#print(model.hyperspectral_total_optical_depths[:, 0])

# Test case 2.2: Rayleigh scattering is significant (such as at 150 nm) so the SSA should be somewhat greater than the dust SSA
#print(rco2.hyperspectral_optical_depths[:, 0])     # Rayleigh OD is 100% scattering OD
#print(dust_column.hyperspectral_scattering_optical_depths[:, 0])    # Get the scattering portion of the dust OD
#print(model.hyperspectral_total_single_scattering_albedos[:, 0])    # Where Rayleigh OD dominates, SSA=1
#print(dust.hyperspectral_single_scattering_albedos[0])   # Rayleigh SSA=1 so this number should always be less than the column SSA

# Test case 3: dust + Rayleigh
# I'm running ./disort_multi -dust_conrath 0.5, 10 -dust_phsfn 98 -use_hg2_thetabar -NSTR 16 -NMOM 128 < testInput.txt
# phsfn_98.dat contain the 65 moments at reff = 1 micron and wavelength = 9.3 microns
# testInput.txt is: 9.3, 0.5, 10, 30, 50, 40, 20, 0.8, 0, 0
#                   0.12, 0.75, 0.9, 1, 0.04, 85.9437

# Test case 4: dust + ice + Rayleigh
# I'm running ./disort_multi -dust_conrath 0.5, 10 -dust_phsfn 98 -ice_phsfn 99 -use_hg2_thetabar -NSTR 16 -zi_top 75 -NMOM 128 < testInput.txt
# phsfn_98.dat contain the 65 moments at reff = 1 micron and wavelength = 9.3 microns
# phsfn_99.dat contains the 128 moments I have for ice
# testInput.txt is: 9.3, 0.5, 10, 30, 50, 40, 20, 0.8, 0.2, 0
#                   0.12, 0.75, 0.5, 1, 0.04, 28.6479

# Get a miscellaneous variable that I'll need later
temperatures = lay.temperature_boundaries

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make a fake observation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
short_wav = 1    # microns
long_wav = 1.1
sza = 50
emission_angle = 40
phase_angle = 20
latitude = 10
longitude = 30
obs = Observation(short_wav, long_wav, sza, emission_angle, phase_angle, latitude, longitude, altitude_map, solar_spec)
phi = np.array([obs.phi])
low_wavenumber = obs.low_wavenumber
high_wavenumber = obs.high_wavenumber
phi0 = obs.phi0
umu0 = obs.mu0
umu = np.array([obs.mu])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make the size of the arrays
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

n_layers = lay.n_layers
n_streams = 16
n_umu = 1
n_phi = len(phi)
n_user_levels = 81
size = Size(n_layers, n_moments, n_streams, n_umu, n_phi, n_user_levels)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make the control class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
control = Control(print_variables=np.array([True, True, True, True, True]))
usrtau = control.user_optical_depths
usrang = control.user_angles
onlyfl = control.only_fluxes
accur = control.accuracy
prnt = control.print_variables
header = control.header
do_pseudo_sphere = control.do_pseudo_sphere
planet_radius = control.radius
deltamplus = control.delta_m_plus

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make the boundary conditions class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
boundary = BoundaryConditions(bottom_temperature=270, top_emissivity=1, lambertian_bottom_boundary=False)
ibcnd = boundary.ibcnd
fbeam = boundary.beam_flux
fisot = boundary.fisot
lamber = boundary.lambertian
plank = boundary.plank
surface_temp = boundary.bottom_temperature
top_temp = boundary.top_temperature
top_emissivity = boundary.top_emissivity

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make the arrays I'm unsure about (for now)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
uns = Unsure(size)
h_lyr = uns.make_h_lyr()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Make the output arrays
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
n_boundaries = 15
output = Output(size)
direct_beam_flux = output.make_direct_beam_flux()
diffuse_down_flux = output.make_diffuse_down_flux()
diffuse_up_flux = output.make_diffuse_up_flux()
flux_divergence = output.make_flux_divergence()
mean_intensity = output.make_mean_intensity()
intensity = output.make_intensity()
albedo_medium = output.make_albedo_medium()
transmissivity_medium = output.make_transmissivity_medium()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Unsorted crap
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
utau = np.zeros(n_user_levels)
# Get albedo (it probably shouldn't go here though...)
albedo = 0.5  #Albedo(albedo_map, obs.latitude, obs.longitude).interpolate_albedo()

# Choose which Hapke surface to use: the default 3 parameter one that comes with DISORT, a 2-lobed HG without roughness,
# or a 2-lobed HG with roughness. The purpose of these classes is to make the rhou, rhoq, bemst, emust, ... arrays
#hapke = Hapke(size, obs, control, boundary, albedo)
#hapke = HapkeHG2(size, obs, control, boundary, albedo, w=0.12, asym=0.75, frac=0.9, b0=1, hh=0.04, n_mug=200)
hapke = HapkeHG2Roughness(size, obs, control, boundary, albedo, w=0.12, asym=0.75, frac=0.5, b0=1, hh=0.04, n_mug=200, roughness=0.5)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run the model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

rfldir, rfldn, flup, dfdt, uavg, uu, albmed, trnmed = disort.disort(usrang, usrtau, ibcnd, onlyfl, prnt, plank, lamber,
                                                                    deltamplus, do_pseudo_sphere, optical_depths,
                               ssa, polynomial_moments, temperatures, low_wavenumber, high_wavenumber, utau, umu0, phi0,
                                                                    umu, phi, fbeam, fisot, albedo,
                               surface_temp, top_temp, top_emissivity, planet_radius, h_lyr, hapke.rhoq, hapke.rhou, hapke.rho_accurate,
                                                                    hapke.bemst, hapke.emust, accur,
                               header, direct_beam_flux, diffuse_down_flux, diffuse_up_flux, flux_divergence,
                                                                    mean_intensity,
                               intensity, albedo_medium, transmissivity_medium)

print(uu[0, :15, 0])   # shape: (1, 81, 1)


# I'm running ./disort_multi -dust_conrath 0.5, 10 -dust_phsfn 98 -ice_phsfn 99 -use_hg2_thetabar -NSTR 16 -zi_top 75 < testInput.txt
# phsfn_98.dat contain the 65 moments at reff = 1 micron and wavelength = 9.3 microns
# phsfn_99.dat contains the 128 moments I have for ice
# testInput.txt is: 9.3, 0.5, 10, 30, 50, 40, 20, 0.8, 0.2, 0
#                   0.12, 0.75, 0.5, 1, 0.04, 28.6479
