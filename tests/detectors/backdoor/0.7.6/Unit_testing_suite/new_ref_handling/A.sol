pragma solidity 0.8.3;

contract A{
    uint a = 0;
    //make mapping here
    mapping(address => bool) public address_bool_map;
    bool[] bool_array;
    mapping(address => int) public address_balance_map;
    int[] balances;
    mapping(address => mapping(int => int)) public d_2_map;
    int[] decimals;

    function bool_array_map(address member) public returns (uint){
        bool d = address_bool_map[member];
        bool e = bool_array[a];
        a = 1+1;
        return a;
    }
    function d_1_array_map(address member) public returns (uint){
        int d = address_balance_map[member];
        int e = balances[a];
        a = 1+1;
        return a;
    }
    function d_2_array_map(address member) public returns (uint){
        int d = d_2_map[member][1];
        a = 1+1;
        return a;
    }
    function decimals_transformation(uint normalized_token_amt) public returns (uint){
	int d = decimals[normalized_token_amt];
        a = 1+1;
        return a;
    }
}
