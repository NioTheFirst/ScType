Project name: Vader Protol p1

Expected Warnings (4):

[FP]  typecheck error: Var name: TMP_169 Func name: calcShare in IF part > total

[FPP] typecheck error: Var name: TMP_232 Func name: calcCoverage in NEW VARIABLE _depositValue = B0 + (T0 * B1) / T1

[TP, 1] typecheck error: Var name: TMP_222 Func name: calcAsymmetricShare in NEW VARIABLE numerator = ((part1 * part2) - part3) + part4

[TP, 2] typecheck error: Var name: TMP_195 Func name: calcLiquidityUnits in NEW VARIABLE _units = (((P * part1) + part2) / part3)

Explanation for [TP, 1]: The equation for calcAsymmetricShare is incorrect, as previously in the function, part1 is calculated as (U x a), part2 is calculated as (U x U) and part3 is calculated as (U x u), where 'U' and 'u' stand for amounts of one token while a stands for an amount of another. 
Hence, the mathematical subtraction of ((part1 x part2) - part3 ... is reported as incorrect, as part1 x part2 has units of tok(U)^3 x tok(a) while part3 has units of tok(U)^2. This warning is the example used in Fig 1. of the motivation section.

True Positives List:
1) https://github.com/code-423n4/2021-04-vader-findings/issues/214
2) https://github.com/code-423n4/2021-04-vader-findings/issues/204
