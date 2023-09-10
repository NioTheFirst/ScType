pragma solidity 0.6.12;
import "./ITypicalTokenWrapper.sol";
contract BalanceAndNormTest{
    address reserveTokenA;
    address reserveTokenB;
    //uint256 reserveBalance;

    /*constructor(address _reserveTokenA, address _reserveTokenB) public{
	reserveTokenA = _reserveTokenA;
	reserveTokenB = _reserveTokenB;
    }*/
	
    function seeReserveTotal(address reserve, uint256 amount) public returns(uint256){
	//see if amount becomes the same type as reserveToken
	uint256 amt = ITypicalTokenWrapper(reserve).balanceOf(address(this))+amount;
        return(amt);
    }

    function addBalanceGood(uint256 amountA, uint256 amountB) public returns (uint256){
        uint256 totalA = seeReserveTotal(reserveTokenA, amountA);
        uint256 totalB = seeReserveTotal(reserveTokenA, amountB);
        uint256 total = totalA + totalB;
        return(total);
    }

    function addBalanceBuild(uint256 amountA, address tokenC, uint256 amountC) public returns (uint256){
       uint256 totalA = seeReserveTotal(reserveTokenA, amountA);
       uint256 totalC = seeReserveTotal(tokenC, amountC);
       uint256 total = totalA + totalC;
       return(total);
    }

    function addBalanceBad(uint256 amountA, uint256 amountB) public returns(uint256){
        uint256 totalA = seeReserveTotal(reserveTokenA, amountA);
	uint256 totalB = seeReserveTotal(reserveTokenB, amountB);
	uint256 total = totalA + totalB;
	return(total);
    }
    
    //VALUE TESTS=================================================================
    function values() public{
        int A = 10;
        int B = 18;
        int C = A + 9;
    }

    function passValue() public{
        uint A = 18;
	A = addTen(A);
	A -= 20;
	A *= 2;
 	A/=4;
	uint normAmt = 10**A;
    }

    function addTen(uint x) public returns (uint){
        return(x + 10);
    }
 
    //NORM TESTS===================================================================
    function normalizeToken(address token, uint256 amount) public returns (uint256){
        uint256 decimals = ITypicalTokenWrapper(token).decimals();
	amount = amount * 10**(18 - decimals);
	return(amount);
    } 
    
    function normComarisonBad(uint256 amountA) public returns (uint256){
        uint256 normAmtA = normalizeToken(reserveTokenA, amountA);
	uint256 badSum = normAmtA + amountA;
	return(badSum);
    } 
   
    function normComarisonGood(uint256 amountA) public returns (uint256){
        uint256 normAmtA = normalizeToken(reserveTokenA, amountA);
        uint256 goodSum = normAmtA + normAmtA;
        return(goodSum);
    }

    
}

