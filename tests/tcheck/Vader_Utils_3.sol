import "./interfaces/iERC20.sol";
contract C{
    uint public pooledVADER;
    uint public pooledUSDV;
    address public VADER;
    address public USDV;
    mapping(address => uint) public mapToken_tokenAmount;
    function getAddedAmount(address _token, address _pool) internal returns(uint addedAmount) {
        uint _balance = iERC20(_token).balanceOf(address(this));
        if(_token == VADER && _pool != VADER){  // Want to know added VADER
            addedAmount = _balance - pooledVADER;
            pooledVADER = pooledVADER + addedAmount;
        } else if(_token == USDV) {             // Want to know added USDV
            addedAmount = _balance - pooledUSDV;
            pooledUSDV = pooledUSDV + addedAmount;
        } else {                                // Want to know added Asset/Anchor
            addedAmount = _balance - mapToken_tokenAmount[_pool];
        }
    }
}
