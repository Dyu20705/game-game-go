// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Deprecated result registry placeholder
/// @notice MatchRegistry is the single source of truth for result commitments.
contract GameGameGoResultRegistry {
    error UseMatchRegistry();

    function recordResult(bytes32, bytes32, bytes32, bytes32) external pure {
        revert UseMatchRegistry();
    }
}
