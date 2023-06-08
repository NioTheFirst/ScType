// SPDX-License-Identifier: MIT

pragma solidity ^0.6.2;
import "./node_modules/@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./interfaces/ExtendedIERC20.sol";
import "./interfaces/IManager.sol";
import "./interfaces/IController.sol";
import "./node_modules/@openzeppelin/contracts/math/SafeMath.sol";

contract Test{
    using SafeMath for uint256;

    IManager manager;
    uint256 public constant MAX = 10000;

	
    modifier checkToken(address _token) {
        require(manager.allowedTokens(_token) && manager.vaults(_token) == address(this), "!_token");
        _;
    }
     function totalSupply()
	public
	view
	returns (uint256 amt){
        amt = MAX;
     }
     function balance()
        public
        view
        returns (uint256 _balance)
    {
        return balanceOfThis().add(IController(manager.controllers(address(this))).balanceOf());
    }
    function withdraw(
        uint256 _shares,
        address _output
    )
        public
        checkToken(_output)
    {
        uint256 _amount = (balance().mul(_shares)).div(totalSupply());
        //i_burn(msg.sender, _shares);

        uint256 _withdrawalProtectionFee = manager.withdrawalProtectionFee();
        if (_withdrawalProtectionFee > 0) {
            uint256 _withdrawalProtection = _amount.mul(_withdrawalProtectionFee).div(MAX);
            _amount = _amount.sub(_withdrawalProtection);
        }

        uint256 _balance = IERC20(_output).balanceOf(address(this));
        if (_balance < _amount) {
            IController _controller = IController(manager.controllers(address(this)));
            uint256 _toWithdraw = _amount.sub(_balance);
            if (_controller.strategies() > 0) {
                _controller.withdraw(_output, _toWithdraw);
            }
            uint256 _after = IERC20(_output).balanceOf(address(this));
            uint256 _diff = _after.sub(_balance);
            if (_diff < _toWithdraw) {
                _amount = _after;
            }
        }
    }
    function balanceOfThis()
        public
        view
        returns (uint256 _balance)
    {
        address[] memory _tokens = manager.getTokens(address(this));
        for (uint8 i; i < _tokens.length; i++) {
            address _token = _tokens[i];
            _balance = _balance.add(_normalizeDecimals(_token, IERC20(_token).balanceOf(address(this))));
        }
    }
    function _normalizeDecimals(
        address _token,
        uint256 _amount
    )
        internal
        view
        returns (uint256)
    {
        uint256 _decimals = uint256(ExtendedIERC20(_token).decimals());
        if (_decimals < 18) {
            _amount = _amount.mul(10**(18-_decimals));
        }
        return _amount;
    }
}

