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

Current Oasis validation level: `STATIC_VALIDATION`.

