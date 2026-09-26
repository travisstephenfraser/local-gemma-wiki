# Class 2 — Signup Sheet

A single-page frontend for the classroom signup service. It lists everyone on the
sheet and lets you add your own name.

**API:** `https://class2-signups-fall26.vercel.app/api/` — public by design for this
exercise. No login, no API key, no class-code header, no database client. The app
sends nothing but a name.

## Run it locally

```sh
npm install
npm run dev      # http://localhost:5173
```

Other commands:

| command | what it does |
| --- | --- |
| `npm test` | Vitest — API status handling, ordinal math, XSS escaping |
| `npm run build` | `tsc --noEmit` then a production bundle into `dist/` |
| `npm run preview` | serve the built `dist/` locally |

## Deploy

Vercel auto-detects the Vite setup; `vercel.json` pins the framework and output
directory.

```sh
vercel --prod
```

The API base URL is absolute, so the deployed origin calls the classroom service
directly rather than its own `/api` path.

## How it's put together

```
index.html          markup and the type/stylesheet links
src/api.ts          getSignups() / addSignup() — the only place fetch is called
src/render.ts       toRows() ordinal math + renderList() DOM building
src/main.ts         state machine, form handling, wiring
src/styles.css      design tokens and layout
```

**`api.ts`** takes `fetch` as an optional injected argument, which is what lets the
tests exercise every status code without stubbing globals. Responses are read as
text and parsed inside a `try`, because a 500 can come back as an HTML error page —
`await response.json()` would throw there and hide the real status behind a parse
error.

**`render.ts`** inserts every name with `textContent`. Names come from an endpoint
anyone can write to, so they are untrusted input; `render.test.ts` asserts that a
name containing `<img onerror=...>` renders as literal text, which is the test that
fails the day someone reaches for `innerHTML`.

Ordinals are derived, not decorative: the API returns newest-first with no ids, so
position is `total - index`. `094` means the ninety-fourth person onto the sheet.

After a successful add the list is refetched rather than patched locally. That
confirms the write landed and keeps the numbering honest when someone else signs up
mid-request.

## Design

The page is a sheet of greenbar continuous-feed printout paper: banded rows, a
tractor-feed strip down the left edge, an oxblood margin rule. The machine's voice
(labels, ordinals, counts, status) is set in IBM Plex Mono; the people printed on it
are set in Source Serif 4.

Light and dark palettes are token swaps under `prefers-color-scheme`. The one
animation — a printer-head sweep across a freshly added row — is skipped under
`prefers-reduced-motion`.
