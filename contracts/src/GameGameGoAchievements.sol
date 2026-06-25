// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Minimal achievement proof registry
/// @notice MVP only records non-transferable achievement evidence hashes from authorized verifiers.
contract GameGameGoAchievements {
    address public owner;
    mapping(address => bool) public verifiers;
    mapping(address => mapping(bytes32 => bytes32)) public evidenceByPlayerAndAchievement;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event VerifierGranted(address indexed verifier, address indexed admin);
    event VerifierRevoked(address indexed verifier, address indexed admin);
    event AchievementRecorded(address indexed player, bytes32 indexed achievementId, bytes32 evidenceHash, address verifier);

    error EmptyValue();
    error AlreadyRecorded();
    error Unauthorized();
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

    function recordAchievement(address player, bytes32 achievementId, bytes32 evidenceHash) external onlyVerifier {
        if (player == address(0) || achievementId == bytes32(0) || evidenceHash == bytes32(0)) revert EmptyValue();
        if (evidenceByPlayerAndAchievement[player][achievementId] != bytes32(0)) revert AlreadyRecorded();
        evidenceByPlayerAndAchievement[player][achievementId] = evidenceHash;
        emit AchievementRecorded(player, achievementId, evidenceHash, msg.sender);
    }
}
