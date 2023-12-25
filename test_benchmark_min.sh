#!/bin/bash


# Function to execute a numbered group of commands
execute_group() {
  group_number=$1
  shift
  echo "Executing Group $group_number"
  "$@"
  echo "Group $group_number complete"
}


# Group 1: MarginSwap
if [[ $# -eq 0 || $1 -eq 1 ]]; then
  solc-select use 0.8.3
  cd "Benchmark/MarginSwap/contracts"
  slither --detect tcheck HourlyBondSubscriptionLending.sol
  cd "../../../"
  execute_group 1 echo "[*] Tested 1 warning for MarginSwap"
  sleep 3
fi

# Group 2: MarginSwap
if [[ $# -eq 0 || $1 -eq 2 ]]; then
  solc-select use 0.8.3
  cd "Benchmark/Vader_Protocol_p1/vader-protocol/contracts"
  slither --detect tcheck Utils.sol
  cd "../../../../"
  execute_group 2 echo "[*] Tested 3 warnings for Vader Protocol P1"
  sleep 3
fi


echo "Testing complete"
