#!/bin/bash

NPOOL=29
MPI="mpirun"
PW="qe-6.1/bin/pw.x"
PH="qe-6.1/bin/ph.x"

$MPI $PW -npool $NPOOL < HfCoSb.scf.in > HfCoSb.scf.out
$MPI $PH -npool $NPOOL < HfCoSb.ph1.in > HfCoSb.ph1.out
$MPI $PH -npool $NPOOL < HfCoSb.ph2.in > HfCoSb.ph2.out
$MPI $PW -npool $NPOOL < HfCoSb.nscf.in > HfCoSb.nscf.out
rm HfCoSb.wfc*
