# Game Blockchain Integration Guide

Mini-games may opt into blockchain capabilities, but local play must remain
possible unless a game is explicitly blockchain-only.

Declare capabilities via `GameDescriptor.capabilities`, then use
`context.blockchain.identity`, `context.blockchain.match_registry` and
`context.blockchain.result_verifier`.

Game code must not import web3, Sapphire SDK, ABI files or wallet
implementations from domain logic.

Do not add deposit, withdrawal, payout, token, fee, marketplace or real-money
wagering flows.

