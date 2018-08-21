import numpy as np
import brave

name = 'silicon'
ext = 'png'
f1 = ['{0:s}.intrans'.format(name), '{0:s}.trace'.format(name)]
f2 = '{0:s}_boltz.{1:s}'.format(name, ext)

prop = ['sigma', 'seebeck', 'L']
scale = [1.0e-5, 1.0e6, 1.0e8]
tauvc = None
kappaelzeroj = True
kappalatvalue = 2.0
tempvalue = 0.0
numelec = -0.01
T_C2K = 273.15

_kind = 'plot'
_style = ['solid', 'None']
_color = ['red', 'none', 'none']
_label = 'EPA'

xlim = [[0.0, 850.0], [0.0, 850.0], [0.0, 850.0]]
xdel = [[200.0, 200.0], [200.0, 200.0], [200.0, 200.0]]
xlabel = ['$T$ ($^\circ$C)', '$T$ ($^\circ$C)', '$T$ ($^\circ$C)']
ylim = [[0.0, 10.0], [0.0, 200.0], [0.0, 5.0]]
ydel = [[2.0, 2.0], [50.0, 50.0], [1.0, 1.0]]
ylabel = ['$\sigma$ (1/(m$\Omega$ cm))',
          '$S$ ($\mu$V/K)',
          '$L$ (10$^{-8}$ W$\Omega$/K$^2$)']

_fmt1 = 'Read {0:s} {1:s}  ###  numelec0 = {2:f} el/uc'
_fmt2 = '{0:s}    ${1:s} = {2:.2f}$'

trn = brave.Transport()
trn.read('boltztrap-out', f1, tauvc, kappaelzeroj)
trn.model_kappalat(kappalatvalue, tempvalue)
trn.calc_kappa()
trn.calc_L()
trn.calc_PF()
trn.calc_ZT()
numelec0 = trn.renorm_numelec()
print(_fmt1.format(name, _label, numelec0))

data = []
kind = []
style = []
color = []
label = []
for jj in range(len(prop)):
    curve = np.empty((2, trn.ntemp), float)
    curve[0][:] = trn.temp - T_C2K
    curve[1][:] = trn.interpolate_binary(prop[jj], 'numelec', numelec) * scale[jj]
    data.append([curve])
    kind.append([_kind])
    style.append([_style])
    color.append([_color])
    label.append([_label])

if numelec < 0.0:
    doped = 'p'
else:
    doped = 'n'
title = _fmt2.format(name, doped, abs(numelec))

plt = brave.Plot()
plt.data = data
plt.kind = kind
plt.style = style
plt.color = color
plt.label = label
plt.legend = [['upper right', 1, None],
              ['upper left', 1, None],
              ['upper right', 1, None]]
plt.xlim = xlim
plt.ylim = ylim
plt.xdel = xdel
plt.ydel = ydel
plt.xlabel = xlabel
plt.ylabel = ylabel
plt.note = [[[0.0, 1.02, 'left', 'bottom', ' (a)    ' + title, 'black', 1.0]],
            [[0.0, 1.02, 'left', 'bottom', ' (b)    ' + title, 'black', 1.0]],
            [[0.0, 1.02, 'left', 'bottom', ' (c)    ' + title, 'black', 1.0]]]

plt.pagesize = [6.0, 2.0]
plt.fontsize = 8.0
plt.linewidth = 0.7
plt.markersize = 3.0
plt.labelpad = [2.0, 2.0]
plt.tickpad = [2.0, 2.0, 2.0, 2.0]
plt.ticksize = [3.0, 1.5, 3.0, 1.5]
plt.griddim = [1, 3]
plt.gridpad = [0.5, 1.0, 1.0]
plt.gridpos = [[0, 1, 0, 1],
               [0, 1, 1, 2],
               [0, 1, 2, 3]]

plt.write('matplotlib', ext, f2)
