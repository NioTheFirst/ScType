pragma solidity ^0.8.0;
import "./ITypicalTokenWrapper.sol";
contract FinancialMeaningTest{
    address reserveTokenA;
    address reserveTokenB;
    address owner;
    //uint256 reserveBalance;
    uint256 isFeeRatio = 5;
    uint256 compoundFeeRatio = 3;

    constructor(address _reserveTokenA, address _reserveTokenB) public{
	reserveTokenA = _reserveTokenA;
	reserveTokenB = _reserveTokenB;
    }

    function goodFinanceFunctions(address user, uint256 userBalance) public{
         uint256 uBalFee = userBalance * isFeeRatio;
	 uint256 uBalWithFee1 = userBalance - uBalFee;
	 uint256 uBalWithFee2 = userBalance * compoundFeeRatio;

	 uint256 newReserveAmt = seeReserveTotal(reserveTokenA, uBalWithFee1); 
         ITypicalTokenWrapper(reserveTokenA).transfer(owner, newReserveAmt);
    }	
    function seeReserveTotal(address reserve, uint256 amount) public returns(uint256){
	//see if amount becomes the same type as reserveToken
	uint256 amt = ITypicalTokenWrapper(reserve).balanceOf(address(this))+amount;
        return(amt);
    }

    
    
}

