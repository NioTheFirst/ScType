Project name: BadgerDao

Expected Warnings(2):

```
[TP, 1] typecheck error: Var name: TMP_637 Func name: manualRebalance in IF newLockRatio <= currentLockRatio

[TPP, 1] typecheck error: Var name: TMP_643 Func name: manualRebalance in NEW VARIABLE cvxToLock = newLockRatio.sub(currentLockRatio)

```
Explanation of [TP, 1]: `newLockRatio` represents a token amount while `currentLockRatio` represents a decimal percentage. 
These two objects are incompatible.
Hence, ScType throws warnings for the compare operation `newLockRatio <= currentLockRatio` as well as for the subtraction operation between the two variables, as the token units and decimals of the two variables
do not match.

True Positives List:
1) https://github.com/code-423n4/2021-09-bvecvx-findings/issues/47

