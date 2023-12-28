## Run Results Description
The following describes how to compare the warnings reported from the tool to the results reported in the paper.

The expected results of ScType run against the projects in the dataset are recorded in the files in this directory. Specifically, each of the 29 projects has a file corresponding to the expected results from running ScType on it. The index of the project on Table 3 of the paper corresponds to the index of the file in this directory. For example, MarginSwap is the 1st project in the table, and its expected results are located in results1.md.

Within each of the files is the name of the project, a numbered list of all the reported warnings by ScType, an explanation of the first TP warning if there is one, and a numbered list of all the true positive reports reported by ScType.

For each reported warning, a label is given that follows one of the four formats:

1) [FP], which is the first instance of a False Positive Warning.

2) [FPP], which stands for a propogation of a False Positive Warning.

3) [TP, {number}], which stands for the first instance of a True Positive Warning, along with the index of the true positive in the true positive list below.

4) [TPP, {number}], which stands for a propogation of a True Positive Warning, along with the index of the true positive in the true positive list below.

For example, 

`[TP, 1] typecheck error: Var name: TMP_57 Func name: updateHourlyBondAmount in NEW VARIABLE deltaAmount = bond.amount - oldAmount`

means that the warning is the first instance of the accounting error reported by the first true positive in the true positives list.

For certain true positive warnings, there may be more than one index, i.e. `[TP, 2, 3]... `.
This means that the warning is a consequence of the second and the third true positive accounting errors in the true positives list.

## Error propagation

The following depicts a simple example of how one accounting error can lead to multiple warnings thrown by ScType:

```solidity
wrongBalanceTokA = balanceOf(addressTokB) //should be addressTokA
...
totalBalanceTokA -= wrongBalanceTokA      //ScType warning 1
...
otherBalanceTokA += wrongBalanceTokA      //ScType warning 2
```

For the provided example, there are two tokens, token A and token B.
`totalBalanceTokA` and `otherBalanceTokA` are both amounts of token A.

`balanceOf(addressTokB)` returns an amount of token B, when the amount for `wrongBalanceTokA` was intended to be of token A.

As a result, the subtraction `totalBalanceTokA -= wrongBalanceTokA` and the addition `otherBalanceTokA += wrongBalanceTokA` would both have token unit mismatches.

The true positive accounting error would only report the first expression, `wrongBalanceTokA = balanceOf(addressTokB)` as problematic, as that is the root cause.

However, ScType will report two warnings, due to the token unit mismatches.




## True and False Positive Statistics

True Postives found: 29

False Positives found: 14

