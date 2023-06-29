pragma solidity 0.8.3;

contract A{
    struct my_struct2 {
	int token;
	int decimals;
    }

    struct my_struct {
        int tokenA;
        int tokenB;
        int decimals;
        my_struct2 in_struct;
    }

    my_struct[] in_struct;

    function addTokenA(my_struct memory struct1, my_struct memory struct2) external returns (int temp) {
  	struct1.decimals = 18;
	struct2.in_struct.decimals = 6;
	temp = struct1.tokenA + struct2.tokenA;
	in_struct[0].decimals = 3;
        return temp;
	//return;

    }

    // Additional contract logic...
}
