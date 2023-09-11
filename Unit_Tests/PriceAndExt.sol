pragma solidity ^0.8.0;
import "./ITypicalTokenWrapper.sol";
import "./ITypicalOracle.sol";

//oracle getprice (global:USDC / global:WETH)
// 1, -999.... / 2, -998  +/-  -997 .../ -996
// -999 + -998  {-999, -998} 
// 1, 2, 3, global
// -999, -998, -997 temp
// {1, -999, -998}, {2, -...}

contract BalanceAndNormTest{
    address reserveTokenA;
    address reserveTokenB;
    address oracle;
    uint256 priceAInB;

    /*constructor(address _reserveTokenA, address _reserveTokenB) public{
	reserveTokenA = _reserveTokenA;
	reserveTokenB = _reserveTokenB;
    }*/

    function priceIncluded(address A, address B) public returns(uint256){
        uint256 price = ITypicalTokenWrapper(A).balanceOf(address(this))/ITypicalTokenWrapper(B).balanceOf(address(this));
        return(price);
    }
    
    function priceGlobal() public returns(uint256){
        return(priceAInB);
    }

    function priceExternal(addressA, address B) public returns(uint256){
        return(ITypicalOracle(oracle).price(A, B));
    }
	
    function seeReserveTotal(address reserve, uint256 amount) public returns(uint256){
	//see if amount becomes the same type as reserveToken
	uint256 amt = ITypicalTokenWrapper(reserve).balanceOf(address(this))+amount;
        return(amt);
    }

    function addPriceIncluded(uint256 amountA, uint256 amountB) public returns (uint256){
        uint256 totalA = seeReserveTotal(reserveTokenA, amountA);
        uint256 totalB = seeReserveTotal(reserveTokenB, amountB);
        uint256 totalBConverted = totalB * priceIncluded(reserveTokenA, reserveTokenB);
        uint256 total = totalA + totalBConverted;
        return(total);
    }

    function addPriceGlobal(uint256 amountA, uint256 amountB) public returns (uint256){
        uint256 totalA = seeReserveTotal(reserveTokenA, amountA);
        uint256 totalB = seeReserveTotal(reserveTokenB, amountB);
        uint256 totalBConverted = totalB * priceGlobal();
        uint256 totalBConverted2 = totalB * priceAInB;
        uint256 total = totalA + totalBConverted;
        uint256 total2 = totalA + totalBConverted2;
        return(total);
    }
    
    function addPriceExternal(uint256 amountA, uint256 amountB) public returns (uint256){
        uint256 totalA = seeReserveTotal(reserveTokenA, amountA);
        uint256 totalB = seeReserveTotal(reserveTokenB, amountB);
        uint256 totalBConverted = totalB * priceExternal(reserveTokenA, reserveTokenB);
        uint256 total = totalA + totalBConverted;
        return(total);
    }
}

