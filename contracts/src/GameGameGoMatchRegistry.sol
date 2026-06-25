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
        bytes32 resultCommitment;
        MatchStatus status;
        address creator;
    }

    address public owner;
    mapping(address => bool) public verifiers;
    mapping(bytes32 => MatchRecord) public matches;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event VerifierGranted(address indexed verifier, address indexed admin);
    event VerifierRevoked(address indexed verifier, address indexed admin);
    event MatchCreated(
        bytes32 indexed matchId,
        bytes32 indexed gameId,
        bytes32 indexed rulesetVersion,
        bytes32 participantsHash,
        address creator
    );
    event MatchActivated(bytes32 indexed matchId, address actor);
    event MatchResolved(bytes32 indexed matchId, bytes32 resultCommitment, address verifier);
    event MatchCancelled(bytes32 indexed matchId, address actor);

    error Unauthorized();
    error MatchAlreadyExists();
    error MatchDoesNotExist();
    error InvalidLifecycle();
    error EmptyValue();
    error ZeroAddress();

    constructor(address initialOwner) {
        if (initialOwner == address(0)) revert ZeroAddress();
        owner = initialOwner;
        emit OwnershipTransferred(address(0), initialOwner);
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }

    modifier onlyVerifier() {
        if (!verifiers[msg.sender]) revert Unauthorized();
        _;
    }

    function transferOwnership(address newOwner) external onlyOwner {
        if (newOwner == address(0)) revert ZeroAddress();
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    function grantVerifier(address verifier) external onlyOwner {
        if (verifier == address(0)) revert ZeroAddress();
        verifiers[verifier] = true;
        emit VerifierGranted(verifier, msg.sender);
    }

    function revokeVerifier(address verifier) external onlyOwner {
        if (verifier == address(0)) revert ZeroAddress();
        verifiers[verifier] = false;
        emit VerifierRevoked(verifier, msg.sender);
    }

    function createMatch(bytes32 matchId, bytes32 gameId, bytes32 rulesetVersion, bytes32 participantsHash) external {
        if (matchId == bytes32(0) || gameId == bytes32(0) || rulesetVersion == bytes32(0) || participantsHash == bytes32(0)) {
            revert EmptyValue();
        }
        if (matches[matchId].status != MatchStatus.None) revert MatchAlreadyExists();

        matches[matchId] = MatchRecord({
            gameId: gameId,
            rulesetVersion: rulesetVersion,
            participantsHash: participantsHash,
            resultCommitment: bytes32(0),
            status: MatchStatus.Created,
            creator: msg.sender
        });

        emit MatchCreated(matchId, gameId, rulesetVersion, participantsHash, msg.sender);
    }

    function activateMatch(bytes32 matchId) external {
        MatchRecord storage record = matches[matchId];
        if (record.status == MatchStatus.None) revert MatchDoesNotExist();
        if (record.status != MatchStatus.Created) revert InvalidLifecycle();
        if (record.creator != msg.sender && msg.sender != owner) revert Unauthorized();
        record.status = MatchStatus.Active;
        emit MatchActivated(matchId, msg.sender);
    }

    function cancelMatch(bytes32 matchId) external {
        MatchRecord storage record = matches[matchId];
        if (record.status == MatchStatus.None) revert MatchDoesNotExist();
        if (record.status != MatchStatus.Created && record.status != MatchStatus.Active) revert InvalidLifecycle();
        if (record.creator != msg.sender && msg.sender != owner) revert Unauthorized();
        record.status = MatchStatus.Cancelled;
        emit MatchCancelled(matchId, msg.sender);
    }

    function submitVerifiedResult(bytes32 matchId, bytes32 resultCommitment) external onlyVerifier {
        if (resultCommitment == bytes32(0)) revert EmptyValue();
        MatchRecord storage record = matches[matchId];
        if (record.status == MatchStatus.None) revert MatchDoesNotExist();
        if (record.status != MatchStatus.Active) revert InvalidLifecycle();
        record.resultCommitment = resultCommitment;
        record.status = MatchStatus.Resolved;
        emit MatchResolved(matchId, resultCommitment, msg.sender);
    }
}
