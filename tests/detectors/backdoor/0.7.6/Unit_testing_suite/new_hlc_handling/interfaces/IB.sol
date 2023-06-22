pragma solidity 0.8.3;

interface IB{
    function bool_function(int a) external returns(bool);
    function int_function(int a, int b) external returns(int);
    function decimals() external returns(int);
    function getTokens() external returns(address, int);
}
