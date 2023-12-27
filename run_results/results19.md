Project name: Sublime

Sublime is split into two parts, due to ScType being run in two separate directories.

Part 1:

Expected Warnings (1):
`[TP, 1] typecheck error: Var name: TMP_357 Func name: liquidate in NEW VARIABLE _returnETH = amount.sub(_borrowTokens,Insufficient ETH to liquidate)`

Explanation of [TP, 1]: The function `getLatestPrice()` returns a price that is used incorrectly.
The contract assumes the price to be `tok(borrow_token)/tok(collateral_token)`, but the inverse is returned.
Hence, there is a token mismatch in function `liquidate`, as `_borrowTokens` relies on the price returned by `getLatestPrice()`. 

True Positives List:
1) https://github.com/code-423n4/2021-12-sublime-findings/issues/155

Part 2:

Expected Warnings (4):
```
[FP] typecheck error: Var name: TMP_113 Func name: _depositERC20 in EXPRESSION sharesReceived = IERC20(vault).balanceOf(address(this)).sub(sharesBefore)

[FP] typecheck error: Var name: TMP_100 Func name: _depositETH in EXPRESSION sharesReceived = IERC20(vault).balanceOf(address(this)).sub(initialTokenBalance)

[TP, 1] typecheck error: Var name: TMP_88 Func name: getTokensForShares in EXPRESSION amount = IyVault(liquidityToken[asset]).getPricePerFullShare().mul(shares).div(1e18)

[TPP, 1] typecheck error: Var name: TMP_87 Func name: getTokensForShares in EXPRESSION amount = IyVault(liquidityToken[asset]).getPricePerFullShare().mul(shares).div(1e18)
```

Explanation of [TP, 1]: The decimals computed for `amount` in `getTokensForShares()` are incorrect, which causes a scaling factor mismatch. Functions `_depositERC20

True Positives List:
1) https://github.com/code-423n4/2021-12-sublime-findings/issues/134
