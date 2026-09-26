# Class 2 Exercise — Build a Signup Frontend

## Connect a frontend to a real, shared classroom API.

# Your task

Build a responsive single-page app that shows everyone who has signed up and lets you add your own name. The API is intentionally public for this classroom exercise: there is no login, class code, authentication header, or API key.  
Use names only. Do not collect or send email addresses or other sensitive information.

# Live service

Base URL: https://class2-signups-fall26.vercel.app/api/

# 1\. Load the signup list

## GET /api/signups

Returns all signups with the newest name first.

`const response = await fetch("https://class2-signups-fall26.vercel.app/api/signups");`

`if (!response.ok) {`

  `throw new Error("Could not load signups");`

`}`

`const { signups } = await response.json();`

Successful response — 200

`{`

  `"signups": [`

    `{ "name": "Ada Lovelace" },`

    `{ "name": "Grace Hopper" }`

  `]`

`}`

# 2\. Add a signup

## POST /api/signups

Send JSON with one field: { "name": "Ada Lovelace" }

`const response = await fetch("https://class2-signups-fall26.vercel.app/api/signups", {`

  `method: "POST",`

  `headers: {`

    `"Content-Type": "application/json"`

  `},`

  `body: JSON.stringify({ name })`

`});`

`const result = await response.json();`

`if (!response.ok) {`

  `throw new Error(result.error || "Could not sign up");`

`}`

Successful response — 201

`{`

  `"signup": { "name": "Ada Lovelace" }`

`}`

## Errors to handle

* 400 — The body is not valid JSON, or the name is missing, empty, or too long.  
* 409 — That exact normalized name is already signed up.  
* 500 — The service had an unexpected problem. Let the user retry.

# Prompt for Claude Code or Codex

Copy the complete prompt below into your AI coding tool:

`Build a clean, responsive single-page frontend for a class signup service.`

`Use this API base URL:`

`https://class2-signups-fall26.vercel.app/api/`

`Requirements:`

`1. When the page loads, send GET /api/signups and render every returned name. The response shape is { "signups": [{ "name": "Ada Lovelace" }] }, newest first.`

`2. Add a form with one required name field and a submit button.`

`3. On submit, send POST /api/signups with Content-Type: application/json and the body { "name": "<the entered name>" }.`

`4. A successful POST returns status 201 and { "signup": { "name": "<the name>" } }. Update or reload the visible list after success, then clear the form.`

`5. Show friendly loading, empty, success, and error states. Treat status 409 as "That name is already signed up." Treat other non-2xx responses using the API's error message when available.`

`6. Disable the submit button while the request is running and prevent empty submissions.`

`7. Make the result easy to use on phones and laptops and ready to deploy to Vercel.`

`8. Do not add authentication, an API key, a class-code header, a database client, email fields, or sensitive data. Use ordinary fetch requests to the API only.`

`Before finishing, run the project's tests or build command and explain how to start it locally.`

# Acceptance checklist

* The page loads and displays the current names.  
* The form collects a name only.  
* A successful submission appears in the list and clears the form.  
* Loading, empty, and request-error states are visible and understandable.  
* Duplicate names produce a friendly message.  
* The app works locally and from a deployed origin.  
* The frontend contains no authentication code, secret, API key, email field, or Supabase client.

# Troubleshooting

* 400 response: confirm the request body is valid JSON and contains a non-empty name.  
* 409 response: use a name that is not already present. Leading, trailing, and repeated spaces are normalized.  
* CORS or network error: confirm you are calling the exact HTTPS URL above, not a relative URL on your own deployment.  
* Nothing appears: open the browser console, inspect the failed request, and show the status and response body to your AI coding tool.

# Classroom safety note

These endpoints are deliberately public for this exercise. Anyone with the URL can read or add names, so submit only a display name you are comfortable sharing with the class. Do not reuse this access pattern for private or sensitive data.  
