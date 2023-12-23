pragma solidity ^0.8.4;

interface IIdleToken{
    function balanceOf(address a) external view returns (uint256);
    function tokenPriceWithFee(address a) external view returns (uint256);
    function mintIdleToken(uint256 amt, bool b, address a) external returns(uint256);
    function redeemIdleToken(uint256 share) external returns(uint256);
}
