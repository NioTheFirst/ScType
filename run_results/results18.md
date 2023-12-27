Project name: Perennial

Expected Warnings (2):
```
[TPP, 1] typecheck error: Var name: REF_26 Func name: settleAccount in EXPRESSION self.balances[account] = newBalance.abs()

[TP, 1] typecheck error: Var name: TMP_13 Func name: settleAccount in EXPRESSION self.shortfall = self.shortfall.add(shortfall)
```

Explanation for [TP, 1]: In function `settleAccount()`, `self.shortfall` and `shortfall` are both categorized as debt financial types. 
Hence the operation of `self.shortfall.add(shortfall)` is reported, as it is a wrong calculation which doubles the value of the debt.

True Positives List:
1) https://github.com/code-423n4/2021-12-perennial-findings/issues/18
