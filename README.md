# Overview
ScType is a static analysis tool written in Python3 to detect accounting errors in Solidity smart contracts. 

Sctype leverages the single-static-assignment representation produced by [Slither](https://github.com/crytic/slither) to perform abstract type inference. It assigns initial abstract types to select variables based on a type file or inference from the code. Then, the abstract types are propogated throughout the contract based on the produced representation and typechecked accordingly.

ScType checks each individual function within the code. Users are able to specify the abstract types of the initial function parameters through the type file, however the majority of abstract type assignment to variables is done through propogation. 

ScType can handle simple variables as well as arrays and object fields. It can also handle function calls as long as the function is located within the user-defined scope. This includes calls to functions outside of the current file being checked. See the section "Build and Run from Source Code" for more information on usage and scope.

In the following sections, we introduce the structure of the repository for ScType, describe and point out locations of core components, explain how to  compile the source code, and finally, how to pull and run a provided Docker Image in order to reproduce the results in our paper.


ScType is applying for:

1. Available. ScType is publically available on [Github](TODO). We have also provided a runnable image of the tool on [Dockerhub](https://hub.docker.com/repository/docker/icse24sctype/full/general) and provide instructions to pull and run below.

2. Reusable. We provide the source code as well as an explanation to key components of ScType below. We also include detailed isntructions on how to reproduce the results obtained in the paper. Finally, ScType is built on top of Slither, a well-known open-source project.


# Introduction to the Repository

`|Sctype`

`|--- README.md`

`|--- LICENSE`

`|--- test_benchmark_final.sh`

`|--- create_typefile.md`

`|--- financial_type_keys.py`

`|--- run_results`

`|--- slither/detectors/my_detectors`

`README.md` is the file you are currently reading now.

`LICENSE` contains the license for ScType.

`test_benchmark_final.sh` is the script used for running ScType on the dataset provided in the paper. More details can be found in the "Docker" section.

`create_typefile.md` contains instructions on how to manually build type files.

`financial_type_keys.py` stores a copy of a table from `tcheck_parser.py` that contains the mappings of financial types and their keys. More information can be found in `create_typefile.md`.

`run_results` is a repository that contains the expected results from running ScType on the dataset used in the paper. More information can be found in the README.md file located there.

`slither/detectors/my_detectors` is a directory that contains all of the files that are used by ScType.

All other code is unimportant or used by Slither.

# Introduction to Core Components

The following section describes the core components of ScType and where they are located. 

## Abstract Type

The abstract type as introduced by Fig. 6 in our paper is defined in `ExtendedType.py`. 
It provides additional information to variables, such as token units, scaling factor, and financial type.

In particular, for every variable intermediate representation (IR) produced by Slither, there is a field, `extok`, that contains the ExtendedType object defined in `ExtendedType.py`.

For development or debugging, simply inputting the following python code `print({var}.extok)` where `{var}` is a variable IR will display information about the variable including the three aforementioned attributes, as well as fields and addresses. 

## Type File Parsing

The type file provides initial abstract types for selected global variables or function parameters.
Detailed information can be found in `create_typefile.md`

All of the type files for the testing dataset have already been provided; when counting the number of annotations made for type files, we exclude the ones which provide the return values of functions not in scope. We reason that this is a common cost for all static analysis tools and is an effort that we plan to improve upon in furture work.

The parser for the type file is located in `tcheck_parser.py`. It checks each annotation that follows the format as described in `create_typefile.md`, and stores the abstract types in dictionaries for use later in type checking. 
Each variable type has its own dictionary, and can be checked within `tcheck_parser.py`.

## Typechecking Engine

The propogation and typechecking of the tool are implemented in `tcheck.py` and `tcheck_propogation.py`.
`tcheck.py` receives the representation from Slither, and performs the typechecking of individual operations within the function `check_type()`.

In particular, `tcheck.py` receives the SSA from Slither, and first determines which contracts are marked to be typechecked. 
More details on how to do so can be found in `create_typefile.md`.

For the contracts that have been marked, Slither typechecks them one-by-one via the function `_tcheck_contract()`.
Per each contract, the global variables are read, and assigned initial type info if annotations have been provided in the type files.
This is done through the function `_tcheck_contract_state_var()`.

Then, each individual function is used as an entry point and typechecked. 
This is done in the function `_tcheck_function()`.

In particular, the function `_check_type()` typechecks each operation or declaration in the SSA nodes, by calling the appropriate helper function.
Helper functions include `type_bin()`, which checks binary operations, `type_fc()`, which checks calls to functions with the contract, and `type_hlc()`, which checks calls to functions outside of the contract.

Certain helper functions make calls to functions stored in `tcheck_propogation.py`.

`tcheck_propogation.py` stores functions related to the propogation and comparison of the abstract types.
For example, function `pass_ftype()` takes as parameters a LHS variable, a RHS variable, and the name of a binary operation, and checks to see if it is in violation of the financial type propogation rules.

We have selected one of the helper functions to explain more in detail, in particular `type_bin_add()`, which is used to typecheck addition operations.

#### Explanation for function `type_bin_add()`

`type_bin_add()` takes as parameters: a destination variable (`dest`), the left operand variable of the addition (`lir`), and the right operand variable of the addition (`rir`).

If both operands are not undefined or constant variables, the token units are compared through the function calls `compare_token_type()` and `handle_trace()`.

If the token units are incompatible, an error is added.

If not, the scaling factors of the operands are compared and the result is passed to the destination variable via the function call `bin_norm()`.

Additionally, `type_bin_add()` checks whether or not the addition operation violated any financial type rules by calling `pass_ftype()`, which in turn calls the `pass_ftype()` function in `tcheck_propogation.py` that was previously mentioned.

Then, the appropriate token units are assigned to the destination variable, and `type_bin_add()` returns.


# Build and Run from Source Code

To compile the source code, navigate to the home directory of ScType and run:

`pip3 install . --upgrade`

ScType requires the target file(s) to be compiled. Hence, any dependencies for the files must also be installed. These instructions are usually provided by the developers of smart contracts.

To run ScType against a specific file, navigate to the directory of the file and run:

`slither --detect tcheck {target_file_name}`

To run ScType against a directory, run:

`slither --detect tcheck .`

ScType will be able to automatically typecheck calls to any functions as long as the function is located within the directory. 

However, ScType needs type files to be made for each contract that shall be typechecked. Details on how to do so can be found in the `create_typefile.md` file.

# Docker

The following section describes how to pull the docker image from Dockerhub and how to reproduce the results in the paper.

## Setup

Docker needs to be installed in order to pull the image. It can be installed [here](https://docs.docker.com/engine/install/). 

To pull the image for ScType, ensure there is at least 24 GB of storage available and run the following command:

`docker pull icse24sctype/full:latest`

To run the image as a container, run the following command:

`docker run -it icse24sctype/full`

Doing so should create an interactable shell. Commands in all later sections should be run inside that shell.

## Understanding ScType Output


For each project, ScType will output warnings corresponding to code impacted by an erroneous accounting bug.

Individual warnings are output with green text with the following format: 

`>typecheck error: Var name: A Func name: B in C`

This warning means that the variable IR variable "A" located within function "B" is incorrect, and the problematic operation or declaration is within IR "C".

The total number of warnings reported by the tool are reported in the following line in the following format:

`>XXX analyzed ... XXX result(s) found`

Expected warnings for each project are reported in the line starting with "[*]":

`>[*] Expected XXX warnings for XXX `

For most test cases, the number of identified true positives will be less than the reported warnings. This is due to the propogation of a single accounting error throughout multiple operations within the contract. 

For a small number of examples, the number of reported warnings may differ by a slight amount from the number of reported number of warnings in the paper. This is due to the order of certain underlying single-static-assignment representations generated by Slither being inconsistent, in particular for Phi propagation representations. 

## Dataset Evaluation

To run ScType against the entire dataset, run the following command within the interactable shell:

`./test_benchmark_final.sh`

The entire execution will take 10 minutes.

To run ScType against individual projects in the dataset, append the index of the project to the previous command.

For example, Vader Protocol p1 is the 2nd project. Hence, to only run ScType against it, input the following command:

`./test_benchmark_final.sh 2`

The number of warnings from the execution will match the ones reported on the paper.

We briefly go over the reproduceable results in the paper as follows.

### Table 3: Evaluation Results

The data from table 3 was obtained by running ScType against the entire dataset: 

The number of annotations was obtained through the metric defined in the "Type File Parsing" section.

The reported number of warnings is directly the amount reported by the tool.

The number of true positives, false positives, missed-type-errors and not-type-errors were determined by manual inspection of the warnings. The expected results and distribution of true and false positives can be found in the `run_results` directory. 
See the README.md file within for more details.

The execution time of the tool was obtained by using a clock within the testing scripts.
