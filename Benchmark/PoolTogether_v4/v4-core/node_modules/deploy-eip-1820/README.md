# Deploy EIP 1820

Ethereum [EIP 1820](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1820.md) is a standard for pseudo-introspection of smart contracts on Ethereum.

This library ensures that the EIP 1820 registry smart contract exists on any given chain.  Particularly useful for test environments.

Uses [ethers.js v5](https://docs.ethers.io/v5).

If you're using ethers.js v4 then try the 0.2 version.

# Setup

Install `deploy-eip-1820` via yarn:

```sh
$ yarn add deploy-eip-1820
```

or npm:

```sh
$ npm i deploy-eip-1820
```

# Usage

To ensure that the EIP 1820 Registry contract exists on the network you are using, use the `setup1820` function:

```javascript
const { deploy1820 } = require('deploy-eip-1820')

async function deploy() {
    const wallet = ethers.Wallet.fromMnemonic("...your mnemonic...")
    // The wallet must have at least 0.08 Ether
    const registryContract = await deploy1820(wallet)

    // Now we have an Ethers Contract instance for the ERC1820 Registry contract
    let implementer = await registryContract.getInterfaceImplementer('0x1234...', '0xINTERFACE_HASH')
}

```