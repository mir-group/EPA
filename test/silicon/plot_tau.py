import numpy as np
import brave

name = 'silicon'
ext = 'png'
f1 = ['{0:s}.intrans'.format(name), '{0:s}.trace'.format(name)]
f2 = ['{0:s}.nscf.out'.format(name)]
f3 = ['{0:s}.intrans'.format(name), '{0:s}.transdos'.format(name)]
f4 = ['{0:s}.intrans'.format(name), '{0:s}.epa.e'.format(name)]
f5 = '{0:s}_tau.{1:s}'.format(name, ext)

title = '{0:s}    ${1:s} = {2:.2f}$    $T = {3:d}$K'
mode = [r'$\tau = {0:d}$ fs' , 'EPA']
tauvc = None
kappaelzeroj = True
numelec = 0.0
T_K = 300.0

_fmt1 = 'Read {0:s} {1:s}  ###  numelec0 = {2:f} el/uc'
_fmt2 = '    bandgap = {0:f} eV'

trn = brave.Transport()
trn.read('boltztrap-out', f1, tauvc, kappaelzeroj)
numelec0 = trn.renorm_numelec()
print(_fmt1.format(name, mode[1], numelec0))

bnd = brave.Energy()
bnd.read('pw-out', f2)
evbm, ecbm, kvbm, kcbm = bnd.calc_efermi()
bandgap = ecbm - evbm
print(_fmt2.format(bandgap))

epa = brave.EPA()
epa.read('pw-out', f2)
epa.read('boltztrap-dos', f3)
epa.read('epa-out', f4)

tau_epa = np.empty((2, trn.nmu), float)
en = np.empty(trn.nmu, float)
mu = np.empty(trn.nmu, float)
temp = np.empty(trn.nmu, float)
temp[:] = T_K
mu[:] = trn.convert_argument('mu', [T_K, numelec])
en[:] = trn.mu[:]
epa.energy = en
epa.mu = mu
epa.temp = temp
epa.calc_invtau()
tau_epa[0, :] = epa.energy
tau_epa[1, :] = np.divide(1.0, np.maximum(epa.invtau * 1.0e-15, 1.0e-6))

_mu = trn.convert_argument('mu', [T_K, numelec])
mu = np.array([[_mu, _mu], [0.0, 120.0]], float)

xx = bandgap / 2
yy = 1.0e3
gap = np.array([[-xx, -xx, xx, xx, -xx], [-yy, yy, yy, -yy, -yy]], float)

if numelec < 0:
    doped = 'p'
elif numelec > 0:
    doped = 'n'
else:
    doped = 'x'

plt = brave.Plot()
plt.data = [[gap, tau_epa, mu]]
plt.kind = [['fill', 'plot', 'plot']]
plt.style = [[['None', 'None'], ['solid', 'None'], [(0, (2, 1)), 'None']]]
plt.color = [[['0.75', 'none'], ['red', 'none', 'none'], ['black', 'none', 'none']]]
plt.label = [['', mode[1], '']]
plt.zorder = [[-3, -2, -1]]
plt.xlim = [[-4.0, 4.0]]
plt.ylim = [[0.0, 120.0]]
plt.xdel = [[1.0, 1.0]]
plt.ydel = [[20.0, 20.0]]
plt.xlabel = ['Energy (eV)']
plt.ylabel = ['Relaxation time (fs)']
plt.note = [[[0.5, 1.02, 'center', 'bottom', title.format(name, doped, abs(numelec), int(round(T_K))), 'black', 1.0]]]

plt.pagesize = [2.6, 2.7]
plt.fontsize = 8.0
plt.linewidth = 0.7
plt.markersize = 3.0
plt.labelpad = [2.0, 2.0]
plt.tickpad = [2.0, 2.0, 2.0, 2.0]
plt.ticksize = [3.0, 1.5, 3.0, 1.5]

plt.write('matplotlib', ext, f5)
