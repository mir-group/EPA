#!/bin/bash

# epa.x dies with I/O errors when ph.x is run with buffered I/O
unset FORT_BUFFERED
unset FORT_BLOCKSIZE
unset FORT_BUFFERCOUNT

NPOOL=20
MPI="mpirun"
PW="q-e-qe-6.6/bin/pw.x"
PH="q-e-qe-6.6/bin/ph.x"

$MPI $PW -npool $NPOOL < HfCoSb.scf.in > HfCoSb.scf.out
$MPI $PH -npool $NPOOL < HfCoSb.ph1.in > HfCoSb.ph1.out
$MPI $PH -npool $NPOOL < HfCoSb.ph2.in > HfCoSb.ph2.out
$MPI $PW -npool $NPOOL < HfCoSb.nscf.in > HfCoSb.nscf.out
rm HfCoSb.wfc*
