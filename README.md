# Electron-Phonon Averaged (EPA) Approximation

The electron-phonon averaged (EPA) approximation is described in [Adv. Energy Mater. 2018, 1800246](https://doi.org/10.1002/aenm.201800246) and [arXiv:1511.08115](https://arxiv.org/abs/1511.08115).

There are two examples, silicon and half-Heusler HfCoSb (from the paper above), containing all the input and output files (output files are gzipped). Each example has two job submission scripts, **submit1.sh** and **submit2.sh**, which follow the same computational workflow (see below). There are several python scripts called from **submit2.sh**, they require python package [BRAVE](https://github.com/mir-group/BRAVE) to convert QE output to BoltzTraP input. Alternatively, this conversion can be performed using python script **qe2boltz.py** included in boltztrap-1.2.5.

## Workflow

1.  Run **pw.x** to obtain the SCF solution
2.  Run **ph.x** with `fildvscf = 'dvscf'` to compute derivatives of the SCF potential
3.  Run **ph.x** with `electron_phonon = 'epa'` to compute the electron-phonon matrix elements and write them to file 'silicon.epa.k'
4.  Run **pw.x** with `calculation = 'nscf'` to obtain the eigenvalues on a fine k-grid
5.  Run **epa.x** to read the electron-phonon matrix elements from file 'silicon.epa.k', average them over wavevector directions, and write them to file 'silicon.epa.e'
6.  Run **BoltzTraP** to read the averaged electron-phonon matrix elements from file 'silicon.epa.e' and compute the transport properties

## Step 5

Format of the input file 'silicon.epa.in' for **epa.x**:

| Content                | Description                                                                                                                                               |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `silicon.epa.k`        | input data used by **epa.x** (contains electron-phonon matrix elements in momentum-space, produced by **ph.x**)                                           |
| `silicon.epa.e`        | output data produced by **epa.x** (contains electron-phonon matrix elements in energy-space, used by **BoltzTraP**)                                       |
| `egrid`                | job type, 'egrid' for the standard EPA averaging procedure from momentum to energy space                                                                  |
| `6.146000 -0.4 10 0 0` | valence energy grid edge (VBM energy), grid step (negative = downwards from VBM), number of bins, range of valence bands (0 0 = all valence bands)        |
| `6.602500 0.4 10 0 0`  | conduction energy grid edge (CBM energy), grid step (positive = updards from CBM), number of bins, range of conduction bands (0 0 = all conduction bands) |
| `0.0 0 0`              | parameters used by job type 'gdist' which constructs the histogram for plotting a distribution of squared matrix elements                                 |

Both valence and conduction energy grids consist of 10 bins of 0.4 eV width (these could be different for the two grids). The valence energy grid extends 4 eV below the VBM (valence band maximum) and the conduction energy grid extends 4 eV above the CBM (conduction band minimum). All energies are in eV. 

Transitions between the valence and conduction energy grids are not implemented, there are only valence-to-valence and conduction-to-conduction transitions. This is only valid if the band gap is larger than the highest phonon energy.

In case of a metal or a narrow-gap semiconductor, one can define a single energy grid that spans both valence and conduction bands. For example, if the Fermi level is at 5 eV, the energy grids can be set as follows:

| Content                | Description                                                                                                                                               |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `2.0 -10.0 1 0 0`     | valence energy grid is 3 eV below the Fermi level and is not functional                                                                                    |
| `2.0 0.5 12 0 0`       | conduction energy grid spans the range from 2 eV to 8 eV, that is, from 3 eV below the Fermi level to 3 eV above the Fermi level                          |

## Energy Grids

The extents of valence and conduction energy grids are determined by the range of chemical potentials for which one wishes to compute the transport properties. Let's say the chemical potential spans from 4 eV below the VBM to 4 eV above the CBM. Then the valence and conduction energy grids have to cover that range, plus the largest phonon energy (because the electron energy can change by as much as the largest phonon energy during the electron-phonon scattering, so all electrons in that energy range will contribute to the transport properties). Extending the energy grids outside of that range won't have any effect on the transport properties (since it doesn't affect electronic transitions in the desired range of chemical potentials). Let's say the largest phonon energy is 0.2 eV, then the energy grids have to cover the range from 4.2 eV below the VBM to 4.2 eV above the CBM. If the grid steps are set to 0.1 eV for both energy grids, this requires 42 bins in each energy grid. If the grid steps are increased to 0.2 eV, the numbers of bins can be decreased to 21.

Look at your band structure to determine the energy range covered by the valence and conduction energy grids. Break them down into several energy bins, then run **epa.x**, and examine the output. Look at the numbers in `countv` and `countc` columns. These are numbers of eigenvalues that fall in each energy bin. If these numbers are large you can refine the energy grids by decreasing grid steps and increasing numbers of bins. For example, if your valence energy grid spans 2 eV below the VBM, you can divide this 2 eV range into increasing numbers of bins, such as 4 bins of 0.5 eV width, 5 bins of 0.4 eV width, 6 bins of 0.33 eV width, 7 bins of 0.29 eV width, 8 bins of 0.25 eV width, etc. You can continue the process until you start hitting zeros in `countv` and `countc` columns. If you want to further decrease the grid steps you would have to increase the numbers of k- and/or q-points and rerun **pw.x** and **ph.x**. Note that if you have different numbers of bins in the valence and conduction energy grids, the undefined energy bins will be padded with zeros in `countv` and `countc` columns. You can disregard these zeros and continue refining the energy grids.

What should be reasonable values for `countv` and `countc`? This, of course, is entirely dependent on the material. As a rule of thumb, anything less than 3-5 is too small, something in 5-10 or 20-50 range is reasonable, and anything above 50-100 is too large. Note that since the electron energy dispersion is generally not homogeneous, there will always be some bins with small values (5-10 and below) and other bins with large values (100-200 and above) for the same grid step. Therefore, one has to focus on those bins that have the smallest values of `countv` and `countc`, and make sure that it doesn't go below 3-5 while decreasing grid steps.

## Step 6

Add the following line to BoltzTraP input file 'silicon.def' to switch BoltzTraP to the EPA mode:
```
88, 'silicon.epa.e', 'old', 'formatted', 0
```
If BoltzTraP is unable to open file 'silicon.epa.e' or read its content, it will automatically fall back to the CRT (constant relaxation time) mode.

Create file 'silicon.ke0j' with content '.TRUE.' and add the following line to BoltzTraP input file 'silicon.def' to make BoltzTraP compute the electronic part of the thermal conductivity at zero electric current:
```
89, 'silicon.ke0j', 'old', 'formatted', 0
```

## License

EPA patches to [Quantum ESPRESSO](https://github.com/QEF/q-e), [BoltzTraP](https://owncloud.tuwien.ac.at/index.php/s/s2d55LYlZnioa3s), and [BoltzTraP2](https://gitlab.com/sousaw/BoltzTraP2) are distributed under [GPL-2.0](https://github.com/QEF/q-e/blob/master/License), [LGPL-3.0+](http://www.gnu.org/licenses/lgpl-3.0.txt), and [GPL-3.0+](https://gitlab.com/sousaw/BoltzTraP2/blob/public/LICENSE.txt) licenses, respectively.
