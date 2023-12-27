Project name: Yield Micro

Expected Warnings:
```
[TP, 1] typecheck error: Var name: TMP_74 Func name: _peek in EXPRESSION priceOut = priceIn * priceOut / (10 ** source.decimals)

[TPP, 1] typecheck error: Var name: TMP_83 Func name: _get in EXPRESSION priceOut = priceIn * priceOut / (10 ** source.decimals)
```

Explanation for [TP, 1]: As per the report, both the `_peek()` and `_get()` functions use incorrect decimals when computing `priceOut`. Hence when ScType typechecks the operation, it correctly reports the error. 

True Positives List:
1) https://github.com/code-423n4/2021-08-yield-findings/issues/26

