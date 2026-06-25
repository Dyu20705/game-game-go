// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../src/GameGameGoAchievements.sol";
import "../src/GameGameGoMatchRegistry.sol";
import "../src/GameGameGoResultRegistry.sol";

contract Actor {
    function create(GameGameGoMatchRegistry registry, bytes32 matchId) external {
        registry.createMatch(matchId, bytes32("square_xo"), bytes32("ruleset_v1"), bytes32("participants"));
    }

    function activate(GameGameGoMatchRegistry registry, bytes32 matchId) external {
        registry.activateMatch(matchId);
    }

    function submit(GameGameGoMatchRegistry registry, bytes32 matchId, bytes32 resultCommitment) external {
        registry.submitVerifiedResult(matchId, resultCommitment);
    }

    function achievement(GameGameGoAchievements achievements, address player, bytes32 achievementId, bytes32 evidenceHash) external {
        achievements.recordAchievement(player, achievementId, evidenceHash);
    }
}

contract GameGameGoMatchRegistryTest {
    bytes32 private constant MATCH_ID = bytes32("match_1");
    bytes32 private constant RESULT = bytes32("result_1");

    function testOwnerCanGrantAndRevokeVerifier() public {
        GameGameGoMatchRegistry registry = new GameGameGoMatchRegistry(address(this));
        Actor verifier = new Actor();

        registry.grantVerifier(address(verifier));
        require(registry.verifiers(address(verifier)), "verifier not granted");
        registry.revokeVerifier(address(verifier));
        require(!registry.verifiers(address(verifier)), "verifier not revoked");
    }

    function testOnlyCreatorOrOwnerCanActivate() public {
        GameGameGoMatchRegistry registry = new GameGameGoMatchRegistry(address(this));
        Actor creator = new Actor();
        Actor stranger = new Actor();
        creator.create(registry, MATCH_ID);

        try stranger.activate(registry, MATCH_ID) {
            revert("stranger activated match");
        } catch {}

        registry.activateMatch(MATCH_ID);
        (,,,, GameGameGoMatchRegistry.MatchStatus status,) = registry.matches(MATCH_ID);
        require(status == GameGameGoMatchRegistry.MatchStatus.Active, "not active");
    }

    function testOnlyVerifierCanResolveAndCannotOverwrite() public {
        GameGameGoMatchRegistry registry = new GameGameGoMatchRegistry(address(this));
        Actor verifier = new Actor();
        registry.createMatch(MATCH_ID, bytes32("square_xo"), bytes32("ruleset_v1"), bytes32("participants"));
        registry.activateMatch(MATCH_ID);

        try verifier.submit(registry, MATCH_ID, RESULT) {
            revert("unverified actor submitted");
        } catch {}

        registry.grantVerifier(address(verifier));
        verifier.submit(registry, MATCH_ID, RESULT);
        (,,, bytes32 resultCommitment, GameGameGoMatchRegistry.MatchStatus status,) = registry.matches(MATCH_ID);
        require(resultCommitment == RESULT, "wrong result");
        require(status == GameGameGoMatchRegistry.MatchStatus.Resolved, "not resolved");

        try verifier.submit(registry, MATCH_ID, bytes32("second")) {
            revert("result overwritten");
        } catch {}
    }

    function testResultRegistryIsNotSourceOfTruth() public {
        GameGameGoResultRegistry registry = new GameGameGoResultRegistry();
        try registry.recordResult(MATCH_ID, bytes32("square_xo"), bytes32("ruleset_v1"), RESULT) {
            revert("result registry accepted write");
        } catch {}
    }

    function testAchievementRequiresVerifier() public {
        GameGameGoAchievements achievements = new GameGameGoAchievements(address(this));
        Actor verifier = new Actor();
        address player = address(0xBEEF);

        try verifier.achievement(achievements, player, bytes32("win_one"), bytes32("evidence")) {
            revert("unverified achievement recorded");
        } catch {}

        achievements.grantVerifier(address(verifier));
        verifier.achievement(achievements, player, bytes32("win_one"), bytes32("evidence"));
        require(
            achievements.evidenceByPlayerAndAchievement(player, bytes32("win_one")) == bytes32("evidence"),
            "achievement missing"
        );
    }
}
