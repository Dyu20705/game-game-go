// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Result commitment registry for Game Game Go
/// @notice Stores only hashes/commitments, never private gameplay payloads.
contract GameGameGoResultRegistry {
    struct ResultRecord {
        bytes32 gameId;
        bytes32 rulesetVersion;
        bytes32 resultHash;
        address submitter;
    }

    mapping(bytes32 => ResultRecord) public resultsByMatch;

    event ResultRecorded(bytes32 indexed matchId, bytes32 indexed gameId, bytes32 indexed rulesetVersion, bytes32 resultHash);

    error ResultAlreadyRecorded();
    error EmptyValue();

    function recordResult(bytes32 matchId, bytes32 gameId, bytes32 rulesetVersion, bytes32 resultHash) external {
        if (matchId == bytes32(0) || gameId == bytes32(0) || rulesetVersion == bytes32(0) || resultHash == bytes32(0)) {
            revert EmptyValue();
        }
        if (resultsByMatch[matchId].resultHash != bytes32(0)) revert ResultAlreadyRecorded();

        resultsByMatch[matchId] = ResultRecord({
            gameId: gameId,
            rulesetVersion: rulesetVersion,
            resultHash: resultHash,
            submitter: msg.sender
        });

        emit ResultRecorded(matchId, gameId, rulesetVersion, resultHash);
    }
}

