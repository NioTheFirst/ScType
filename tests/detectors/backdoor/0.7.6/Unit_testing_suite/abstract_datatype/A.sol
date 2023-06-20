pragma solidity 0.8.3

contract A{
   int _balAConcrete = 0;
   int _balBConcrete = 0;
   address _tokenA;
   address _tokenB;
   function addbalance(address token, int tokenAmt, int otherTokenAmt) public returns (int){
       //token, tokenAmt, and otherTokenAmt will be assigned abstract types, with otherTokenAmt assigned a different abstract type than the first two
       if(token == _tokenA){
		_balAConcrete+=tokenAmt;
                _balAConcrete-=tokenAmt;
                _balAConcrete*=tokenAmt;
                _balAConcrete/=tokenAmt;
       }
       else{
                _balBConcrete+=tokenAmt;
                _balBConcrete-=tokenAmt;
                _balBConcrete*=tokenAmt;
                _balBConcrete/=tokenAmt;
       }
       //no other errors should be thrown except for here
       tokenAmt += otherTokenAmt
       return(tokenAmt);
   }
}
