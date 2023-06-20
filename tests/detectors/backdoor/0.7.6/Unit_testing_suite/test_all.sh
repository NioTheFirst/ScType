#!/bin/bash

#Abstract type
cd abstract_datatype
slither --detect tcheck A.sol
cd ..

sleep 3

#Cross Contract Function Call
cd cross_contract_hlc
slither --detect tcheck .
cd ..

sleep 3

#High Level Call Handling
cd new_hlc_handling
slither --detect tcheck A.sol
cd ..

sleep 3

#Reference Handling
cd new_ref_handling
slither --detect tcheck A.sol
cd ..

sleep 3


echo "Unit testing complete"
