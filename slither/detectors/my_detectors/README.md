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
