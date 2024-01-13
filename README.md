# Purpose

ScType is a static analysis tool written in Python3 to detect accounting errors in Solidity smart contracts. It can be found on [Github](https://github.com/NioTheFirst/ScType).

ScType leverages the single-static-assignment representation produced by [Slither](https://github.com/crytic/slither) to perform abstract type inference. It assigns initial abstract types to select variables based on a type file or inference from the code. Then, the abstract types are propogated throughout the contract based on the produced representation and typechecked accordingly.

ScType checks each individual function within the code. Users are able to specify the abstract types of the initial function parameters through the type file, however the majority of abstract type assignment to variables is done through propogation. 

ScType can handle simple variables as well as arrays and object fields. It can also handle function calls as long as the function is located within the user-defined scope. This includes calls to functions outside of the current file being checked. See the section "Build and Run from Source Code" for more information on usage and scope.

In the following sections, we describe how to pull a Docker image for ScType, and how to reproduce the key results from our paper using the image.

The Docker Image requires 24GB of space.

ScType is applying for:

1. Available. ScType is publically available on [Github](https://github.com/NioTheFirst/ScType). We have also provided a runnable image of the tool on [Dockerhub](https://hub.docker.com/repository/docker/icse24sctype/full/general) and provide instructions to pull and run below.

2. Reusable. We provide detailed instructions on how to reproduce the results in the paper. We also provide an explanation of key components of ScType and how developers can leverage our tool in the file [`README_dev.md`](https://github.com/NioTheFirst/ScType/blob/main/README-dev.md) in this directory.
Finally, ScType is built on top of Slither, a well-known open-source project. Using open-source code improves reusability by making the code easier to understand.


# Provenance

ScType is publically available in this repository on [Github](https://github.com/NioTheFirst/ScType), and a runnable docker image of the tool can be found on [Dockerhub](https://hub.docker.com/repository/docker/icse24sctype/full/general). Please refer to the "Setup" section for more details.

The DOI for this repository on Zenodo is provided below:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10449162.svg)](https://doi.org/10.5281/zenodo.10449162)

The pre-print for the corresponding paper to this artifact, _Towards Finding Accounting Errors in Smart Contracts_, can be found in this repository. For convenience, the [link](https://github.com/NioTheFirst/ScType/blob/main/icse2024-paper1049.pdf) is provided.

# Setup

The following subsections detail how to pull the Docker image and how to understand the output of the artifact.

## Pulling the Docker Image

Docker needs to be installed in order to pull the image. It can be installed [here](https://docs.docker.com/engine/install/). 

To pull the [Dockerhub](https://hub.docker.com/r/icse24sctype/full) image for ScType, ensure there is at least 24 GB of storage available and run the following command:

`docker pull icse24sctype/full:latest`

The pull should take around 40 minutes to finish.

To run the image as a container, run the following command:

`docker run -it icse24sctype/full`

Doing so should create an interactable shell. __Commands in the "Usage" section below should be run inside that shell__.

## Understanding ScType Output

For each project, ScType will output warnings corresponding to code impacted by an erroneous accounting bug.

Individual warnings are output with green text with the following format: 

`>typecheck error: Var name: A Func name: B in C`

This warning means that the intermediate representation (IR) variable "A" located within function with name "B" is incorrect, and the problematic operation or declaration is within IR expression "C".

The total number of warnings reported by the tool are reported in the following line in the following format:

`>XXX analyzed ... XXX result(s) found`

Expected warnings for each project are reported in the line starting with "[*]":

`>[*] Expected XXX warnings for XXX `


# Usage

The following subsections detail a basic usage command to test the artifact docker image installation, and how to reproduce the major results in our paper.

## Basic Usage Command

In order to test the installation of the image, please run the following command within the interactable shell produced by the Docker Image. 

`./test_benchmark_final.sh 1`

Refer to the "Setup" section for instructions on how to download the Docker Image and produce the interactable shell.

The output of the command should look like the following screenshot:

![Expected Results of MarginSwap](https://github.com/NioTheFirst/ScType/blob/main/Expected_results_marginswap.png)

This output is produced by running ScType against the first smart contract project in our dataset, MarginSwap. 

## Reproducing Major Results

To run ScType against the entire dataset, run the following command within the interactable shell:

`./test_benchmark_final.sh`

The entire execution will take 10 minutes.

The expected results of the batch execution can be found in `expected_results.txt`.

To run ScType against individual projects in the dataset, append the index of the project to the previous command.

For example, Vader Protocol p1 is the 2nd project. Hence, to only run ScType against it, input the following command:

`./test_benchmark_final.sh 2`

Individual results are found in the `run_results` repository. See the `README.md` file within for more information.

For most test cases, the number of identified true positives will be less than the reported warnings. This is due to the propogation of a single accounting error throughout multiple operations within the contract. 

For a small number of examples, the number of reported warnings may differ by a slight amount from the number of reported number of warnings in the paper, `expected_results.txt` file, and the `run_results` repository. This is due to the order of certain underlying single-static-assignment representations generated by Slither being inconsistent, in particular for Phi propagation representations. 

We briefly go over the reproduceable results in the paper as follows.

### Table 3: Evaluation Results

The data from table 3 on page 8 of our [paper](https://github.com/NioTheFirst/ScType/blob/main/icse2024-paper1049.pdf) was obtained by running ScType against the entire dataset: 

The number of annotations was obtained through the metric defined in the "Type File Parsing" section of the file [`README-dev.md`](https://github.com/NioTheFirst/ScType/blob/main/README-dev.md), which can be found in this directory.

The reported number of warnings is directly the amount reported by the tool.

The number of true positives, false positives, missed-type-errors and not-type-errors were determined by manual inspection of the warnings. The expected results and distribution of true and false positives can be found in the `run_results` directory. 
See the `README.md` file within for more details.

The execution time of the tool was obtained by using a clock within the testing scripts.
