pragma solidity ^0.8.0;
import "./ITypicalTokenWrapper.sol";
import "./ITypicalOracle.sol";


contract ImportedContract{
    address reserveTokenA;
    address reserveTokenB;


    function setAToken(address newAToken) external{
	reserveTokenA = newAToken;
    }

    function setBToken(address newBToken) external{
         reserveTokenB = newBToken;
    }

    function mixAdd(uint256 amtA, uint256 amtB) external returns (uint256, uint256){
        uint256 sumA = amtA + ITypicalTokenWrapper(reserveTokenA).balanceOf(address(this));
	uint256 sumB = amtB + ITypicalTokenWrapper(reserveTokenB).balanceOf(address(this));
	return(sumA, sumB); 
    }
}
