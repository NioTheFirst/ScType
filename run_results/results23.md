Project name: Rocket Joe

Expected Warnings(3):

```
[TP, 1] typecheck error: Var name: tokenIncentivesForUsers Func name: createPair in EXPRESSION tokenIncentivesForUsers = (tokenIncentivesForUsers * tokenAllocated) / tokenReserve

[TPP, 1] typecheck error: Var name: TMP_114 Func name: createPair in EXPRESSION tokenIncentiveIssuerRefund = tokenIncentivesBalance - tokenIncentivesForUsers

[FP] typecheck error: Var name: tokenIncentivesBalance Func name: withdrawIncentives in EXPRESSION tokenIncentivesBalance -= amount
```

Explanation of [TP, 1]: The computation for `tokenIncentivesForUsers` in function `createPair()` assumes that the token has a scaling factor of 18. 
Hence, when the expresssion is computed for tokens that do not have such a scaling factor, there is a scaling factor mismatch in the reported expression.

True Positives List:

1) https://github.com/code-423n4/2022-01-trader-joe-findings/issues/193

