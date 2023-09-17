pragma solidity ^0.8.0;
import "./ITypicalTokenWrapper.sol";
import "./ITypicalOracle.sol";
import "./IImportedContract.sol";

contract CrossContractTest{
    address reserveTokenA;
    address reserveTokenB;
    address oracle;
    address importedContract;
    uint256 priceAInB;

    constructor(address _reserveTokenA, address _reserveTokenB) public{
	reserveTokenA = _reserveTokenA;
	reserveTokenB = _reserveTokenB;
    }

    function testCrossContract(uint256 val) public{
        IImportedContract ic = IImportedContract(importedContract);
	ic.setAToken(reserveTokenA);
	ic.setBToken(reserveTokenB);
	val += 5;
	(uint256 newA, uint256 newB) = ic.mixAdd(seeReserveTotal(reserveTokenA, 0), seeReserveTotal(reserveTokenB, 0));
	uint256 badSum = newA + newB;
	val += badSum;
    } 
	
    function seeReserveTotal(address reserve, uint256 amount) public returns(uint256){
	//see if amount becomes the same type as reserveToken
	uint256 amt = ITypicalTokenWrapper(reserve).balanceOf(address(this))+amount;
        return(amt);
    }

}

