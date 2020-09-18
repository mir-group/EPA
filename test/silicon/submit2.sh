#!/bin/bash

EPA="q-e-qe-6.6/bin/epa.x"
PYTHON="python3"
BOLTZTRAP="boltztrap-1.2.5/src/BoltzTraP"

$EPA < silicon.epa.in > silicon.epa.out
$PYTHON qe2boltz.py > qe2boltz.out
$BOLTZTRAP silicon.def > silicon.boltztrap.out
