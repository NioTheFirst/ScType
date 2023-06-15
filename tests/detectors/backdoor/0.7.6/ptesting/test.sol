pragma solidity ^0.8.3;

import "./Itest2.sol";
contract C{
   struct Source {
        address source;
        uint8 decimals;
        bool inverse;
    }
   
   int[] decimals;
   address _Baddress;
   function cats(int a) public{
       a = a * 10;
       int b = a;
       a = a/100;
       a = a+b;
       int c = IB(_Baddress).x(a);
       //Source memory c = Source({source: address(0), decimals:uint8(b), inverse: true});
       //int d = c.decimals;
       int e = decimals[uint(a)];
   } 
}
