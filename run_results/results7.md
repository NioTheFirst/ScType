Project name: yAxis

Expected Warnings (4):

```
[TP, 1] typecheck error: Var name: TMP_182 Func name: balance in RETURN balanceOfThis().add(IController(manager.controllers(address(this))).balanceOf())

[FP] typecheck error: Var name: _totalSupply Func name: _mint in EXPRESSION _totalSupply = _totalSupply.add(amount)

[TP, 2] typecheck error: Var name: TMP_157 Func name: withdraw in NEW VARIABLE _toWithdraw = _amount.sub(_balance)

[TPP, 2] typecheck error: Var name: TMP_164 Func name: withdraw in NEW VARIABLE _diff = _after.sub(_balance)
```

Explanation for [TP, 1]: `balanceOfThis()` normalizes the balance to 18 decimals, while `manager.controllers(address(this))).balanceOf()` is not normalized, and uses the base decimals for the token. Hence, there is a decimal mismatch between the two operands and thus ScType throws a warning. 

True Positives List:
1) https://github.com/code-423n4/2021-09-yaxis-findings/issues/132
2) https://github.com/code-423n4/2021-09-yaxis-findings/issues/131
