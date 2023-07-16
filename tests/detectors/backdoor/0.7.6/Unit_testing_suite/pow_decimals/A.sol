pragma solidity 0.8.3;
contract A{
    struct my_bank{
    	uint256 amount;    //initialize decimals to 6
	uint256 decimals;
    }
    my_bank bank;
    function add_bank(uint256 amount) public{
	bank.decimals = 6;
    	bank.amount += amount^bank.decimals;
    }
}
