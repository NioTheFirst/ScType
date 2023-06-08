#!/bin/bash

#mydetectors
cd ..
#detectors
cd ..
#slither
cd ..

python3 setup.py install

cd tests
#cd tcheck
cd detectors
cd backdoor
cd 0.7.6

#slither --detect detect_round backdoor.sol
slither --detect tcheck test.sol
