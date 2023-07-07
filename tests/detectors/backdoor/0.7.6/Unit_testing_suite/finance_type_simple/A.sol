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

    function applySimpleInterest(int balanceA) public returns (int){
    	int new_balanceA = balanceA*simpleInterest;
        return new_balanceA;
    }

    function applyCompoundInterest(int balanceA) public returns(int){
    	int new_balanceA = balanceA + balanceA*compoundInterest;
        return new_balanceA;
    }

    function withdrawBalance(int balanceA) public returns (int){
    	int feeA = calculateFee(balanceA);
	int net_balanceA = balanceA - feeA;
        int final_balanceA = applySimpleInterest(balanceA);
	reserveA -= final_balanceA + justConstant + weird;
	updateFee(); //Throw error here (late update)
	return(net_balanceA);
    }

}
