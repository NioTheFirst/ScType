Project name: Swivel

Expected Warnings(2):
```
[TP, 1] typecheck error: Var name: REF_170 Func name: exitVaultFillingVaultInitiate in EXPRESSION Balance[msg.sender] -= fee

[TPP, 1] typecheck error: Var name: REF_171 Func name: exitVaultFillingVaultInitiate in EXPRESSION Balance[msg.sender] -= fee
```

Explanation of [TP, 1]: The `Balance[]` array has a financial type of net balance. It stores the value of `premiumFilled`, a raw balance, decremented by `fee`, a transaction fee, hence becoming a net balance. However, it is again decremented by `fee`, and thus ScType reports the two warnings as shown.

True Positives List:
1) https://github.com/code-423n4/2021-09-swivel-findings/issues/39
