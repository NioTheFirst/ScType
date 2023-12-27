# Overview

The following file details how to create typefiles for Solidity smart contracts. 
First, there will be a section explaining where to put the type file, what is an annotation, the difference between a token type file and a finance type file, and how the total number of annotations is counted.
Then, there will be several sections explaining the several types of annotations for variables.

The types of variables that are supported are:

1) Addresses
2) Integer variables (including all uint and int)
3) Arrays
4) User objects with fields
5) Return values for function calls not included in the scope of the detector run

Additionally, this file will also explain three special annotations in Smart Contracts, which are:

1) The annotation to test a specific file: "[*c]"
2) The annotation to skip typechecking a certain function: "[xf]"
3) The annotation to provide an alias for contracts names: "[alias]".

Finally, this file will state all of the optimizations currently implemented for making type files easier for users.

## Location of the Typefile, Token type file vs Finance type file, and Counting Annotations

### What is a Token Type File? A Finance Type File?

Token type files are type files that store the token units and scaling factors of variables. 
They also store the three special annotations of: testing flag "[*c]", skip flag "[xf]", and aliases "[alias]".

Finance type files store the financial type information of variables.

Each smart contract file to be typechecked by ScType needs a token type file, but the finance type file can be excluded if the user does not wish to typecheck using the financial types as defined in our paper.

The token type file must start with the "[*c]" flag so as to let ScType know to typecheck a file, this can be done by pasting the following command into the first line of the token type file:

`[*c], {exact_contract_name}`

### What is a Type Annotation

A type annotation is a line of text which provides initial abstract type information about a singular variable in a smart contract.

An annotation in a type files is typically made for a global variable or a function parameter. 
In essence, annotations are assigned to the first instance of a variable (if a function name is provided, then it will be the first instance of the variable within the function)

The information to make a type annotation is not difficult to obtain, and can typically be found within comments in the code, or in documents provided by the developer of the smart contract.

### Location and Naming of Type Files

Type files should be in the same directory as the file they pertain to.

The name of a token type file associated with a certain smart contract file should be: `{file_name}_types.txt`

The name of a finance type file associated with a certain file should be: `{file_name}_ftypes.txt`

For example, if the name of the smart contract was `ABC`, the token type file and finance type file names need to be: `ABC_types.txt` and `ABC_ftypes.txt`, respectively.

__It is important to note that the "name" of a smart contract is the name is used for the contract or library within the smart contract file, not necessarily the name of the file itself__

For example, if the file name was `CDE.sol`, but with the file, the contract's name was `ABC`, then `ABC` should be used to name the token type and finance type files.

### Counting Annotations

The total number of annotations as reported in our paper is the sum of the lines in both the token type files and finance type files __EXCLUDING__ the number of annotations made for:
1) Return values for function calls not included in the scope of the detector run
2) The singular annotation for the "[*c]" flag.

## Making Type Annotations

The following section explains how to make annotations for variables belonging to the various types listed in the "Overview" section.
Each section will be split into subsections for token type files and finance type files. 
The annotations made should go into their respective files.

It is important to know that __finance type files are independent from token type files__; it is possible to have annotations for certain variables in a finance type file while not having them in the token type file, or vice versa.

Common attributes of annotations include:
1) `{function_name}` the function a certain variable appears in (including as a parameter), or `global` if the variable is a global variable.
2) `{variable_name}` the name of the variable referred to by the annotation
3) `{scaling_factor}` the number of decimals that the current variable is scaled by. Common examples include 6 (10^6, typical for USDC tokens) or 18 (10^18, typical for ETH tokens)

Other fields will be explained more in detail in their relavant sections.

### Addresses

#### Token Type File

To make annotations for address variables, follow the following format:

`[ta], {function_name}, {variable_name}, {scaling_factor}`

In this case, `{scaling_factor}` refers to the scaling factor that a token of the address has.

For example, if address `USDCaddress` represented the address for the `USDC` token, and was a field of the function `getBalance()` and given that the typical scaling factor for a `USDC` token is 6, the annotation would be:

`[ta], getBalance, USDCaddress, 6`

If the address does not have a scaling factor, it can be dropped completely from the type file.

In general, all addresses with scaling factors will need to have such an annotation, bar the ones with duplicated names and scaling factors. See the "Optimizations" section for more detail.

#### Finance Type File

None, addresses do not have financial types.

### Integer Variables

#### Token Type File

To make token type file annotations for integer variables, follow the following format:

`[t], {function_name}, {variable_name}, {numerator_token_type}, {denominator_token_type}, {scaling _factor}, {value}`

where
1) `{numerator_token_type}` is the numerator token type for the variable. This can be obtained by copying the address of the token from the type file like so:
`{function_name}:{address_name}`. Reusing the address `USDCaddress` from the "Addresses" section, if the variable were an amount of the token referred to by the `USDCaddress`, than its numerator should be `getBalance:USDCaddress`. If unknown, fill with `-1`.
2) `{denominator_token_type}` is exactly the same as the numberator token type, except that it represents the denominator token unit of the variable. It is most commonly used when defining a price of two tokens. If unknown, fill with `-1`
3) `{scaling_factor}` represents the scaling factor for the variable. If unknown, fill with `0`
4) `{value}` represents a value that the variable can take. If unknown, fill with `'u'`

If none of the information is none, the annotation can be excluded entirely.

For example, an integer variable named `priceAToB` in a function `getCost()`  which represents a price of token A over token B, where A and B are both global variables, has a scaling factor of 6, and has an unknown value would be type like so:

`[t], getCost, priceAToB, global:A, global:B, 6, 'u'`

Typically, annotations for token types are not needed since they can be inferred from special functions like `balanceOf()`. Additionally, if they are provided, the user-provided annotation will be prioritized over inference in case of differences (and a warning will be issued).

#### Finance Type File

To make finance type file annotations for integer variables, follow the following format:

`[t], {function_name}, {variable_name}, f:{finance_type_key}`

The `{finance_type_key}` is the integer corresponding to the finance type of the variable. The table is included in `tcheck_parser.py`, and also within the `finance_type_keys.py` file within this directory.

For example, since the price financial type has a key of `40`, an annotation for `priceAToB` defined in the above section would be:

`[t], getCost, priceAToB, f:40`

Generally, these annotation will always need to be provided, as the current system has very few methods to infer them from the code, especially for finance types that are not balances.

### Arrays

#### Token Type File

To make token type file annotations for arrays, follow the following format:

`[tref], {variable_name}, {numerator_token_type}, {denominator_token_type}, {scaling _factor}`

Arrays follow the same rules as Integer variables.

In the event that an array can represent values of different token types, i.e.`balance[]`, do not make an annotation.

#### Finance Type File
To make finance type file annotations for arrays, follow the following format:

  `[tref], {variable_name}, {finance_type_key}`

Arrays follow the same rules as Integer variables

### Objects and Fields

#### Token Type File

To make token type file annotations for objects and fields, follow the following format:

For Objects:

Follow the same rules as the "Integer variables" section

For Fields:

`[t*], {function_name}, {variable_name}, {field_name}, {address}, {scaling_factor}`

or 

`[t*], {function_name}, {variable_name}, {field_name}, {numerator_token_type}, {denominator_token_type}, {scaling_factor}, {value}`

The former is used for addresses; `{address}` is the name of the address as defined in the "Integer variables" section.

The latter is used for integers, it follows the same rules as Integer variables.

To make annotations for fields that are deeper within objects, simply extend the `{variable_name}` with the "_" character.

For example, the annotations required to annotate the field: {myobj.A.B.C} would be:
```
[t*] ..., myobj_a_b, c, ...
```

#### Finance Type File

To make finance type file annotations for objects and fields, follow the following format:

For Objects:

Follow the same rules as the "Integer variables" section.

For Fields:

`[t*], {function_name}, {variable_name}, {field_name}, {finance_type_key}`

### Return Values of Functions Not Included within Detection Scope

The detection scope is all accessible files reachable by Slither. Typically this means the specific file if a selected file is chosen as a target for ScType, or all files in the directory that ScType was called in if the directory is chosen as the target.

For return values of functions that are not included within the detection scope, follow the following format:

`[sefa], {contract_name}, {function_name}, {length of return tuple}, {type for return value one}, {type for return value two}, ...`

where:
1) `{contract_name}` stands for the name of the contract which stores the annotated function
2) `{function_name}` is the name of the annotated function
3) `{length of return tuple}` is the length of the return tuple.

Then, there are `{length of return tuple}` comma-separated, annotations that represent each of the tuple objects, in order. 
If an object in the return tuple does not have much usage (i.e. it is a string or a boolean), simply leave a blank space, add a comma, and move on to the next object.

For all other objects, follow the following format:

#### Token Type File

{`copy or transfer`, `[numerator_token_types]`, `[denominator_token_types]`, `{scaling factor}`, `{value}`, `{address}`}

`copy or transfer` is either a 'c' or a 't' character.
It serves as a flag that determines whether or not this return type is copied from the annotation directly, or is some transformation on the parameters of the function call.

The `{address}` field is only used if there is nothing in both the `[numerator_token_types]` and `[denominator_token_types]` fields.

##### Copy
If the return type for the current object should be copied:
1) `[numerator_token_types]` stores a '[]' enclosed list containing all of the numerator token types in the format defined in the "Integer Variables" section, i.e. `[function1_name:address1_name, function2_name:address2_name, ...]`. If empty, replace with [-1].
2) `[denominator_token_types]` has the exact same format as `[numerator_token_types]` does.
3) `{address}` stores the intended address in the format defined above, i.e. `[function1_name:address1_name]`
The other two parameters are self-explanitory

#### Transfer
If the return type for the current object should be transferred:
1) `[numerator_token_types]` stores a '[]' enclosed list containing the indexes of the function call parameters that make up the numerator of the return type, i.e. `[1, 1, 2]` means that the numerator of the object is made by the units of the first parameter ^2 multiplied by the second parameter. If the parameters are addresses, they are treated as integer amounts of their underlying tokens (if they have any). If empty, replace with [-1].
2) `[denominator_token_types]` follows the same rules as the numerator.
3) `{scaling factor}` holds a single value pertaining to a parameter that has the intended token unit.
4) `{address}` holds a single value pertaining to a parameter that has the same address. 
5) `{value}` holds a single value pertaining to its actual value.

#### Finance Type File

The format for finance type annotations is simply:

{f:`{finance_type_key}`}. 

The `finance_type_key` is always copied.

#### Example

Given a function `getBalances(address B)` in contract `Bank` that has three return values, the first of which is a token balance with scaling factor 6 and unknown value, the second is a string, and the third is simply the parameter of the function call returned, and that the financial type key for raw balances is `0`, the annotations for both files are shown below:

##### Token Type File

`[sefa], Bank, getBalances, 3, {c, [global:token], [-1], 6, 'u'}, , {t, [1], [-1], 1, 'u'}`

##### Finance Type FIle

`[sefa], Bank, getBalances, 3, {f:0}, , `

## Special Annotations

There are three special annotations that can be provided alongside the annotations for variables. 
Special Annotations belong in only the token type file.
They are:

1) `[*c], {contract_name}`, which serves as a flag that notifies ScType to typecheck the contract with the name `{contract_name}`
2) `[xf], {function_name}`, which serves as a flag that notifies ScType to skip checking a particular function within the contract
3) `[alias], used_name, current_name`, which provides an alias for contracts. It is used when the scope of ScType is a directory, and the names of the function call interfaces do not match the names of the actual contracts.
   i.e. if `ICOIN.getBalance()` refers to the `getBalance()` function call with a contract named `MyCoin`, an alias can be provided like so: `[alias], ICOIN, MyCoin`.

## Optimizations

The current optimization that has been performed is the automatic reuse of annotations that share the same names as well as abstract type info. 
For example, if the contract contains 5 function which each have the same parameter, `asset` that has scaling factor 18, instead of:
```
[ta], function1, asset, 6
[ta], function2, asset, 6
...
[ta], function5, asset, 6
```

a single annotation of

`[ta], function1, asset, 6` is all that is required.

This feature is common to both Token and Finance type files.
