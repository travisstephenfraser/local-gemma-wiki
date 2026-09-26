---
type: project
project_folder: class2
sources:
  - raw/class2/Class 2 Exercise — Build a Signup Frontend.md
  - raw/class2/README.md
generated_by:
  - google/gemma-4-26b-a4b-qat
tags:
  - project
---

# Class Signup Frontend

This document describes a single-page frontend application for a classroom signup service. It details the implementation of the API interaction, rendering logic, and deployment via Vercel.

## The assignment brief: `Class 2 Exercise — Build a Signup Frontend.md`

This document outlines an exercise to build a responsive single-page application that connects to a shared classroom API. The goal is to create a frontend that can list signups and allow users to add their own names via GET and POST requests.

- Build a responsive single-page app that shows everyone who has signed up and lets you add your own name.
- The API is intentionally public with no login, class code, authentication header, or API key.
- Base URL: https://class2-signups-fall26.vercel.app/api/
- GET /api/signups returns all signups with the newest name first.
- POST /api/signups requires a JSON body with one field: { "name": "Ada Lovelace" }.
- Handle 400, 409, and 500 error codes.
- The app should show loading, empty, success, and error states.
- The app must be ready to deploy to Vercel.

Source: [raw/class2/Class 2 Exercise — Build a Signup Frontend.md](../../raw/class2/Class%202%20Exercise%20—%20Build%20a%20Signup%20Frontend.md)

## My write-up: `README.md`

- The API endpoint is https://class2-signups-fall26.vercel.app/api/.
- The app sends only a name to the API.
- Local development uses npm install and npm run dev.
- The app uses Vitest for testing, specifically for API status handling, ordinal math, and XSS escaping.
- The app uses tsc --noEmit for type checking during the build process.
- The app is deployed using Vercel.
- The app uses Vercel auto-detection for the Vite setup.
- The app uses textContent to prevent XSS attacks.

Source: [raw/class2/README.md](../../raw/class2/README.md)

## Concepts and tools

- [[Dependency Injection]]: api.ts takes fetch as an optional injected argument, which lets the tests exercise every status code without stubbing globals.
- [[Public Unauthenticated API]]: The signup API deliberately has no login, class code, or API key, and the brief warns not to reuse the pattern for private or sensitive data.
- [[UI State Handling]]: The brief requires friendly loading, empty, success, and error states, and treating status 409 as 'That name is already signed up.'
- [[Vercel]]: The assignment specifies that the app should be ready to deploy to Vercel.
- [[Vite]]: The app uses Vite setup and Vercel auto-detection for the Vite setup.
- [[Vitest]]: The app uses Vitest for testing API status handling, ordinal math, and XSS escaping.
- [[XSS Prevention]]: render.ts inserts every name with textContent because anyone can write to the endpoint; a test asserts an <img onerror> name renders as literal text.

## Related projects

- [[Strada Networking Tracker]]: also uses [[Vercel]]

---
See [[Source Catalog]] for file hashes and ingest details.
