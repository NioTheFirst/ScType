#!/bin/bash

cd ..
cd ..
cd ..

cd tests
cd tcheck

num=1
#begin tests
echo "TEST $num================================================="
slither --detect tcheck Vader_Utils_1.sol
((num++))
echo "TEST $num================================================="
slither --detect tcheck Vader_Utils_2.sol
((num++))
echo "TEST $num================================================="
slither --detect tcheck Vader_Utils_3.sol
((num++))

echo "[*] TEST COMPLETE"
