## BoltzTraP2 example for silicon

### Input files

| File name          | Origin                           | Modification                     |
|--------------------|----------------------------------|----------------------------------|
| **silicon.struct** | **../silicon/silicon.structure** | Substantial                      |
| **silicon.energy** | **../silicon/silicon.energy**    | Added nspin & efermi in 2nd line |
| **silicon.epa.e**  | **../silicon/silicon.epa.e**     | None                             |

### Output files

| File name             | Produced by           | Method |
|-----------------------|-----------------------|--------|
| **silicon_crt.trace** | **silicon_crt.py**    | CRT    |
| **silicon_epa.trace** | **silicon_epa.py**    | EPA    |