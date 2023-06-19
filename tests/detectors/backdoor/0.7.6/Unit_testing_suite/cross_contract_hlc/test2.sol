pragma solidity ^0.8.3;
contract B{
     int a = 10;
     function x (int b) external returns (int c){
         c = a + b;
	 return(c);
     }
}
