contract AbstractModel {
  IERC20 public T;
  uint public fee_ratio;
  uint public interest_ratio;
  uint public reserve;
  uint public totalSupply;
  unit public price;
  mapping(address => uint) public balance;
  mapping(address => uint) public debt;
  mapping(address => uint) public collateral;

  function deposit(uint raw_amount) public { //deposit USDC for T
      share= exchange(USDC, raw_amount)
      fee_ratio= update_fee(fee_ratio, totalSupply, revenue); 
      fee= share * fee_ratio
      balance[msg.sender]+=share;
      balance[msg.sender]-=fee;
      totalSupply+=share;
      reserve+=fee;
 }
 function withdraw(uint amount) public {
      ... //fee computation
      balance[msg.sender]-=amount;
      balance[msg.sender]-=fee;
      reserve-=amount;
      reserve+=fee;
      totalSupply-=amount;
     
  }
  function accounting() public {
      uint divident = calc_divident(reserve, totalSupply, share[msg.sender])
      reserve-=divident
      balance[msg.sender]+=divident
      uint interest = calc_interest(debt[msg.sender])
      debt[msg.sender]+=interest
      //calc_divident() and calc_interest() represent the core business policies for various DeFi projects 
  }
  function exchange(address T1, uint amount) public {
      price=  T1.balanceof()/totalSupply     //exchange T1 for T, T*T1=k
      unit swapped_amount= amount * price
      ...
  }
  function loan(uint amount, uint collateral) public {
      ... //fee computation
      collateral[msg.sender]+=collateral;
      collateral[msg.sender]-=fee; //Or, debt[msg.sender]+=fee
      debt[msg.sender]+=amount;
      totalSupply-=amount;
      revenue+=fee;
  }
  function payoff (uint amount) public {
      ... //fee computation
      collateral[msg.sender]-=fee; //Or, debt[msg.sender]+=fee
      debt[msg.sender]-=amount;
      totalSupply+=amount;
      revenue+=fee
  }
  function liquidate (uint amount) public {
      collateral[msg.sender] = 0; 
      debt[msg.sender] = 0;
      revenue+= collateral[msg.sender];
  }
}//201 https://github.com/sushiswap/trident/blob/c405f3402a1ed336244053f8186742d2da5975e9/contracts/pool/concentrated/ConcentratedLiquidityPool.sol#L263-L267