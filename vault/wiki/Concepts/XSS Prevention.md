---
type: concept
sources:
  - raw/class2/README.md
tags:
  - concept
---

# XSS Prevention

Rendering untrusted input as literal text (e.g. the DOM textContent property, never innerHTML) so injected markup cannot run.

## Where it appears

### [[Class Signup Frontend]]
- render.ts inserts every name with textContent because anyone can write to the endpoint; a test asserts an <img onerror> name renders as literal text. ([raw/class2/README.md](../../raw/class2/README.md))
- Used alongside [[Dependency Injection]], [[Public Unauthenticated API]], [[UI State Handling]], [[Vercel]], [[Vite]], [[Vitest]] in this project.
