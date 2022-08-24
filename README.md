# Electron-Phonon Averaged (EPA) Approximation

The electron-phonon averaged (EPA) approximation is described in [Adv. Energy Mater. 2018, 1800246](https://doi.org/10.1002/aenm.201800246) and [arXiv:1511.08115](https://arxiv.org/abs/1511.08115).

There are two examples, silicon and half-Heusler HfCoSb (from the paper above), containing all the input and output files (output files are gzipped). Each example has two job submission scripts, **submit1.sh** and **submit2.sh**, which follow the same computational workflow (see below). There are several python scripts called from **submit2.sh**, they require python package [BRAVE](https://github.com/mir-group/BRAVE) to convert QE output to BoltzTraP input. Alternatively, this conversion can be performed using python script **qe2boltz.py** included in boltztrap-1.2.5.

## Workflow

1.  Run **pw.x** to obtain the SCF solution
2.  Run **ph.x** with `fildvscf = 'dvscf'` to compute derivatives of the SCF potential
3.  Run **ph.x** with `electron_phonon = 'epa'` to compute the electron-phonon coupling matrix elements and write them to file 'silicon.epa.k'
4.  Run **pw.x** with `calculation = 'nscf'` to obtain the eigenvalues on a fine k-grid
5.  Run **epa.x** to read the electron-phonon coupling matrix elements from file 'silicon.epa.k', average their absolute squared values over wavevector directions, and write them to file 'silicon.epa.e'
6.  Run **BoltzTraP** to read the averaged squared absolute electron-phonon coupling matrix elements from file 'silicon.epa.e' and compute the transport properties

## Step 1

You have to use metallic occupations even for semiconducting systems. This is because the electron-phonon coupling in **ph.x** is only implemented for metallic systems. It works fine for semiconducting systems, but only by using this trick with metallic occupations. Note that for semiconducting systems you can legitimately use any occupations (fixed or smearing) and they produce identical results, but not the other way around&mdash;using fixed occupations for metallic systems is not allowed.

## Step 5

Format of the input file 'silicon.epa.in' for **epa.x**:

| Content                | Description                                                                                                                                               |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `silicon.epa.k`        | input data used by **epa.x** (contains electron-phonon coupling matrix elements in momentum-space, produced by **ph.x**)                                  |
| `silicon.epa.e`        | output data produced by **epa.x** (contains averaged squared absolute electron-phonon coupling matrix elements in energy-space, used by **BoltzTraP**)    |
| `egrid`                | job type, 'egrid' for the standard EPA averaging procedure from momentum to energy space, 'bpair' for the obsolete procedure (kept for testing purposes)  |
| `6.146000 -0.4 10 0 0` | valence energy grid edge (VBM energy), grid step (negative = downwards from VBM), number of bins, range of valence bands (0 0 = all valence bands)        |
| `6.602500 0.4 10 0 0`  | conduction energy grid edge (CBM energy), grid step (positive = updards from CBM), number of bins, range of conduction bands (0 0 = all conduction bands) |
| `0.0 0 0`              | parameters used by job type 'gdist' for plotting a distribution of squared absolute electron-phonon coupling matrix elements                              |

Both valence and conduction energy grids consist of 10 bins of 0.4 eV width (these could be different for the two grids). The valence energy grid extends 4 eV below the VBM (valence band maximum) and the conduction energy grid extends 4 eV above the CBM (conduction band minimum). All energies are in eV. 

Transitions between the valence and conduction energy grids are not implemented, there are only valence-to-valence and conduction-to-conduction transitions. This is only valid if the band gap is larger than the highest phonon energy.

In case of a metal or a narrow-gap semiconductor, you can define a single energy grid that spans both valence and conduction bands. For example, if the Fermi level is at 5 eV, the energy grids can be set as follows:

| Content                | Description                                                                                                                                               |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `2.0 -10.0 1 0 0`     | valence energy grid is 3 eV below the Fermi level and is not functional                                                                                    |
| `2.0 0.5 12 0 0`       | conduction energy grid spans the range from 2 eV to 8 eV, that is, from 3 eV below the Fermi level to 3 eV above the Fermi level                          |

## Energy Grids

The extents of valence and conduction energy grids are determined by the range of chemical potential for which you wish to compute the transport properties. Let's say the chemical potential spans from 2 eV below the VBM to 2 eV above the CBM. Then the valence and conduction energy grids have to cover that range, plus the largest phonon energy (because the electron energy can change by as much as the largest phonon energy during the electron-phonon scattering, so all electrons in that energy range will contribute to the transport properties). Extending the energy grids outside of that range won't have any effect on the transport properties (since it doesn't affect electronic transitions in the desired range of chemical potentials). Let's say the largest phonon energy is 0.2 eV, then the energy grids have to cover the range from 2.2 eV below the VBM to 2.2 eV above the CBM. If the grid steps for the valence and conduction energy grids are set to 0.2 eV and 0.5 eV, then the numbers of bins in each grid respectively should be set to 11 and 5.

Look at your band structure to determine the energy range covered by the valence and conduction energy grids. Break them down into several energy bins, then run **epa.x**, and examine the output. Look at the numbers in `countv` and `countc` columns. These are numbers of eigenvalues that fall in each energy bin. If these numbers are large you can refine the energy grids by decreasing grid steps and increasing numbers of bins. For example, if your valence energy grid spans 2 eV below the VBM, you can divide this 2 eV range into increasing numbers of bins, such as 4 bins of 0.5 eV width, 5 bins of 0.4 eV width, 6 bins of 0.33 eV width, 7 bins of 0.29 eV width, 8 bins of 0.25 eV width, etc. You can continue the process until you start hitting zeros in `countv` and `countc` columns. If you want to further refine the energy grids you will need to increase the numbers of k- and/or q-points and rerun **pw.x** and **ph.x**.

There are several points to note about `countv` and `countc` values:
* The electron energy dispersion is usually not homogeneous, which means that for the same grid step, some energy bins will have small values of `countv` and `countc` while other energy bins with have large values of `countv` and `countc`.
* If the energy grids span multiple manifolds of bands separated by gaps (zero-DOS regions), the energy bins within these gaps will have zeros in `countv` and `countc` columns. These zeros can be safely ignored.
* If the numbers of bins in the valence and conduction energy grids are different, the undefined energy bins will be padded with zeros in `countv` and `countc` columns. These zeros can be safely ignored.
* Some of the energy bins in finite-DOS regions may have zeros in `countv` and `countc` columns due to grid steps which are too small. This will cause spikes in the tau-epsilon dependence (inverse tau dropping to zero and tau jumping to infinity in these energy bins), which in turn will result in spikes or oscillations in transport integrals. You must increase energy grid steps or increase the numbers of k- and/or q-points to get rid of these zeros.

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
