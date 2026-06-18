// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Game Game Go platform match registry
/// @notice No wagering, deposits, payouts, tokens, or fees are implemented.
contract GameGameGoMatchRegistry {
    enum MatchStatus {
        None,
        Created,
        Active,
        Resolved,
        Cancelled
    }

    struct MatchRecord {
        bytes32 gameId;
        bytes32 rulesetVersion;
        bytes32 participantsHash;
        bytes32 resultHash;
        MatchStatus status;
        address creator;
    }

    mapping(bytes32 => MatchRecord) public matches;

    event MatchCreated(bytes32 indexed matchId, bytes32 indexed gameId, bytes32 indexed rulesetVersion, bytes32 participantsHash);
    event MatchActivated(bytes32 indexed matchId);
    event MatchResolved(bytes32 indexed matchId, bytes32 resultHash);
    event MatchCancelled(bytes32 indexed matchId);

    error MatchAlreadyExists();
    error MatchDoesNotExist();
    error InvalidLifecycle();
    error EmptyValue();

    function createMatch(bytes32 matchId, bytes32 gameId, bytes32 rulesetVersion, bytes32 participantsHash) external {
        if (matchId == bytes32(0) || gameId == bytes32(0) || rulesetVersion == bytes32(0)) revert EmptyValue();
        if (matches[matchId].status != MatchStatus.None) revert MatchAlreadyExists();

        matches[matchId] = MatchRecord({
            gameId: gameId,
            rulesetVersion: rulesetVersion,
            participantsHash: participantsHash,
            resultHash: bytes32(0),
            status: MatchStatus.Created,
            creator: msg.sender
        });

        emit MatchCreated(matchId, gameId, rulesetVersion, participantsHash);
    }

    function activateMatch(bytes32 matchId) external {
        MatchRecord storage record = matches[matchId];
        if (record.status == MatchStatus.None) revert MatchDoesNotExist();
        if (record.status != MatchStatus.Created) revert InvalidLifecycle();
        record.status = MatchStatus.Active;
        emit MatchActivated(matchId);
    }

    function cancelMatch(bytes32 matchId) external {
        MatchRecord storage record = matches[matchId];
        if (record.status == MatchStatus.None) revert MatchDoesNotExist();
        if (record.status != MatchStatus.Created && record.status != MatchStatus.Active) revert InvalidLifecycle();
        if (record.creator != msg.sender) revert InvalidLifecycle();
        record.status = MatchStatus.Cancelled;
        emit MatchCancelled(matchId);
    }

    function submitResult(bytes32 matchId, bytes32 resultHash) external {
        if (resultHash == bytes32(0)) revert EmptyValue();
        MatchRecord storage record = matches[matchId];
        if (record.status == MatchStatus.None) revert MatchDoesNotExist();
        if (record.status != MatchStatus.Active) revert InvalidLifecycle();
        record.resultHash = resultHash;
        record.status = MatchStatus.Resolved;
        emit MatchResolved(matchId, resultHash);
    }
}

