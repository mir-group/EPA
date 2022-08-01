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
#doping_level = 0.01

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
Tr = np.arange(deltat, tmax + deltat / 2, deltat)
mur_indices = np.logical_and(epsilon > data.fermi - efcut, epsilon < data.fermi + efcut)
mur = epsilon[mur_indices]

# Set different chemical potentials at each temperature corresponding to the constant doping level
#Tr = np.arange(deltat, tmax + deltat / 2, deltat)
#mur = np.empty_like(Tr)
#_nelect = data.nelect
#for iT, T in enumerate(Tr):
#    mur[iT] = bandlib.solve_for_mu(epsilon, dos, _nelect - doping_level, T, data.dosweight, refine=True)

# Obtain the Fermi integrals required to get the Onsager coefficients
(N, L0, L1, L2, Lm11) = bandlib.fermiintegrals(epsilon, dos, vvdos, mur=mur, Tr=Tr, dosweight=data.dosweight, cdos=cdos, scattering_model = 'epa', scattering_file = fepa)
#N += data.nelect # incorrect because of missing states due to ecut and efcut
# ??? N -= N[0, round(N.shape[1] / 2)] # zero doping at low T in the middle of the band gap
volume = data.get_volume()
# Translate those into Onsager coefficients
(sigma, seebeck, kappa, Hall) = bandlib.calc_Onsager_coefficients(L0, L1, L2, mur, Tr, volume, Lm11)

# Rescale the carrier count into a volumetric density in cm^-3
#N = -N / (volume / (units.Meter / 100) ** 3)
# Transform the transport coefficients to more convenient units
sigma *= 1e-5 # kS / cm
seebeck *= 1e6  # uV / K
kappa *= 1e-2 # W / cm / K
# Obtain the scalar conductivity and Seebeck coefficient
sigmatr = sigma.trace(axis1=2, axis2=3) / 3
seebecktr = seebeck.trace(axis1=2, axis2=3) / 3
kappatr = kappa.trace(axis1=2, axis2=3) / 3
# Compute the scalar power factor
#P = sigmatr * seebecktr * seebecktr
#P *= 1e4 # uW / cm / K^2
#lorenz = 1e5 * kappatr / (sigmatr * Tr) # 10^-8 W Ohm / K^2

h = open(ftr, 'w')
h.write('#       Ef[Ry] T [K]            N         DOS(Ef)           S             s/t               R_H        kappa0         c                 chi\n')
for imu, mu in enumerate(mur):
    for iT, T in enumerate(Tr):
        h.write(('{:10.5f}{:10.4f}' + '{:16.8f}' * 8 + '\n').format(
                mu / RYDBERG, T, N[iT, imu], 0.0, seebecktr[iT, imu], sigmatr[iT, imu], 0.0, kappatr[iT, imu], 0.0, 0.0))
h.close()

h = open(fct, 'w')
h.write('#       Ef[Ry] T [K]            N         cond(x,x\')' + ' ' * 130 + 'seebeck(x,x\')' + ' ' * 131 + 'kappa0(x,x\')\n')
for imu, mu in enumerate(mur):
    for iT, T in enumerate(Tr):
        h.write(('{:10.5f}{:10.4f}' + '{:16.8f}' * 27 + '\n').format(
                mu / RYDBERG, T, *tuple(sigma[iT].flatten()), *tuple(seebeck[iT].flatten()), *tuple(kappa[iT].flatten())))
h.close()
