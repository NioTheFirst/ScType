[![Node.js CI](https://github.com/Idle-Finance/hardhat-proposals-plugin/actions/workflows/node.js.yml/badge.svg)](https://github.com/Idle-Finance/hardhat-proposals-plugin/actions/workflows/node.js.yml)

# hardhat-proposals-plugin

_A Hardhat plugin for working with on-chain proposals_

## What

A helper plugin for developing and testing on-chain proposals

This plugin will assist in simulating proposals in a Hardhat environment for testing and debugging proposals before they are submitted on-chain.

## Installation


```bash
npm install --save-dev @idle-finance/hardhat-proposals-plugin @nomiclabs/hardhat-ethers ethers
```

Import the plugin in your `hardhat.config.js`:

```js
require("@idle-finance/hardhat-proposals-plugin");
```

Or if you are using TypeScript, in your `hardhat.config.ts`:

```ts
import "@idle-finance/hardhat-proposals-plugin";
```


## Required plugins

- [@nomiclabs/hardhat-ethers](https://github.com/nomiclabs/hardhat/tree/master/packages/hardhat-ethers)

## Tasks

This plugin adds the _proposal_ task to Hardhat:
```
Usage: hardhat [GLOBAL OPTIONS] proposal [--action <STRING>] --governor <STRING> --voting-token <STRING> id

OPTIONS:

  --action              What type of action to perform from options (info) (default: "info") (default: "info")
  --governor            The governor address 
  --voting-token        The voting token registered with the governor 

POSITIONAL ARGUMENTS:

  id    The proposal id 

proposal: Interact with proposals using hardhat
```

## Environment extensions

This plugin extends the Hardhat Runtime Environment by adding the `proposal` field whose type is `ProposalsHardHatRunTimeEnvironmentField`

## Configuration

This plugin extends the `HardhatUserConfig` by adding the `proposals` field whose type is `ProposalsUserConfig`

This is an example of how to set it:

```js
module.exports = {
  proposals: {
    governor: "0x2256b25CFC8E35c3135664FD03E77595042fe31B",
    votingToken: "0x875773784Af8135eA0ef43b5a374AaD105c5D39e"
  }
};
```

## Usage

There are no additional steps you need to take for this plugin to work.

Install it and access proposals through the Hardhat Runtime Environment anywhere
you need it (tasks, scripts, tests, etc).

## Example 

The following example illustrates how to use the plugin.

This example will create a proposal for a `GovernorAlpha` like proposal.

```js
...
export default task(..., async(args, hre) => {
  ...
  let proposer = await hre.ethers.getSigner(PROPOSER)

  let proposal = hre.proposals.builders.alpha()
    .setProposer(proposer)
    .addContractAction(
      DAIInterestRateModelV2, // Contract we are interacting with
      "_setInterestRateModel(address)", // Contract signature
      ['0'] // Method args
    )
    .setDescription("CIP #2 ...") // Set proposal description
    .build()

  await proposal.simulate() // Simulate the execution of the proposal.
})

```

A full project implementation using this plugin can be found [here](https://github.com/asafsilman/test-usdt-proposal)
