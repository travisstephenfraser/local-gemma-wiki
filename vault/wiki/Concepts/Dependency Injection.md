---
type: concept
sources:
  - raw/class2/README.md
tags:
  - concept
---

# Dependency Injection

Passing a component its collaborators as arguments instead of having it reach for globals.

## Where it appears

### [[Class Signup Frontend]]
- api.ts takes fetch as an optional injected argument, which lets the tests exercise every status code without stubbing globals. ([raw/class2/README.md](../../raw/class2/README.md))
- Used alongside [[Public Unauthenticated API]], [[UI State Handling]], [[Vercel]], [[Vite]], [[Vitest]], [[XSS Prevention]] in this project.
