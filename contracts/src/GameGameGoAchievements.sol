// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Minimal achievement proof registry
/// @notice MVP only records non-transferable achievement evidence hashes.
contract GameGameGoAchievements {
    mapping(address => mapping(bytes32 => bytes32)) public evidenceByPlayerAndAchievement;

    event AchievementRecorded(address indexed player, bytes32 indexed achievementId, bytes32 evidenceHash);

    error EmptyValue();
    error AlreadyRecorded();

    function recordAchievement(address player, bytes32 achievementId, bytes32 evidenceHash) external {
        if (player == address(0) || achievementId == bytes32(0) || evidenceHash == bytes32(0)) revert EmptyValue();
        if (evidenceByPlayerAndAchievement[player][achievementId] != bytes32(0)) revert AlreadyRecorded();
        evidenceByPlayerAndAchievement[player][achievementId] = evidenceHash;
        emit AchievementRecorded(player, achievementId, evidenceHash);
    }
}

