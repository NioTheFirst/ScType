pragma solidity 0.8.3;

contract A{
    struct my_struct {
        int tokenA;
        int tokenB;
        int decimals;
        my_struct in_struct;
    }

    my_struct in_struct;

    function addTokenA(my_struct memory struct1, my_struct memory struct2) internal pure returns (int) {
  	struct_1.decimals = 18;
	struct_2.in_struct.decimals = 6;
        return struct1.tokenA + struct2.tokenA;

    }

    // Additional contract logic...
}
