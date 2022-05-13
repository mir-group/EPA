import numpy as np

from BoltzTraP2 import dft
from BoltzTraP2 import sphere
from BoltzTraP2 import fite
from BoltzTraP2 import bandlib
from BoltzTraP2 import units

dirname = './'
fepa = dirname + 'silicon.epa.e'
ftr = dirname + 'silicon_epa.trace'
fct = dirname + 'silicon_epa.condtens'
RYDBERG = 0.5
doping_level = 0.01

ecut, efcut, deltae, tmax, deltat, lpfac = 1.0 * RYDBERG, 0.3 * RYDBERG, 0.0005 * RYDBERG, 1200.0, 10.0, 5

# Load the input
data = dft.DFTData(dirname)
# Select the interesting bands
data.bandana(emin=data.fermi - ecut, emax=data.fermi + ecut)
# Set up a k point grid with roughly five times the density of the input
equivalences = sphere.get_equivalences(data.atoms, data.magmom, len(data.kpoints) * lpfac)
# Perform the interpolation
coeffs = fite.fitde3D(data, equivalences)

lattvec = data.get_lattvec()
eband, vvband, cband = fite.getBTPbands(equivalences, coeffs, lattvec)
epsilon, dos, vvdos, cdos = bandlib.BTPDOS(eband, vvband, erange=[data.fermi - ecut, data.fermi + ecut], npts=round(2 * ecut / deltae), scattering_model='uniform_tau')

# Define the temperatures and chemical potentials we are interested in
#Tr = np.arange(deltat, tmax + deltat / 2, deltat)
#mur_indices = np.logical_and(epsilon > data.fermi - efcut, epsilon < data.fermi + efcut)
#mur = epsilon[mur_indices]

Tr = np.arange(deltat, tmax + deltat / 2, deltat)
mur = np.empty_like(Tr)
_nelect = data.nelect
for iT, T in enumerate(Tr):
    mur[iT] = bandlib.solve_for_mu(epsilon, dos, _nelect - doping_level, T, data.dosweight, refine=True)

    # The flow from this point is again similar to that in parse_integrate,
    # with the exception that the chemical potentials are different for
    # each temperature.

N = np.empty_like(Tr)
L0, L1, L2 = (np.empty((Tr.shape[0], 3, 3)) for ii in range(3))
Lm11 = np.empty((Tr.shape[0], 3, 3, 3))
# Obtain the Fermi integrals required to get the Onsager coefficients
for iT, T in enumerate(Tr):
    (N[iT], L0[iT], L1[iT], L2[iT], Lm11[iT]) = bandlib.fermiintegrals(epsilon, dos, vvdos, mur=np.array([mur[iT]]), Tr=np.array([T]), dosweight=data.dosweight, cdos=cdos, scattering_model = 'epa', scattering_file = fepa)
#N += data.nelect # incorrect because of missing states due to ecut and efcut
# ??? N -= N[0, round(N.shape[1] / 2)] # zero doping at low T in the middle of the band gap
volume = data.get_volume()
# Translate those into Onsager coefficients
sigma, seebeck, kappa = (np.empty((Tr.shape[0], 3, 3)) for ii in range(3))
Hall = np.empty((Tr.shape[0], 3, 3, 3))
for iT, T in enumerate(Tr):
    (sigma[iT], seebeck[iT], kappa[iT], Hall[iT]) = bandlib.calc_Onsager_coefficients(np.array([[L0[iT]]]), np.array([[L1[iT]]]), np.array([[L2[iT]]]), np.array([mur[iT]]), np.array([T]), volume, np.array([[Lm11[iT]]]))

# Rescale the carrier count into a volumetric density in cm^-3
#N = -N / (volume / (units.Meter / 100) ** 3)
# Transform the transport coefficients to more convenient units
sigma *= 1e-5 # kS / cm
seebeck *= 1e6  # uV / K
kappa *= 1e-2 # W / cm / K
# Obtain the scalar conductivity and Seebeck coefficient
sigmatr = sigma.trace(axis1=1, axis2=2) / 3
seebecktr = seebeck.trace(axis1=1, axis2=2) / 3
kappatr = kappa.trace(axis1=1, axis2=2) / 3
# Compute the scalar power factor
#P = sigmatr * seebecktr * seebecktr
#P *= 1e4 # uW / cm / K^2
#lorenz = 1e5 * kappatr / (sigmatr * Tr) # 10^-8 W Ohm / K^2

#h = open(ftr, 'w')
#h.write('#       Ef[Ry] T [K]            N         DOS(Ef)           S             s/t               R_H        kappa0         c                 chi\n')
#for imu, mu in enumerate(mur):
#    for iT, T in enumerate(Tr):
#        h.write('{0:10.5f}{1:10.4f}{2:16.8f}{3:16.8e}{4:16.8e}{5:16.8e}{6:16.8e}{7:16.8e}{8:16.8e}{9:16.8e}\n'.format(
#                mu / RYDBERG, T, N[iT, imu], 0.0, seebecktr[iT, imu], sigmatr[iT, imu], 0.0, kappatr[iT, imu], 0.0, 0.0))
#h.close()

h = open(ftr, 'w')
for iT, T in enumerate(Tr):
    h.write('{0:10.4f}{1:16.8f}{2:16.8f}{3:16.8f}\n'.format(T, sigmatr[iT], seebecktr[iT], kappatr[iT]))
h.close()

h = open(fct, 'w')
for iT, T in enumerate(Tr):
    h.write(('{:10.4f}' + '{:16.8f}' * 27 + '\n').format(T, *tuple(sigma[iT].flatten()), *tuple(seebeck[iT].flatten()), *tuple(kappa[iT].flatten())))
h.close()
