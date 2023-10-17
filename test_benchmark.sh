#!/bin/bash

# Save the current directory
ORIGINAL_DIR="$(pwd)"

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
  cd "../Benchmark/MarginSwap/contracts"
  slither --detect tcheck HourlyBondSubscriptionLending.sol
  cd "$ORIGINAL_DIR"
  execute_group 1 echo "[*] Tested 1 warning for MarginSwap"
  sleep 3
fi

# Group 2: MarginSwap
if [[ $# -eq 0 || $1 -eq 2 ]]; then
  solc-select use 0.8.3
  cd "../Benchmark/Vader_Protocol_p1/vader-protocol/contracts"
  slither --detect tcheck Utils.sol
  cd "$ORIGINAL_DIR"
  execute_group 2 echo "[*] Tested 3 warnings for Vader Protocol P1"
  sleep 3
fi

# Group 3: PoolTogether
if [[ $# -eq 0 || $1 -eq 3 ]]; then
  solc-select use 0.8.4
  cd "../Benchmark/PoolTogether/contracts/yield-source"
  slither --detect tcheck .
  #echo "Currently ommitted"
  cd "$ORIGINAL_DIR"
  execute_group 3 echo "[*] Tested 1 warning for PoolTogether"
  sleep 3
fi

# Group 4: Tracer
if [[ $# -eq 0 || $1 -eq 4 ]]; then
  solc-select use 0.8.4
  #cd "Benchmark/Tracer/src/contracts/lib"
  #slither --detect tcheck .
  echo "Currently ommitted"
  #cd "../../../../../"
  execute_group 4 echo "[*] Tested 1 warning for Tracer"
  sleep 3
fi

# Group 5: Yield Micro
if [[ $# -eq 0 || $1 -eq 5 ]]; then
  solc-select use 0.8.1
  cd "../Benchmark/Yield_Micro/contracts/oracles/composite"
  slither --detect tcheck CompositeMultiOracle.sol
  cd "$ORIGINAL_DIR"
  execute_group 5 echo "[*] Tested 2 warning for Yield Micro"
  sleep 3
fi

# Group 6: Sushi Trident
if [[ $# -eq 0 || $1 -eq 6 ]]; then
  solc-select use 0.8.1
  cd "../Benchmark/Sushi_Trident/trident/contracts/pool"
  slither --detect tcheck HybridPool.sol
  cd "$ORIGINAL_DIR"
  execute_group 6 echo "[*] Tested 0 warnings for Sushi Tridnet"
  sleep 3
fi

# Group 7: yAxis8
if [[ $# -eq 0 || $1 -eq 7 ]]; then
  solc-select use 0.6.12
  cd "../Benchmark/yAxis/contracts/v3"
  slither --detect tcheck Vault.sol
  cd "$ORIGINAL_DIR"
  execute_group 7 echo "[*] Tested 3 warnings for yAxis"
  sleep 3
fi

# Group 8: BadgerDao
if [[ $# -eq 0 || $1 -eq 8 ]]; then
  solc-select use 0.6.12
  cd "../Benchmark/BadgerDao/veCVX/contracts"
  slither --detect tcheck veCVXStrategy.sol
  cd "$ORIGINAL_DIR"
  execute_group 8 echo "[*] Tested 2 warnings for veCVX"
  sleep 3
fi

# Group 9: Wild Credit
if [[ $# -eq 0 || $1 -eq 9 ]]; then
  solc-select use 0.8.6
  cd "../Benchmark/Wild_Credit/contracts"
  slither --detect tcheck LendingPair.sol
  cd "$ORIGINAL_DIR"
  execute_group 9 echo "[*] Tested 2 warnings for Wild Credit"
  sleep 3
fi

#Group 10: PoolTogether_v4
if [[ $# -eq 0 || $1 -eq 10 ]]; then
  solc-select use 0.8.6
  cd "../Benchmark/PoolTogether_v4/v4-core/contracts"
  slither --detect tcheck DrawCalculator.sol
  cd "$ORIGINAL_DIR"
  execute_group 10 echo "[*] Tested 1 warnings for Pool Together v4"
  sleep 3
fi

#Group 11: Sushi Trident p2
if [[ $# -eq 0 || $1 -eq 11 ]]; then
  solc-select use 0.8.4
  cd "../Benchmark/Sushi_Trident_p2/trident/contracts/pool/concentrated"
  slither --detect tcheck ConcentratedLiquidityPool.sol
  cd "$ORIGINAL_DIR"
  execute_group 11 echo "[*] Tested 12 warnings for Sushi Trident"
  sleep 3
fi

#Group 12: Swivel
if [[ $# -eq 0 || $1 -eq 12 ]]; then
  solc-select use 0.8.4
  cd "../Benchmark/Swivel/gost/build/swivel"
  slither --detect tcheck Swivel.sol
  cd "$ORIGINAL_DIR"
  execute_group 12 echo "[*] Tested 2 warnings for Swivel"
  sleep 3
fi

#Group 13 Covalent
if [[ $# -eq 0 || $1 -eq 13 ]]; then
  solc-select use 0.8.4
  cd "../Benchmark/Covalent/contracts"
  slither --detect tcheck DelegatedStaking.sol
  cd "$ORIGINAL_DIR"
  execute_group 13 echo "[*] Tested 3 warnings for Covalent"
  sleep 3
fi

#Group 14 Badger Dao p2
if [[ $# -eq 0 || $1 -eq 14 ]]; then
  solc-select use 0.6.12
  cd "../Benchmark/Badger_Dao_p2/contracts"
  slither --detect tcheck WrappedIbbtc.sol
  cd "$ORIGINAL_DIR"
  execute_group 14 echo "[*] Tested 1 warnings for Badger Dao p2"
  sleep 3
fi

#Group 15 Vader Protocol  p2
if [[ $# -eq 0 || $1 -eq 15 ]]; then
  solc-select use 0.8.9
  cd "../Benchmark/Vader_Protocol_p2/contracts"
  cd "twap"
  slither --detect tcheck TwapOracle.sol
  cd "../"
  cd "dex/router"
  #slither --detect tcheck .
  echo "Currently Omitted (9)"
  cd "../../"
  cd "dex-v2/router"
  #slither --detect tcheck .
  echo "Currently Omitted (3)"
  cd "../../"
  cd "$ORIGINAL_DIR"
  execute_group 15 echo "[*] Tested 17 warnings for Badger Dao p2"
  sleep 3
fi

#Group 16 yAxis p2
if [[ $# -eq 0 || $1 -eq 16 ]]; then
  solc-select use 0.6.12
  cd "../Benchmark/yAxis_p2/contracts/v3/alchemix/libraries/alchemist"
  slither --detect tcheck CDP.sol
  cd "$ORIGINAL_DIR"
  execute_group 16 echo "[*] Tested 0 warnings for yAxis p2"
  sleep 3
fi

#Group 17 Malt Finance
if [[ $# -eq 0 || $1 -eq 17 ]]; then
  solc-select use 0.6.12
  cd "../Benchmark/Malt_Finance/src/contracts"
  slither --detect tcheck AuctionEscapeHatch.sol
  slither --detect tcheck AuctionBurnReserveSkew.sol
  cd "$ORIGINAL_DIR"
  execute_group 17 echo "[*] Tested 0 warnings for Malt Finance"
  sleep 3
fi

#Group 18 Perennial
if [[ $# -eq 0 || $1 -eq 18 ]]; then
  solc-select use 0.8.10
  cd "../Benchmark/Perennial/protocol/contracts/collateral/types"
  slither --detect tcheck OptimisticLedger.sol
  cd "$ORIGINAL_DIR"
  execute_group 18 echo "[*] Tested 1 warnings for Perennial"
  sleep 3
fi

#Group 19 Sublime
if [[ $# -eq 0 || $1 -eq 19 ]]; then
  solc-select use 0.7.6
  cd "../Benchmark/Sublime/contracts"
  cd "CreditLine"
  slither --detect tcheck CreditLine.sol
  cd ".."
  cd "yield"
  #slither --detect tcheck YearnYield.sol
  cd ".."
  cd "$ORIGINAL_DIR"
  execute_group 19 echo "[*] Tested 6 warnings for Sublime"
  sleep 3
fi

#Group 20 Yeti Finance
if [[ $# -eq 0 || $1 -eq 20 ]]; then
  solc-select use 0.6.12  
  cd "../Benchmark/Yeti_Finance/packages/contracts/contracts/YETI"
  slither --detect tcheck sYETIToken.sol
  cd "$ORIGINAL_DIR"
  execute_group 20 echo "[*] Tested 0 warnings for Yeti Finance"
  sleep 3
fi

#Group 21 Vader Protocol p3
if [[ $# -eq 0 || $1 -eq 21 ]]; then
  solc-select use 0.8.9
  cd "../Benchmark/Vader_Protocol_p3/contracts/lbt"
  slither --detect tcheck LiquidityBasedTWAP.sol
  cd "$ORIGINAL_DIR"
  execute_group 21 echo "[*] Tested 7 warnings for Vader Protocol p3"
  sleep 3
fi

#Group 22 InsureDao
if [[ $# -eq 0 || $1 -eq 22 ]]; then
  solc-select use 0.8.7
  cd "../Benchmark/InsureDao/contracts"
  slither --detect tcheck PoolTemplate.sol
  cd "$ORIGINAL_DIR"
  execute_group 22 echo "[*] Tested 0 warnings for InsureDao"
  sleep 3
fi

#Group 23 Rocket Joe
if [[ $# -eq 0 || $1 -eq 23 ]]; then
  solc-select use 0.8.7  
  cd "../Benchmark/Rocket_Joe/contracts"
  slither --detect tcheck LaunchEvent.sol
  cd "$ORIGINAL_DIR"
  execute_group 23 echo "[*] Tested 4 warnings for Rocket Joe"
  sleep 3
fi

#Group 24 Concur Finance
if [[ $# -eq 0 || $1 -eq 24 ]]; then
  solc-select use 0.8.12
  cd "../Benchmark/Concur_Finance/contracts"
  slither --detect tcheck MasterChef.sol
  cd "$ORIGINAL_DIR"
  execute_group 24 echo "[*] Tested 0 warnings for Concur Finance"
  sleep 3
fi

#Group 25 Biconomy Hyphen
if [[ $# -eq 0 || $1 -eq 25 ]]; then
  solc-select use 0.8.0
  cd "../Benchmark/Biconomy_Hyphen/contracts/hyphen"
  slither --detect tcheck LiquidityPool.sol
  cd "$ORIGINAL_DIR"
  execute_group 25 echo "[*] Tested 1 warnings for Biconomy Hyphen"
  sleep 3
fi

#Group 26 Sublime p2
if [[ $# -eq 0 || $1 -eq 26 ]]; then
  solc-select use 0.7.6
  cd "../Benchmark/Sublime_p2/sublime-v1/contracts/PooledCreditLine"
  slither --detect tcheck LenderPool.sol
  cd "$ORIGINAL_DIR"
  execute_group 26 echo "[*] Tested 0 warnings for Sublime p2"
  sleep 3
fi

#Group 27 Volt
if [[ $# -eq 0 || $1 -eq 27 ]]; then
  solc-select use 0.8.6
  cd "../Benchmark/Volt/contracts/oracle"
  slither --detect tcheck ScalingPriceOracle.sol
  cd "$ORIGINAL_DIR"
  execute_group 27 echo "[*] Tested 0 warnings for Volt"
  sleep 3
fi

#Group 28 Badger Dao p3
if [[ $# -eq 0 || $1 -eq 28 ]]; then
  solc-select use 0.8.12 
  cd "../Benchmark/Badger_Dao_p3/src"
  slither --detect tcheck StakedCitadel.sol
  cd "$ORIGINAL_DIR"
  execute_group 28 echo "[*] Tested 0 warnings for Badger Dao p3"
  sleep 3
fi

#Group 29 Tigris Trade
if [[ $# -eq 0 || $1 -eq 29 ]]; then
  solc-select use 0.8.12   
  cd "../Benchmark/Tigris_Trade/contracts"
  slither --detect tcheck Trading.sol
 cd "$ORIGINAL_DIR"
  execute_group 29 echo "[*] Tested 5 warnings for Tigris Trade"
  sleep 3
fi

echo "Testing complete"
