# Oasis Testnet Deployment

Status: not deployed from this environment.

Future steps:

1. Install and pin Foundry/Oasis tooling.
2. Compile no-wager platform contracts and run Foundry tests.
3. Deploy `GameGameGoMatchRegistry` and `GameGameGoAchievements` only to
   Sapphire testnet.
4. Grant verifier role only to the planned ROFL/testnet verifier account.
5. Write deployed addresses to a versioned address registry.
6. Configure the client with `BLOCKCHAIN_MODE=oasis_testnet`, `OASIS_RPC_URL`,
   `OASIS_CHAIN_ID`, `MATCH_REGISTRY_ADDRESS` and `ROFL_SERVICE_URL`.
7. Build/register the ROFL verifier bundle.
8. Run mocked RPC/ROFL integration tests, then live end-to-end testnet
   verification.

`GameGameGoResultRegistry` is deprecated and must not be deployed as a source
of truth for results.

Never commit private keys or seed phrases.
