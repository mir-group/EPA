# Electron-Phonon Averaged (EPA) Approximation

The electron-phonon averaged (EPA) Approximation is described in [Adv. Energy Mater. 2018, 1800246](https://doi.org/10.1002/aenm.201800246) and [arXiv:1511.08115](https://arxiv.org/abs/1511.08115).

There are two examples, silicon and half-Heusler HfCoSb, containing all the input and output files (output files are gzipped). I would suggest starting with silicon because HfCoSb is computationally much more expensive. Take a look at the job submission scripts, **submit1.sh** and **submit2.sh**, to see the computational workflow. There are several python scripts called from **submit2.sh**, they require another (private) package to convert QE output to BoltzTraP input. You can instead use the converter included in boltztrap-1.2.5, called **qe2boltz.py**.

The computational workflow:

1.  Run **pw.x** to obtain the SCF solution
2.  Run **ph.x** with `fildvscf = 'dvscf'` to compute derivatives of the SCF potential
3.  Run **ph.x** with `electron_phonon = 'epa'` to compute the electron-phonon matrix elements and write them to file 'silicon.epa.k'
4.  Run **pw.x** with calculation = 'nscf' to obtain the eigenvalues on a fine k-grid
5.  Run **epa.x** to read the electron-phonon matrix elements from file 'silicon.epa.k', average them over wavevector directions, and write them to file 'silicon.epa.e'
6.  Run **BoltzTraP** to read the averaged electron-phonon matrix elements from file 'silicon.epa.e' and compute the transport properties

## Step 4

Format of the input file 'silicon.epa.in' for **epa.x**:

| Content                | Description                                                                                                                                          |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| `silicon.epa.k`        | input file for **epa.x** (contains electron-phonon matrix elements in momentum-space, produced by **ph.x**)                                          |
| `silicon.epa.e`        | output file of **epa.x** (contains electron-phonon matrix elements in energy-space, averaged over directions)                                        |
| `egrid`                | job type, 'egrid' stands for the standard EPA averaging scheme from momentum to energy space                                                         |
| `6.146000 -0.4 10 0 0` | VBM energy in eV, energy grid step in eV (negative because valence bands are below VBM), number of bins in valence energy grid, last two must be 0's |
| `6.602500 0.4 10 0 0`  | CBM energy in eV, energy grid step in eV, number of bins in conduction energy grid, last two must be 0's                                             |
| `0.0 0 0`              | for plotting the electron-phonon matrix elements vs energy (like in Supplementary Figure 1 of the EPA paper), only used if job type is 'gdist'       |

The energy grids for both valence and conduction bands span 4 eV below the VBM and 4 eV above the CBM (0.4 eV step times 10 energy bins gives 4 eV range). This could be the same or different for valence and conduction bands.

How to choose grid steps and numbers of bins for valence and conduction energy grids? Choose some initial values, then run epa.x, and examine the output. Look at the numbers in `countv` and `countc` columns. These are numbers of eigenvalues that fall in each energy bin. If there are any zeros or small numbers (say less than 10), you would have to increase grid steps or decrease numbers of bins or increase the number of k-points (the latter requires rerunning **pw.x** NSCF calculation).

Transitions between the valence and conduction energy grids are not implemented, there are only valence-to-valence and conduction-to-conduction transitions. This won't work for metals.

If you have a metal you can try to define a single energy grid that spans both valence and conduction bands. I haven't tested it but I think it should work. For example, if the Fermi level is at +5 eV, you can define the grids in EPA input file as follows:

| Content                | Description                                                                                                                                          |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-5.0 -10.0 1 0 0`     | valence energy grid is far below the Fermi level and is not functional                                                                               |
| `2.0 0.5 12 0 0`       | conduction energy grid spans the range from 2 eV to 8 eV, that is, 3 eV below and 3 eV above the Fermi level                                         |

## Step 5

Add the following line to BoltzTraP input file 'silicon.def' to switch BoltzTraP to the EPA mode:
```
88, 'silicon.epa.e', 'old', 'formatted', 0
```
If BoltzTraP is unable to open file 'silicon.epa.e' or read its content, it will automatically fall back to the CRT (constant relaxation time) mode.

Create file 'silicon.ke0j' with content '.TRUE.' to make BoltzTraP compute the electronic part of the thermal conductivity at zero electric current.

## License

Quantum ESPRESSO, BoltzTraP, and BoltzTraP2 patches are distributed under GPL-2.0, LGPL-3.0+, and GPL-3.0+ licenses, respectively. For license information see "license.txt"
