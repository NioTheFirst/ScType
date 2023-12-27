# Overview
ScType is a static analysis tool written in Python3 to detect accounting errors in Solidity smart contracts. 

Sctype leverages the single-static-assignment representation produced by [Slither](https://github.com/crytic/slither) to perform abstract type inference. It assigns initial abstract types to select variables based on a type file or inference from the code. Then, the abstract types are propogated throughout the contract based on the produced representation and are typechecked accordingly.

ScType checks each individual function within the code. Users are able to specify the abstract types of the initial function parameters through the type file, however the majority of abstract type assignment to variables is done through propogation. 

ScType can handle simple variables as well as arrays and object fields. It can also handle function calls as long as the function is located within the user-defined scope. This includes calls to functions outside of the current file being checked. See the section "Build and Run from Source Code" for more information on usage and scope.

In the following sections, we introduce the structure of the repository for ScType, describe and point out locations of core components, explain how to  compile the source code, and finally, how to pull and run a provided Docker Image in order to reproduce the results in our paper.


ScType is applying for:

1. Available. ScType is publically available on [Github](TODO). We have also provided a runnable image of the tool on [Dockerhub](https://hub.docker.com/repository/docker/icse24sctype/full/general) and provide instructions to pull and run below.

2. Reusable. We provide the source code as well as an explanation to key components of ScType below. We also include detailed isntructions on how to reproduce the results obtained in the paper. Finally, ScType is built on top of Slither, a well-known open-source project.


# Introduction to the Repository

`|Sctype`

`|--- README-dev.md`

`|--- README-docker.md`

`|--- test_benchmark_final.sh`

`|--- test_benchmark_min.sh`

`|--- create_typefile.md`

`|--- financial_type_keys.py`

`|--- slither/detectors/my_detectors`

`README-dev.md` contains the information written here.

`README-docker.md` contains instructions on how to pull and run the docker image of ScType. Those instructions are included below in the "Docker" section.

`test_benchmark_final.sh` is the script used for running ScType on the dataset provided in the paper. More details can be found in the "Docker" section.

`slither/detectors/my_detectors` is a directory that contains all of the files that are used by ScType.

All other code is used by Slither.

# Introduction to Core Components

The following section describes the core components of ScType and where they are located. 

## Abstract Type

The abstract type as introduced by Fig. 6 in our paper is defined in `ExtendedType.py`. 
It provides additional information to variables, such as token units, scaling factor, and financial type.

## Type File Parsing

The type file provides initial abstract types for select global variables or function parameters.
Detailed information can be found in `create_typefile.md`

All of the type files for the testing dataset have already been provided; when counting the number of annotations made for type files, we exclude the ones which provide the return values of functions not in scope. We reason that this is a common cost for all static analysis tools and is an effort that we plan to improve upon in furture work.

The parser for the type file is located in `tcheck_parser.py`. It checks each annotation that follows the format as described in `create_typefile.md`, and stores the abstract types in dictionaries for use later in type checking. 
Each variable type has its own dictionary, and can be checked within `tcheck_parser.py`.

## Typechecking Engine

The propogation and typechecking of the tool are implemented in `tcheck.py` and `tcheck_propogation.py`.
`tcheck.py` receives the representation from Slither, and performs the typechecking of individual operations within the function `check_type()`.
It handles mainly token unit and scaling factor checking.

`tcheck_propogation.py` performs the more complex typechecking of financial types. In particular, it stores the rules for financial type propogation and verifies that each operation is in accordance. Table 2 in the paper as well as Tables 1-3 in the Appendix are subsets of the rules in this file. 


# Build and Run from Source Code

To compile the source code, navigate to the home directory of ScType and run:

`pip3 install . --upgrade`

ScType requires the target file(s) to be compiled. Hence, any dependencies for the files must also be installed. These instructions are usually provided by the developers of smart contracts.

To run ScType against a specific file, navigate to the directory of the file and run:

`slither --detect tcheck {target_file_name}`

To run ScType against a directory, run:

`slither --detect tcheck .`

ScType will be able to automatically typecheck calls to any functions as long as the function is somewhere within the directory. 

However, ScType needs type files to be made for each contract that needs to be checked. Details can be found in the `create_typefile.md` file.

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

`>typecheck error: Var name: XXX Func name: XXX in XXX`

The total number of warnings reported by the tool are reported in the following line in the following format:

`>XXX analyzed ... XXX result(s) found`

Expected warnings for each project are reported in the line starting with "[*]":

`>[*] Expected XXX warnings for XXX `

For most test cases, the expected warnings will be less than the actual reported warnings. This is due to the propogation of a single accounting error throughout multiple operations within the contract. 

For a small number of examples, the number of reported warnings may differ by a slight amount from the number of reported number of warnings in the paper. This is due to the order of certain underlying single-static-assignment representations generated by Slither being inconsistent, in particular for Phi propagation representations. The reported warnings in the paper are based on the maximum number of warnings so as to include all of the false positives. All true positives are detected.

## Dataset Evaluation

To run ScType against the entire dataset, run the following command within the interactable shell:

`./test_benchmark_final.sh`

The entire execution will take XXX minutes.

To run ScType against individual projects in the dataset, append the index of the project to the previous command.

For example, Vader Protocol p1 is the 2nd project. Hence, to only run ScType against it, input the following command:

`./test_benchmark_final.sh 2`

The number of warnings from the execution will match the ones reported on the paper.

We briefly go over the reproduceable results in the paper

### Table 3: Evaluation Results

The data from table 3 was obtained by running ScType against the entire dataset: 

The number of annotations was obtained through the metric defined in the "Type File Parsing" section.

The reported number of warnings is directly the amount reported by the tool.

The number of true positives, false positives, missed-type-errors and not-type-errors were determined by manual inspection of the warnings.

The execution time of the tool was obtained by using a clock within the testing scripts.

### Fig 9: False Positive Example in Vader Protocol P2


Fig 9 in the paper demonstrates a false positive generated from the tool.

The project is the Vader Protol P2 project, corresponding to number 15 on the table. To run the project, input the command:

`./test_benchmark_final.sh 15`

The corresponding false positive is the warning reported as:

`> typecheck error: Var name: TMP_28 Func name: calculateSwap in NEW VARIABLE denominator = pow(amountIn + reserveIn)`
