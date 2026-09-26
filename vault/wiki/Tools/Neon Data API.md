---
type: tool
sources:
  - raw/assign1/Assignment 1_ Secure Networking Tracker.md
  - raw/assign1/README.md
tags:
  - tool
---

# Neon Data API

Neon's PostgREST-based HTTP interface to a Postgres database, called with the end user's own JWT.

## Where it appears

### [[Strada Networking Tracker]]
- A required part of the stack; the frontend may use its public URL, so RLS must protect every exposed contacts row. ([raw/assign1/Assignment 1_ Secure Networking Tracker.md](../../raw/assign1/Assignment%201_%20Secure%20Networking%20Tracker.md))
- The Express API has no Postgres driver or DATABASE_URL; it reaches the database only through the Data API with the user's own token, so RLS scopes every query. ([raw/assign1/README.md](../../raw/assign1/README.md))
- Used alongside [[Ed25519 JWT]], [[Managed Better Auth]], [[Neon Postgres]], [[Row Level Security]], [[Vercel]] in this project.
