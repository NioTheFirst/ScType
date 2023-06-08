
contract C{
    uint i_am_storage = 6;
    uint storage_b;
    uint storage_b2;
    int b2;
    uint tokenA;
    uint tokenB;
    function prog(int b, int c) public returns(int x){
        x = b-c;
	return x;
    }
    function i_am_a_backdoor() public{
	tokenA = 0;
        b2 = 0;
	b2 = b2-5;
	int c = b2 / b2;
	bool d = b2 > c;
	if(b2 > c){
            d = true;
	}
	int e = c+b2*b2;
	prog(b2, c);
        selfdestruct(msg.sender);
    }
}
