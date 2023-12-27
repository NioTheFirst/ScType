Project name: Wild Credit

Expected Warnings (4):
```
[TP, 1] typecheck error: Var name: TMP_339 Func name: _supplyCreditUni in RETURN (creditA + creditB)

[TPP, 1] typecheck error: Var name: TMP_204 Func name: accountHealth in NEW VARIABLE totalAccountSupply = creditA + creditB + creditUni

[FP] typecheck error: Var name: TMP_208 Func name: accountHealth in NEW VARIABLE totalAccountBorrow = _borrowBalanceConverted(_account,tokenA,tokenA,priceA,priceA) + _borrowBalanceConverted(_account,tokenB,tokenA,priceB,priceA)

[FP] typecheck error: Var name: REF_75 Func name: _burnSupplyShares in EXPRESSION supplySharesOf[_token][_account] -= _shares
```

Explanation of [TP, 1]: In the function `_supplyCreditUni()`, a price for one token (`_priceB`) is replaced by the price for another toekn (`_priceA`). This leads to the token amounts `creditA` and `creditB` to have mismatching token types hence ScType reports warning 1. 

True Positives List:
1) https://github.com/code-423n4/2021-09-wildcredit-findings/issues/70

