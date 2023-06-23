#!/bin/bash

# Check if commit message is provided as an argument
if [ -z "$1" ]; then
  echo "Please provide a commit message."
  exit 1
fi

#mydetectors
cd ..
#detectors
cd ..
#slither
cd ..

#python3 setup.py install
pip3 install .

cd slither
cd detectors
cd my_detectors
#cd 0.7.6
./compile_git.sh "$1"

#slither --detect detect_round backdoor.sol
