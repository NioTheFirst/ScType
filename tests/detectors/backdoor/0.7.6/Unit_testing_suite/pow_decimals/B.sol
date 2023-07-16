pragma solidity 0.8.3;
contract B{
    struct my_bank{
    	uint256 amount;    //initialize decimals to 6
	uint256 decimals;
    }
    my_bank bank;
    function add_bank(uint256 amount) public{
    	bank.amount += amount^bank.decimals;
    }
}
