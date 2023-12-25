pragma solidity ^0.8.4;

contract IIdleToken{
    uint256 balance = 0;
    uint256 tPWF = 0;
    uint256 tokenToShare = 1;
    function balanceOf(address a) external view returns (uint256){
        return(balance);
    }
    function tokenPriceWithFee(address a) external view returns (uint256){
    	return(tPWF);
    }
    function mintIdleToken(uint256 amt, bool b, address a) external returns(uint256){
        return(amt);
    }
    function redeemIdleToken(uint256 share) external returns(uint256){
    	return(share * tokenToShare);
    }
}
