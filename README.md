# Electron-Phonon Averaged (EPA) Approximation

There are two examples, silicon and half-Heusler HfCoSb, containing all the input and output files (output files are gzipped). I would suggest starting with silicon because HfCoSb is computationally much more expensive. Take a look at the job submission scripts, **submit1.sh** and **submit2.sh**, to see the computational workflow. There are several python scripts called from **submit2.sh**, they require another (private) package to convert QE output to Boltztrap input. You can instead use the converter included in Boltztrap-1.2.5, called **qe2boltz.py**.

The computational workflow is as follows:
- Run **ph.x** with `fildvscf = 'dvscf'` to compute derivatives of scf potential
- Run **ph.x** with `electron_phonon = 'epa'` to compute el-ph matrix elements and write them to file 'silicon.epa.k'
- Run **epa.x** to read the matrix elements from file 'silicon.epa.k', average them over wavevector directions, and write them to file 'silicon.epa.e'
- Run BoltzTraP to read the averaged matrix elements from file 'silicon.epa.e' and compute the transport properties

The important file is 'silicon.epa.in' which contains parameters for program **epa.x**. It has the following content:

| Content                | Description                                                                                                                                          |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| `silicon.epa.k`        | input file for **epa.x** (contains el-ph matrix elements in momentum-space, produced by **ph.x**)                                                    |
| `silicon.epa.e`        | output file of **epa.x** (contains el-ph matrix elements in energy-space, averaged over directions)                                                  |
| `egrid`                | job type, 'egrid' stands for the standard EPA averaging scheme from momentum to energy space                                                         |
| `6.146000 -0.4 10 0 0` | VBM energy in eV, energy grid step in eV (negative because valence bands are below VBM), number of bins in valence energy grid, last two must be 0’s |
| `6.602500 0.4 10 0 0`  | CBM energy in eV, energy grid step in eV, number of bins in conduction energy grid, last two must be 0’s                                             |
| `0.0 0 0`              | for plotting matrix elements vs energy (like in Supplementary Figure 1 of the EPA paper), only used if job type is 'gdist'                           |

The patched Boltztrap will automatically switch to the EPA mode if it finds file 'silicon.epa.e' (as defined in Boltztrap input file 'silicon.def'). If 'silicon.epa.e' is not present, the patched Boltztrap will fall back to the CRT (constant relaxation time) mode.

The energy grids for both valence and conduction bands span 4 eV below the VBM and 4 eV above the CBM (0.4 eV step times 10 energy bins gives 4 eV range). This could be the same or different for valence and conduction bands.

Transitions between the valence and conduction energy grids are not implemented, there are only valence-to-valence and conduction-to-conduction transitions. This won’t work for metals.

If you have a metal you can try to define a single energy grid that spans both valence and conduction bands. I haven’t tested it but I think it should work. For example, if the Fermi level is at +5 eV, you can define the grids in EPA input file as follows:

| Content                | Description                                                                                                                                          |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-5.0 -10.0 1 0 0`     | valence energy grid is far below the Fermi level and is not functional                                                                               |
| `2.0 0.5 12 0 0`       | conduction energy grid spans the range from 2 eV to 8 eV, that is, 3 eV below and 3 eV above the Fermi level                                         |
