pragma solidity 0.6.12;
import "./ITypicalTokenWrapper.sol";
contract BalanceAndNormTest{
    address reserveTokenA;
    address reserveTokenB;
    //uint256 reserveBalance;

    constructor(address _reserveTokenA, address _reserveTokenB) public{
	reserveTokenA = _reserveTokenA;
	reserveTokenB = _reserveTokenB;
    }
	
    function seeReserveTotal(address reserve, uint256 amount) public returns(uint256){
	//see if amount becomes the same type as reserveToken
        return(ITypicalTokenWrapper(reserve).balanceOf(address(this))+amount);
    }

    function addBalanceBad(uint256 amountA, uint256 amountB) public returns(uint256){
        uint256 totalA = seeReserveTotal(reserveTokenA, amountA);
	uint256 totalB = seeReserveTotal(reserveTokenB, amountB);
	uint256 total = totalA + totalB;
	return(total);
    }

    

    
}

