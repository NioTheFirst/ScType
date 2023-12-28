Project name: Biconomy Hyphen

Expected Warnings (1):

`[TP, 1] typecheck error: Var name: REF_47 Func name: getAmountToTransfer in EXPRESSION incentivePool[tokenAddress] = (incentivePool[tokenAddress] + (amount * (transferFeePerc - tokenManager.getTokensInfo(tokenAddress).equilibriumFee))) / BASE_DIVISOR`

Explanation of [TP, 1]: The expression for `incentivePool[tokenAddress]` in function `getAmountToTransfer()` has a decimal mismatch error.
This is due the inclusion of the divide by `BASE_DIVISOR` at the end, which causes the right-hand-side expression to have 18 less decimals compared to the `incentivePool[tokenAddress]` on the left.

True Positives List:
1) https://github.com/code-423n4/2022-03-biconomy-findings/issues/38
