Project name: MarginSwap

Expected Warnings (1): 

`[TP, 1] typecheck error: Var name: TMP_57 Func name: updateHourlyBondAmount in NEW VARIABLE deltaAmount = bond.amount - oldAmount`

Explanation for [TP, 1]: `updateHourlyBondAmount()` calls `applyInterest()` to produce `bond.amount`. 
Hence, `bond.amount` has a financial type of accrued balance while `oldAmount` still has financial type of raw balance.
Therefore, ScType detects and error during the subtraction operation reported by the warning.

True Positives List:

1) https://github.com/code-423n4/2021-04-marginswap-findings/issues/64
