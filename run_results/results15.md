Project name: Vader Protocol p2

For this project, there are three parts. This is from ScType being separately run in three directories.

Part 1:

Part 1 Expected Warnings (4):

```
[TP, 1, 2, 3] typecheck error: Var name: TMP_48 Func name: consult in EXPRESSION result = ((sumUSD * IERC20Metadata(token).decimals()) / sumNative)

[TPP, 1, 2, 3] typecheck error: Var name: TMP_55 Func name: consult in EXPRESSION result = ((sumUSD * IERC20Metadata(token).decimals()) / sumNative)

[TPP, 1, 2, 3] typecheck error: Var name: TMP_41 Func name: consult in EXPRESSION result = ((sumUSD * IERC20Metadata(token).decimals()) / sumNative)

[TPP, 1, 2, 3] typecheck error: Var name: TMP_47 Func name: consult in EXPRESSION result = ((sumUSD * IERC20Metadata(token).decimals()) / sumNative)
```

Explanation of [TP, 1, 2, 3]: The equation for variable `result` in the `consult()` function is incorrect.
This is because the scaling factor, `IERC20Metadata(token).decimals` does not represent the actual scaling factor, but represents the number of decimals, instead. 
For example, instead of 10^18, it returns 18. Hence, ScType returns a decimal mismatch.


Part 1 True Positives List:
1) https://github.com/code-423n4/2021-11-vader-findings/issues/19
2) https://github.com/code-423n4/2021-11-vader-findings/issues/260
3) https://github.com/code-423n4/2021-11-vader-findings/issues/235

Part 2:

Part 2 Expected Warnings (3+5):

The first three warnings will be duplicated. It is a minor side effect of running ScType in a directory.

```
[FP] typecheck error: Var name: totalSupply Func name: mint in EXPRESSION totalSupply += liquidity

[TP, 1] typecheck error: Var name: TMP_222 Func name: swap in EXPRESSION require(bool,string)(foreignAmountOut > 0 && foreignAmountOut <= foreignReserve,BasePool::swap: Swap Impossible)

[TPP, 1] typecheck error: Var name: TMP_211 Func name: swap in EXPRESSION require(bool,string)(nativeAmountOut > 0 && nativeAmountOut <= nativeReserve,BasePool::swap: Swap Impossible)

[FP] typecheck error: Var name: TMP_43 Func name: calculateSwapReverse in NEW VARIABLE numerator = numeratorC - numeratorA - numeratorB

[TP. 2] typecheck error: Var name: TMP_28 Func name: calculateSwap in ENTRY_POINT
```

Explanation of [TP, 1, 2]: The `_swap()` function switches an amount of one token, `nativeAmountIn`, with an amount of a different token, `foreignAmountIn`. 
Hence, when the swap is performed in the `swap()` function call, there are multiple operations that result in token unit mismatches.

Part 2 True Positives List:
1) https://github.com/code-423n4/2021-11-vader-findings/issues/161
2) https://github.com/code-423n4/2021-11-vader-findings/issues/162

Part 3:

Part 3 Expected Warnings (2):
```
[TP, 1] typecheck error: Var name: TMP_40 Func name: _min in IF a < b

[TPP, 1] typecheck error: Var name: TMP_40 Func name: _min in IF a < b
```

Explanation of [TP, 1]: The `reimburseImpermanentLoss()` function call in contract VaderReserve compares a loss amount, `amount` with the current VADER tokens in the reserve, `reserve()`. However, the `removeLiquidity()` function call calls `reimburseImpermanentLoss()` with a loss amount of `coveredLoss`, which was type as a USDV token. Hence, there will be a type mismatch when the two are compared in the `_min()` function call within `reimburseImpermanentLoss()`.

Part 3 True Positives List:
1) https://github.com/code-423n4/2021-11-vader-findings/issues/54

