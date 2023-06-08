#!/bin/bash

#mydetectors
cd ..
#detectors
cd ..
#slither
cd ..

python3 setup.py install

cd slither
cd detectors
cd my_detectors
#cd 0.7.6

#slither --detect detect_round backdoor.sol
