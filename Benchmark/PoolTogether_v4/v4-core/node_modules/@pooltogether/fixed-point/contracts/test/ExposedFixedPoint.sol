/**
Copyright 2020 PoolTogether Inc.

This file is part of PoolTogether.

PoolTogether is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation under version 3 of the License.

PoolTogether is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PoolTogether.  If not, see <https://www.gnu.org/licenses/>.
*/

pragma solidity >=0.4.0;

import "../FixedPoint.sol";

contract ExposedFixedPoint {

    function calculateMantissa(uint256 numerator, uint256 denominator) external pure returns (uint256) {
        return FixedPoint.calculateMantissa(numerator, denominator);
    }

    function multiplyUintByMantissa(uint256 b, uint256 mantissa) external pure returns (uint256) {
        return FixedPoint.multiplyUintByMantissa(b, mantissa);
    }

    function divideUintByMantissa(uint256 dividend, uint256 mantissa) external pure returns (uint256) {
        return FixedPoint.divideUintByMantissa(dividend, mantissa);
    }
}
