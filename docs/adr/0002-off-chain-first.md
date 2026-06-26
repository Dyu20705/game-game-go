# ADR 0002: Off-Chain First

## Decision

Local/offline gameplay is the default. Blockchain/Oasis features are optional
integration boundaries and must not be required for normal desktop play.

## Consequences

- No wallet is required for local gameplay.
- Contracts and ROFL service code remain pre-testnet until deployment artifacts
  and live smoke tests exist.
- README and docs must not claim live settlement or production attestation.
