Project name: Vader Protol p3

Expected Warnings (4):
```
[TP, 2] typecheck error: Var name: TMP_56 Func name: _updateVaderPrice in EXPRESSION currentLiquidityEvaluation = (reserveNative * previousPrices[uint256(Paths.VADER)]) + (reserveForeign * getChainlinkPrice(pairData.foreignAsset))

[TPP, 2] typecheck error: Var name: TMP_98 Func name: _addVaderPair in NEW VARIABLE pairLiquidityEvaluation = (reserveNative * previousPrices[uint256(Paths.VADER)]) + (reserveForeign * getChainlinkPrice(foreignAsset))

[TPP, 1, 3] typecheck error: Var name: TMP_130 Func name: _updateUSDVPrice in EXPRESSION currentLiquidityEvaluation = (reserveNative * previousPrices[uint256(Paths.USDV)]) + (reserveForeign * getChainlinkPrice(address(foreignAsset)))

[TP, 1, 3] typecheck error: Var name: TMP_172 Func name: _addUSDVPair in NEW VARIABLE pairLiquidityEvaluation = (reserveNative * previousPrices[uint256(Paths.USDV)]) + (reserveForeign * getChainlinkPrice(address(foreignAsset)))
```

Explanation of [TP, 1, 2, 3]: The price computed for `_calculateUSDVPrice()` is incorrect due to incorrect values returned from the oracle, `getChainLinkPrice()`. Hence, the `previousPrices[]` array, which stores the incorrect prices, leads to token type mismatches in the various functions that invoke it. 

True Positives List:
1) https://github.com/code-423n4/2021-12-vader-findings/issues/42
2) https://github.com/code-423n4/2021-12-vader-findings/issues/148
3) https://github.com/code-423n4/2021-12-vader-findings/issues/70
