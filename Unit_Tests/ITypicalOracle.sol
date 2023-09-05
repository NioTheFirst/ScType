pragma solidity 0.6.12;

interface ITypicalTokenWrapper{
    function price(address A, address B) external view returns(uint256 price);
}
