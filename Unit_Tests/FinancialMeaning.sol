pragma solidity ^0.8.0;
import "./ITypicalTokenWrapper.sol";
contract FinancialMeaningTest{
    address reserveTokenA;
    address reserveTokenB;
    //uint256 reserveBalance;

    constructor(address _reserveTokenA, address _reserveTokenB) public{
	reserveTokenA = _reserveTokenA;
	reserveTokenB = _reserveTokenB;
    }
	
    function seeReserveTotal(address reserve, uint256 amount) public returns(uint256){
	//see if amount becomes the same type as reserveToken
	uint256 amt = ITypicalTokenWrapper(reserve).balanceOf(address(this))+amount;
        return(amt);
    }


    
}

