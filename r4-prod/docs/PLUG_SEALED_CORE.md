# Plugging sealed core (enterprise)

Goal: run the same gateway surface, but replace stub RNG with sealed core.

## Contract between gateway and RNG backend
Gateway calls an RNG backend via a configured binary / endpoint.
In the public repo we ship:
- `tools/re4_dump_stub` (demo-only)

Enterprise options:
1) **Binary plugin**:
   - Provide `re4_dump` on disk
   - Set `RNG_BIN=/path/to/re4_dump`
   - Mount it into container/host (volume/secret)

2) **Private registry image**:
   - Run `r4-core-sealed` from private registry
   - Gateway points to it via `CORE_URL`

## Recommended enterprise packaging
- keep sealed artifact outside this repo
- deliver as:
  - encrypted download + customer-specific key
  - or private registry tag + short-lived token
- include SBOM + checksum for audit
