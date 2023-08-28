pragma solidity 0.6.12;

interface ITypicalTokenWrapper{
   function decimals() external view returns (uint8);
   function name() external view returns (string memory);
   function symbol() external view returns (string memory);
   function balanceOf(address account) external view returns (uint256);
   function transfer(address to, uint256 value) external returns (bool);
}
