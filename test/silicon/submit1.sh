#!/bin/bash

NPOOL=24
export OMP_NUM_THREADS=1
MPI="mpirun"
PW="q-e-qe-6.2.1/bin/pw.x"
PH="q-e-qe-6.2.1/bin/ph.x"

$MPI $PW -npool $NPOOL < silicon.scf.in > silicon.scf.out
$MPI $PH -npool $NPOOL < silicon.ph1.in > silicon.ph1.out
$MPI $PH -npool $NPOOL < silicon.ph2.in > silicon.ph2.out
$MPI $PW -npool $NPOOL < silicon.nscf.in > silicon.nscf.out
rm silicon.wfc*