# Security

Never commit private keys, seed phrases, real wallet files, production RPC
credentials or deployment secrets.

Local gameplay must not require a wallet. Testnet signing must be explicit,
cancellable, labeled with network/action and must not retry signing forever.

Game Game Go does not implement real-money wagering, deposits, withdrawals,
fees, token payouts, NFT payouts or mainnet value settlement.

SquareXO source wagering contract was audited and intentionally not connected to
the user-facing flow.

Current blockchain trust/authorization details are tracked in:

- `docs/BLOCKCHAIN_PREPHASE_AUDIT.md`
- `docs/RESULT_COMMITMENT_SPEC.md`
- `docs/THREAT_MODEL.md`

Only authorized verifier roles may write result commitments or achievement
evidence in the prephase contract boundary. Local/offline play remains wallet
free and is not treated as authoritative on-chain settlement.
