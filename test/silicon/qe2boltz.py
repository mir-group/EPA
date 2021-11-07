import brave

name = 'silicon'
f1 = ['{0:s}.nscf.out'.format(name)]
f2 = ['{0:s}.def'.format(name), '{0:s}.intrans'.format(name), '{0:s}.struct'.format(name), '{0:s}.energy'.format(name)]

bnd = brave.Energy()
bnd.read('pw-out', f1)

# For insulators, set the Fermi level in the middle of the band gap !!!! DO NOT TRY THIS FOR METALS !!!!
evbm, ecbm, kvbm, kcbm = bnd.calc_efermi()
egap = ecbm - evbm
ss = '{0:s}  nelec = {1:.2f}  evbm = {2:.6f}  ecbm = {3:.6f}  egap = {4:.6f}  efermi = {5:.6f}  kvbm = {6[0]:.3f} {6[1]:.3f} {6[2]:.3f}  kcbm = {7[0]:.3f} {7[1]:.3f} {7[2]:.3f}'.format(
    name, bnd.nelec, evbm, ecbm, egap, bnd.efermi, kvbm, kcbm)
print(ss)

# For metals, don't mess with the Fermi level
#ss = '{0:s}  nelec = {1:.2f}  efermi = {2:.6f}'.format(name, bnd.nelec, bnd.efermi))
#print(ss)

bnd.write('boltztrap-in', f2)
