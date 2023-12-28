Project name: 

Expected Warnings (10):

```
[FP] typecheck error: Var name: reserve1 Func name: mint in EXPRESSION reserve1 -= uint128(amount1fees)

[FPP] typecheck error: Var name: reserve0 Func name: mint in EXPRESSION reserve0 -= uint128(amount0fees)

[FP] typecheck error: Var name: amount0 Func name: burn in EXPRESSION amount0 += amount0fees

[FPP] typecheck error: Var name: amount1 Func name: burn in EXPRESSION amount1 += amount1fees

[TP, 1, 2] typecheck error: Var name: reserve0 Func name: burn in EXPRESSION reserve0 -= uint128(amount0fees)

[TPP, 1, 2] typecheck error: Var name: reserve1 Func name: burn in EXPRESSION reserve1 -= uint128(amount1fees)

[FP] typecheck error: Var name: reserve0 Func name: collect in EXPRESSION reserve0 -= uint128(amount0fees)

[FPP] typecheck error: Var name: reserve1 Func name: collect in EXPRESSION reserve1 -= uint128(amount1fees)

[FP] typecheck error: Var name: reserve1 Func name: _updateReserves in EXPRESSION reserve1 -= uint128(amountOut)

[FPP] typecheck error: Var name: reserve0 Func name: _updateReserves in EXPRESSION reserve0 -= uint128(amountOut)
```

Explanation of [TP, 1, 2]: Inside the `burn()` function, both global variables representing a financial type of total supply (`reserve0`, `reserve1`) are decremented by variables (`amount0fees`, `amount1fees`), respectively, which have financial types of transaction fee. 
This is not allowed, as the transaction fee financial type should not be subtracted from total supply, only added to it.
The correct behviour should have been tp decremented by `amount0` and `amount1`, which represent `net balance`, as reported in the true positive reports.


However, ScType also reports false positives in functions `collect()` and `mint()`, as the `amount0fees` and `amount1fees` represent earnings for a contract instead of a transaction fee. We leave handling this case to our future work.

True Positives List:
1) https://github.com/code-423n4/2021-09-sushitrident-2-findings/issues/24
2) https://github.com/code-423n4/2021-09-sushitrident-2-findings/issues/51

