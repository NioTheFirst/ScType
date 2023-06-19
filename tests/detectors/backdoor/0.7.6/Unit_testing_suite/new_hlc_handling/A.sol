pragma solidity 0.8.3;
import "./interfaces/IB.sol";

contract A{
    int a = 0;
    address b = address(0);
    function test_bool(int c) external returns(bool){
	//should simply assign constant and move on
	//simple bool handling
    	bool d = IB(b).bool_function(c);
	a = 1+1; //obligatory binary
        return(d);
    }
    function test_int(int balanceA, int balanceB) external returns(int){
        //should reflect the transformation of A^2/B presented in the type file
	int d = IB(b).int_function(balanceA, balanceB);
	a = 1+1; //obligatory binary
        return(d);
    }
}
