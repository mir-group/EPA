#!/bin/bash

# epa.x dies with I/O errors when ph.x is run with buffered I/O
unset FORT_BUFFERED
unset FORT_BLOCKSIZE
unset FORT_BUFFERCOUNT

NPOOL=20
MPI="mpirun"
PW="q-e-qe-6.6/bin/pw.x"
PH="q-e-qe-6.6/bin/ph.x"

$MPI $PW -npool $NPOOL < silicon.scf.in > silicon.scf.out
$MPI $PH -npool $NPOOL < silicon.ph1.in > silicon.ph1.out
$MPI $PH -npool $NPOOL < silicon.ph2.in > silicon.ph2.out
$MPI $PW -npool $NPOOL < silicon.nscf.in > silicon.nscf.out
rm silicon.wfc*
