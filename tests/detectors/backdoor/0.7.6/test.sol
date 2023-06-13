contract C{
   struct Source {
        address source;
        uint8 decimals;
        bool inverse;
    }
   int[] decimals;
   function cats(int a) public{
       a = a * 10;
       int b = a;
       a = a/100;
       a = a+b;
       //Source memory c = Source({source: address(0), decimals:uint8(b), inverse: true});
       //int d = c.decimals;
       int e = decimals[uint(a)];
   } 
}
