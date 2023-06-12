contract tFC{
    function add (int a, int b) public returns (int){
        int c = mul(a);
        return b + c;
    }
    function mul (int a) public returns (int){
    	int b = a*10;
	return b;
    }
}
