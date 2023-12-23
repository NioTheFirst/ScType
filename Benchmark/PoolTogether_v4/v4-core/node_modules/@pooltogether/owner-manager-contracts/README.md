# PoolTogether Owner Manager Contracts
[![Coverage Status](https://coveralls.io/repos/github/pooltogether/owner-manager-contracts/badge.svg?branch=master)](https://coveralls.io/github/pooltogether/owner-manager-contracts?branch=master)

![Tests](https://github.com/pooltogether/owner-manager-contracts/actions/workflows/main.yml/badge.svg)

Abstract ownable contract with additional manager role

Contract module based on Ownable which provides a basic access control mechanism, where
there is an account (a draw manager for example) that can be granted exclusive access to
specific functions.

The manager account needs to be set using {setManager}.
 
This module is used through inheritance. It will make available the modifier
`onlyManager`, which can be applied to your functions to restrict their use to the manager.


## Usage
This repo is setup to compile (`nvm use && yarn compile`) and successfully pass tests (`yarn test`)


# Installation
Install the repo and dependencies by running:
`yarn`

## Deployment
These contracts can be deployed to a network by running:
`yarn deploy <networkName>`

## Verification
These contracts can be verified on Etherscan, or an Etherscan clone, for example (Polygonscan) by running:
`yarn etherscan-verify <ethereum network name>` or `yarn etherscan-verify-polygon matic`


# Testing
Run the unit tests locally with:
`yarn test`

## Coverage
Generate the test coverage report with:
`yarn coverage`