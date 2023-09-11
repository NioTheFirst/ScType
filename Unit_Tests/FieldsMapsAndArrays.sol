pragma solidity ^0.8.0;
import "./ITypicalTokenWrapper.sol";
import "./ITypicalOracle.sol";

//oracle getprice (global:USDC / global:WETH)
// 1, -999.... / 2, -998  +/-  -997 .../ -996
// -999 + -998  {-999, -998} 
// 1, 2, 3, global
// -999, -998, -997 temp
// {1, -999, -998}, {2, -...}

struct MyField {
    uint256 amount;
    address asset;
}



contract FieldsMapsAndArraysTest{
    address reserveTokenA;
    address reserveTokenB;
    mapping(address => uint256) balances;

	
    constructor(address _reserveTokenA, address _reserveTokenB) public{
	reserveTokenA = _reserveTokenA;
	reserveTokenB = _reserveTokenB;
    }

    function testFieldGood(MyField memory myfield) public{
	myfield.amount += ITypicalTokenWrapper(reserveTokenA).balanceOf(msg.sender);
	//myfield.child.asset = reserveTokenB;
    }

    function testFieldBad(MyField memory myfield) public{
	myfield.amount += ITypicalTokenWrapper(reserveTokenA).balanceOf(msg.sender);
	myfield.amount += ITypicalTokenWrapper(reserveTokenB).balanceOf(msg.sender);
    }
}
