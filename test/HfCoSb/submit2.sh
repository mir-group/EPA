#!/bin/bash

EPI2EPA="qe-6.1/bin/epi2epa.x"
PYTHON="python3"
BOLTZTRAP="boltztrap-1.2.5/src/BoltzTraP"

$EPI2EPA < HfCoSb.epi2epa.in > HfCoSb.epi2epa.out
$PYTHON qe2boltz.py > qe2boltz.out
$BOLTZTRAP HfCoSb.def > HfCoSb.boltztrap.out
$PYTHON boltz2plot.py > boltz2plot.out
