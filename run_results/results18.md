Project name: Perennial

Expected Warnings (2):
```
[TPP, 1] typecheck error: Var name: REF_26 Func name: settleAccount in EXPRESSION self.balances[account] = newBalance.abs()

[TP, 1] typecheck error: Var name: TMP_10 Func name: settleAccount in EXPRESSION self.shortfall = self.shortfall.add(shortfall)
```

Explanation for [TP, 1]: Variables `self.shortfall` and `shortfall` are both categorized as debt. 
Hence, ScType produces a financial rule violation when they are added together in the expression, as the same debt should not be added twice.

True Positives List:
1) https://github.com/code-423n4/2021-12-perennial-findings/issues/18
