# Troubleshooting

## Pygame Cannot Open a Window

For headless checks, use:

```bash
set SDL_VIDEODRIVER=dummy
set SDL_AUDIODRIVER=dummy
python -m tools.smoke_test
```

## Temp Cleanup Errors on Windows

Use `-p no:cacheprovider` with pytest in restricted sandboxes. The repository's
`pytest.ini` also excludes sandbox temp cache folders from collection.

## Oasis Config Errors

`BLOCKCHAIN_MODE=offline` or `BLOCKCHAIN_MODE=local` requires no network config.
`oasis_testnet` intentionally fails fast unless RPC, chain, match registry and
ROFL service URL settings are present.
