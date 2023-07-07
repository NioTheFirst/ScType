pragma solidity 0.8.3;

contract A{
    int balanceA = 0;
    int feeRatioA = 0;
    int justConstant = 0;
    int weird = 0;
    int reserveA = 0;
    int simpleInterest = 2;
    int compoundInterest = 3;
    
    function calculateFee(int balanceA) public returns (int){
    	int feeA = balanceA * feeRatioA;
        return feeA;
    }

    function updateFee() public{
        feeRatioA = feeRatioA + 1;
    }

    function withdrawBalance(int balanceA) public returns (int){
    	int feeA = calculateFee(balanceA);
	int net_balanceA = balanceA - feeA;
	reserveA -= net_balanceA;
	updateFee();
	return(net_balanceA);
    }
}
