Typecheck project:

assign a token type to each variable

this variable will be propogated throughout the contract

variables such as units will be kept track of

if there is a faulty comparison of token types then error is reported


First Version:

assign a type 'a' to a singular variable.

Propogate that type throughout a contract.

i.e. b(a) = a(a) * 2(NULL)

b(a) = a(a) + a(a)

b(a) = returna(x,y,z)

returna(x(a),y, z)
    b(a) = x(a)        

script formula:
"function name"
"parameter:"
...
"other:"
...
"---"

for state/global variables, function name is: "global"



next goal:

function call propagation (deadline 6/14/23)

new stuff to add

balance type draft:

balance
interest
fee
final balance
reserve

type harness: support a harness function (external) that is able to call functions in a specified order: this allows for global variable type propagation


Chat GPT prompt (7/20/23)
Here demonstrates a type system that stores the type information of a variable in the form of {numerator, denominator, normalization, and financial meaning}, please help inference new variable types given the following information: Current financial meanings (the fourth parameter) are in this dictionary: -1: "undef",
    0: "raw balance",
    1: "net balance",
    2: "accrued balance",
    3: "final balance",
    10: "compound fee ratio (t)",
    11: "transaction fee",  
    12: "simple fee ratio",
    13: "transaction fee (n)",
    14: "transaction fee (d)",
    20: "simple interest ratio",
    21: "compound interest ratio",
    22: "simple interest",
    23: "compound interest",
    30: "reserve",
    40: "price/exchange rate",
    50: "debt", and these are some examples to make the inference easier: USDCAmount, or an amount of the USDC currency has type information {1, -1, 6, 0}, given that 1 is a token representing USDC and is the numerator, -1 is a token representing nothing in the denominator, 6 is the base value of decimals that the USDCAmount supports, and USDCAmount is a balance, so the financial meaning is 0. WETHamount would have type information {2, -1, 18, 0}, meaning an abstract token 2 representing WETH for the numberator, -1, since there is no denominator, 18, since WETH supports 18 decimals, and 0, since it is a balance. feeNumerator would have type information {-1, -1, 0, 10}, corresponding to no token units in the numerator or denominator, and 10 for financial type, as that represents fee ratio. USDCToWETH would have the type information {2, 1, 12, 0}, as this is used to convert USDC (in this example defined as token unit 1), to WETH (in this example defined as token unit 2). USDCdecimals has  type {-1, -1, 0, 6}. Variable nodef, which represents a constant or bool has the type of {-1, -1, 0, -1}, meaning nothing is defined. Please note that numerator and denominator types should be types of token currency, such as USDC, WETH, ETH, USDT, which can even be defined within the contract itself. They should not take the value of constants, for example if int a = 1000, it has unit {-1, -1, 3, -1}, since there is no associated token currency attributed to a. In the following, a smart contract will be provided, and a prompt for either [t], function_name, variable_name, corresponding to the variable with the variable_name in the function with the function_name, or global if the variable is a global variable, [t*], function_name, variable_name, field_name, which represents the field with field_name of the variable in the function, or [tref], array_name, which represents the entire array with the corresponding name. Please output the corresponding type given the above type system. This type system should only be used with variables and function parameters, which will be asked of you in separate prompts.