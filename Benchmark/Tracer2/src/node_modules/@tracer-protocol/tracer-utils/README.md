# Description
Utility package for common functions within the Tracer ecosystem. Useful for clients who wish to interact with the Tracer protocol.
# Usage
```
npm install @tracer-protocol/tracer-utils
```

To use any of the packages, simply import the function from the package you wish to use, directly from the tracer-utils library.
```
import { signOrders } from "@tracer-protocol/tracer-utils`
await signOrders(...)
```
# Packages
## OME
This package adds utility functions for interacting with the Tracer [OME](https://github.com/tracer-protocol/tracer-ome).

Supported are the following functions
- createMarket: create a new market on the OME. Markets are identified by their Ethereum address.
- getMarkets: returns all markets currently registered with the OME
- getOrders: returns all orders currently associated with a market
- submitOrder: submits an EIP712 compliant signed order to the OME.

## Signing
This package adds utility functionality for signing orders via the EIP712 [specification](https://eips.ethereum.org/EIPS/eip-712)

Supported are the following functions
- signOrder: sign a single instance of an order via a local Ethereum node using the eth_signTypedData RPC call
- signOrders: sign multiple orders are once.

## Serialisation
This package adds utility functionality for serialising orders between the contracts and the OME

Supported are the following functions
- orderToOMEOrder: converts an order from the raw signed order type to a type supported by the OME
- omeOrderToOrder: converts an order sent from the OME into the type to send it to the contracts

# Development
## Contributing
When creating a new package follow the structure of 

```
-- src
    -- NewUtilsSpace
        -- index.ts // export or main 
        -- source.ts
        -- extra source files or folders
```