---
type: concept
sources:
  - raw/assign1/Assignment 1_ Secure Networking Tracker.md
  - raw/assign1/README.md
tags:
  - concept
---

# Row Level Security

A security mechanism that restricts database access to specific rows based on user identity.

## Where it appears

### [[Strada Networking Tracker]]
- The project requires enabling Row Level Security on the contacts table to ensure users can only access their own data. ([raw/assign1/Assignment 1_ Secure Networking Tracker.md](../../raw/assign1/Assignment%201_%20Secure%20Networking%20Tracker.md))
- The project uses Postgres RLS to enforce ownership of contacts, ensuring users can only access their own rows. ([raw/assign1/README.md](../../raw/assign1/README.md))
- Used alongside [[Ed25519 JWT]], [[Managed Better Auth]], [[Neon Data API]], [[Neon Postgres]], [[Vercel]] in this project.
