pragma solidity ^0.8.0;

interface IImportedContract{
    function setAToken(address A) external;
    function setBToken(address B) external;
    function mixAdd(uint256 amtA, uint256 amtB) external returns (uint256, uint256);
}
