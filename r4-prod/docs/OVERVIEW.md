# re4ctor-public — Overview

This repository is a **partner/public** distribution of RE4CTOR:
- builds + demos **without** sealed core access
- supports plugging a sealed core backend later (enterprise)

## What is included (public)
- Gateway API (open integration surface)
- VRF demo node (as-is, for sandbox)
- Stub RNG backend (tools/re4_dump_stub) for demos/tests
- Docs + examples

## What is NOT included
- sealed core RNG binary / proprietary entropy backend
- production keys, Stripe secrets, private infra

## Architecture (high-level)
Client -> Gateway -> (RNG backend + VRF backend)

Public mode:
- RNG backend is a stub (non-production)

Enterprise mode:
- RNG backend is sealed core via plugin (RNG_BIN) or private image
