pragma solidity ^0.8.0;

interface ITypicalOracle{
    function price(address A, address B) external view returns(uint256 price);
}
