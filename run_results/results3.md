Project name: Pool Together

Expected Warnings(1):

`[TP, 1] typecheck error: Var name: redeemedUnderlyingAsset Func name: redeemToken in EXPRESSION redeemedUnderlyingAsset += redeemedShare`

Explanation for [TP, 1]: `redeemAmount` is used instead of `redeemShare` in function `redeemToken`. 
These two variables represent amounts of different tokens ("amount" token and "share" token). 
Hence, when the expression `redeemedUnderlyingAsset += redeemedShare` is typechecked, ScType reports an error due to a token type mismatch in the expression with `redeemedUnderlyingAsset`.

True Positives List:
1) https://github.com/code-423n4/2021-06-pooltogether-findings/issues/120

