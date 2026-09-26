---
type: project
project_folder: assign1
sources:
  - raw/assign1/Assignment 1_ Secure Networking Tracker.md
  - raw/assign1/README.md
generated_by:
  - google/gemma-4-26b-a4b-qat
tags:
  - project
---

# Strada Networking Tracker

Strada is a private contact management application that uses Postgres row-level security to enforce data ownership. The project features a React frontend and an Express backend, with an optional local wiki-sync tool for Obsidian vaults.

## The assignment brief: `Assignment 1_ Secure Networking Tracker.md`

This document outlines the requirements for building a full-stack web application that tracks contacts while ensuring strict data privacy. The project requires implementing user authentication, database persistence, and Row Level Security to prevent unauthorized access between users.

- Build a public web application deployed on Vercel
- Sign-in and sign-out flow using Neon Managed Better Auth
- A private contact list for each authenticated user
- Create, view, edit, delete, sort, and filter contact records
- Priority accepts only high, medium, or low
- Contacts survive a browser refresh
- The contacts table includes a text user_id that defaults to auth.user_id() and cannot be null
- Row Level Security is enabled on the contacts table

Source: [raw/assign1/Assignment 1_ Secure Networking Tracker.md](../../raw/assign1/Assignment%201_%20Secure%20Networking%20Tracker.md)

## My write-up: `README.md`

- Strada is a private record of people to stay close to, behaving like a record rather than a queue.
- The application uses React 19, Vite, TypeScript, and Tailwind CSS v4 for the frontend.
- The backend is built with Express 5 and TypeScript (ESM) and is deployed on Vercel.
- The database is Neon Postgres with Row Level Security (RLS) enforced on the contacts table.
- Authentication is handled via Neon Managed Better Auth using Ed25519 JWTs.
- 188 automated tests: 163 hermetic (npm test) and 25 live (npm run test:rls) covering the two-account privacy proof and the wiki-layer lock.
- The project includes an optional local wiki-sync tool that populates Strada from an Obsidian vault.
- The application supports light, dark, and system themes.

Source: [raw/assign1/README.md](../../raw/assign1/README.md)

## Concepts and tools

- [[Ed25519 JWT]]: The application uses Ed25519 JWTs issued by Neon Managed Better Auth for authentication.
- [[Managed Better Auth]]: The project requires implementing a sign-in and sign-out flow using Managed Better Auth.
- [[Neon Data API]]: A required part of the stack; the frontend may use its public URL, so RLS must protect every exposed contacts row.
- [[Neon Postgres]]: The project requires using Neon Postgres for persistent data storage.
- [[Row Level Security]]: The project requires enabling Row Level Security on the contacts table to ensure users can only access their own data.
- [[Vercel]]: The project requires deploying the final web application on Vercel.

## Related projects

- [[Class Signup Frontend]]: also uses [[Vercel]]

---
See [[Source Catalog]] for file hashes and ingest details.
