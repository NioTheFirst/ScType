// SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.6;

import "../../libraries/DrawRingBufferLib.sol";

/**
 * @title  Expose the DrawRingBufferLib for unit tests
 * @author PoolTogether Inc.
 */
contract DrawRingBufferLibHarness {
    using DrawRingBufferLib for DrawRingBufferLib.Buffer;

    uint16 public constant MAX_CARDINALITY = 256;
    DrawRingBufferLib.Buffer internal drawRingBuffer;

    constructor(uint8 _cardinality) {
        drawRingBuffer.cardinality = _cardinality;
    }

    function _push(DrawRingBufferLib.Buffer memory _buffer, uint32 _drawId)
        external
        pure
        returns (DrawRingBufferLib.Buffer memory)
    {
        return DrawRingBufferLib.push(_buffer, _drawId);
    }

    function _getIndex(DrawRingBufferLib.Buffer memory _buffer, uint32 _drawId)
        external
        pure
        returns (uint32)
    {
        return DrawRingBufferLib.getIndex(_buffer, _drawId);
    }

    function _isInitialized(DrawRingBufferLib.Buffer memory _buffer) external pure returns (bool) {
        return DrawRingBufferLib.isInitialized(_buffer);
    }
}
