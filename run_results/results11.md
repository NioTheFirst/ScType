Project name: 

Expected Warnings (8):

```
[FP] typecheck error: Var name: reserve1 Func name: mint in EXPRESSION reserve1 -= uint128(amount1fees)

[FPP] typecheck error: Var name: reserve0 Func name: mint in EXPRESSION reserve0 -= uint128(amount0fees)

[TP 1, 2] typecheck error: Var name: amount0 Func name: burn in EXPRESSION amount0 += amount0fees

[TPP] typecheck error: Var name: amount1 Func name: burn in EXPRESSION amount1 += amount1fees

[FP] typecheck error: Var name: reserve0 Func name: collect in EXPRESSION reserve0 -= uint128(amount0fees)

[FP] typecheck error: Var name: reserve1 Func name: collect in EXPRESSION reserve1 -= uint128(amount1fees)

[FP] typecheck error: Var name: reserve1 Func name: _updateReserves in EXPRESSION reserve1 -= uint128(amountOut)

[FPP] typecheck error: Var name: reserve0 Func name: _updateReserves in EXPRESSION reserve0 -= uint128(amountOut)
```

Explanation of [TP, 1]: The

True Positives List:
1) https://github.com/code-423n4/2021-09-sushitrident-2-findings/issues/24
2) https://github.com/code-423n4/2021-09-sushitrident-2-findings/issues/51

