# ICSE 2024 Submission: SCType type checker

=======

Ratios and External functions need to be provided for the type file

SCType is a Solidity type checker written in Python 3. 

Currently working on overhaul for type fileeeeee

There are two Docker Images that we have provided for our tool. Both of the images contain the tool, as well as the benchmarks we use.

The full Docker Image holds the complete benchmark set and all of their dependencies. It includes 29 projects. It can be downloaded by running `docker pull icse24sctype/full`. It is 23 GB.

The reduced Docker Image holds one benchmark case and its dependencies. It can be downloaded by running `docker pull icse24sctype/min`. It is 1 GB.

## Benchmark

Our benchmark test cases can be found in the `Benchmark` directory. 

### Reduced verion
This reduced version only contains one project, `Vader_Protocol_p1`.

The benchmark test is run on the `Utils.sol` file in `Benchmark/Vader_Protocol_p1/vader-protocl/contracts`.


## Tests


To run the reduced tests, run the following code: `./test_minbenchmark.sh` in a Linux environment.

To run the full tests, run the following code: `./test_benchmark.sh`.

The type-checking results are in green. The output of the warnings is: Variable name (IR), Function name, and Operation with mistake. Please ignore all other outputs.

For example, one of the three warnings describing the function `calcLiquidityUnits()` of the second benchmark for the full version and the benchmark for the reduced verion is the example case we explain in our Motivation section.

## Source

The source code for our tool can be found in the directory: `slither/detectors/my_detectors`. In particular, `tcheck.py` is the main engine.
