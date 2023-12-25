// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;

import "../Ownable.sol";

contract OwnableHarness is Ownable {
    event ReallyCoolEvent(address);

    constructor(address _initialOwner) Ownable(_initialOwner) {}

    function protectedFunction() external onlyOwner {
        // do admin priviledges things

        emit ReallyCoolEvent(msg.sender);
    }
}
