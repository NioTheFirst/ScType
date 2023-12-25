# PoolTogether Yield Source Specification

PoolTogether would like to integrate any protocol that serves as a yield source.  The PoolTogether 3.3.0 contracts introduce a Yield Source Prize Pool, that is bound to a contract that implements the Yield Source Interface.  This is a generic interface that allows a Yield Source Prize Pool to use an external contract for yield.  As long as a contract supports the Yield Source Interface, it can be plugged into the Yield Source Prize Pool.  This makes it easy to add new yield sources.

# Yield Source Interface

The Yield Source Interface is defined in the [IYieldSource.sol](./contracts/IYieldSource.sol) file.

Keep in mind:

- All deposits are denominated in the `depositToken()` ERC20.
- The `balanceOfToken(address)` function is similar to the Aave aToken, in that the balance must always increase.

# Implementations

**Note: these implementations may or may not have been audited.**  They should be considered experimental until proven otherwise.

- [Compound cToken Yield Source](https://github.com/pooltogether/pooltogether-pool-contracts/blob/f3c40ecacc654caa323f956f91e9851703a73111/contracts/yield-source/CTokenYieldSource.sol)
- [Aave aToken Yield Source](https://github.com/pooltogether/aave-yield-source)
- [xSushi Yield Source](https://github.com/steffenix/sushi-pooltogether)
- [Yearn V2 Vault Yield Source](https://github.com/pooltogether/pooltogether-yearnv2-yield-source)
