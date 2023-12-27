Project name: Tracer

Expected Warnings(1):

`[TP, 1] typecheck error: Var name: TMP_33 Func name: applyTrade in EXPRESSION newQuote = position.quote - quoteChange + fee`

Explanation for [TP, 1]: `position.quote` has a financial type of raw balance while `fee` is categorized as a transaction fee. However, `fee` is added to `poition.quote`, which is not allowed, as transaction fees can only be subtracted from raw balances. This is the example used in Fig. 2 in the motivation section of the paper.

True Positives List:
1) https://github.com/code-423n4/2021-06-tracer-findings/issues/127
