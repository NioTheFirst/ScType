#!/bin/bash
echo "Testing yAxis..."
slither --detect tcheck yAxis_1.sol > yAxis_output.txt
sleep 5

echo "Testing badger ..."
slither --detect tcheck badger_strat.sol > badger_strat_output.txt

#solc-select use 0.8.3
