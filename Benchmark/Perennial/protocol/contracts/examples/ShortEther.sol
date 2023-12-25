// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.10;

import "../product/ProductProviderBase.sol";

contract ShortEther is ProductProviderBase {
    using UFixed18Lib for UFixed18;
    using Fixed18Lib for Fixed18;

    constructor(IOracle oracle) ProductProviderBase(oracle) { }

    // Implementation

    function rate(Position memory position) external pure override returns (Fixed18) {
        if (position.maker.isZero()) return Fixed18Lib.ZERO;

        UFixed18 utilization = position.taker.div(position.maker);
        UFixed18 capped = UFixed18Lib.min(utilization, UFixed18Lib.ONE);
        Fixed18 centered = (Fixed18Lib.from(capped).sub(Fixed18Lib.ratio(1, 2))).mul(Fixed18Lib.from(2));

        return centered.div(Fixed18Lib.from(365 days));
    }

    function payoff(Fixed18 price) public pure override returns (Fixed18) {
        return Fixed18Lib.from(-1).mul(price);
    }

    function maintenance() external pure override returns (UFixed18) {
        return UFixed18Lib.ratio(30, 100);
    }

    function fundingFee() external pure override returns (UFixed18) {
        return UFixed18Lib.ratio(10, 100);
    }

    function makerFee() external pure override returns (UFixed18) {
        return UFixed18Lib.ZERO;
    }

    function takerFee() external pure override returns (UFixed18) {
        return UFixed18Lib.ZERO;
    }

    function makerLimit() external pure override returns (UFixed18) {
        return UFixed18Lib.from(1000);
    }
}
