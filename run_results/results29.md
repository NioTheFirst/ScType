Project name: Tigris Trade

Expected Warnings(2):
```
[TP, 1] typecheck error: Var name: TMP_275 Func name: _handleDeposit in IF tigAsset.balanceOf(address(this)) != _balBefore + _margin

[TPP, 1] typecheck error: Var name: TMP_83 Func name: addToPosition in NEW VARIABLE _newPrice = _trade.price * _trade.margin / _newMargin + _price * _addMargin / _newMargin
```

Explanation of [TP, 1]: `_margin` from `_handleDeposit()` is categorized as a net balance, since when function `addToPosition()` calls `_handleDeposit()`, the parameter `_margin` is set to be `_addMargin`, a raw balance subtracted by `fee`, which is a fee. 
Hence, when `_margin` is comapred with `_balBefore`, a raw balance, there is a financial type mismatch.` 

True Positives List:
1) https://github.com/code-423n4/2022-12-tigris-findings/issues/236
