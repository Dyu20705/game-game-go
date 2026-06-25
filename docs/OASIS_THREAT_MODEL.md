# Oasis Threat Model

Public data may include game ID, ruleset version, match ID, participant
commitments and final result hashes.

Client-only or confidential data includes local input timing, animations, UI
state, private keys, seed phrases and deployment secrets.

ROFL may see canonical replay payloads for verification. Sapphire contracts
should store commitments/hashes and lifecycle state, not private gameplay
payloads.

Oasis/ROFL improves integrity and auditability but does not make cheating
impossible. Availability failures must not break offline play.

Current Oasis validation level: local adapters, SquareXO replay verification,
result commitments and the Python ROFL service boundary are unit-tested. Live
Oasis/ROFL deployment remains unvalidated.

The current detailed prephase threat model is maintained in
`docs/THREAT_MODEL.md`.
