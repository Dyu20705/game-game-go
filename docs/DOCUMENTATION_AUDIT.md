# Documentation Audit

Status: repository-hardening audit after the modular-monolith and blockchain
prephase work.

| Statement / Area | Implementation Truth | Status | Action |
| --- | --- | --- | --- |
| Game Game Go is a desktop Pygame platform | `src.main` boots `src.platform.app`; games register through `src.platform.bootstrap` | Accurate | Keep and simplify in README |
| Color Wars legacy root modules exist | `src/ai`, `src/engine`, `src/game`, `src/view` and `src/controller.py` are removed | Stale in old checkpoint docs only | Keep historical checkpoint docs, update current docs |
| SquareXO has online/testnet mode | `src/games/square_xo/runtime/online_session.py` raises disabled MVP error | Speculative | README says local 1v1 only; docs keep testnet as future work |
| Nuts & Bolts has bundled SFX | `SoundManager` no-ops for missing game SFX | Accurate as limitation | Keep in game doc |
| Blockchain/Oasis is deployed | Contracts/ROFL are scaffolded and unit-tested; no live deployment | Stale if implied elsewhere | README and deployment docs say not deployed |
| ROFL is trusted production attestation | Python service boundary is unit-tested; no bundle/register/deploy | Speculative | Security/blockchain docs say pre-testnet only |
| Rewards/token/wallet flow is live | Library UI has local status labels; no real token/reward/wallet settlement | Speculative | README says no real-money/token flow |
| PyInstaller ColorWars spec is current | `GameGameGo.spec` still produced `ColorWars`; removed | Stale | Delete spec and references |
| Docker is production deployment | Docker is only test/smoke/local noVNC demo | Speculative | Add Docker demo docs with warning |
| Tests import legacy paths | Tests import `src.games.color_wars.*` and architecture tests guard this | Accurate | Keep architecture tests |
| README command `python -m src.main` works | Verified through smoke path/imports | Accurate | Keep |
| Full suite passes | `py -m pytest -q -p no:cacheprovider` passes locally | Accurate | Keep current result in testing docs |

## Current Documentation Map

- Landing page: `README.md`
- Docs index: `docs/README.md`
- Architecture: `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE_REFACTOR_REPORT.md`, `docs/SRC_DEPENDENCY_AUDIT.md`
- Games: `docs/games/*.md`
- Development/testing: `docs/development/*.md`, `docs/TESTING.md`
- Deployment: `docs/deployment/docker_demo.md`, `docs/OASIS_TESTNET_DEPLOYMENT.md`
- Security: `docs/security/security_policy.md`, `docs/THREAT_MODEL.md`
- Roadmap: `docs/roadmap/*.md`

Historical checkpoint reports are kept as project history and should not be
treated as the current source of truth.
