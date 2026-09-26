# Class Notes Wiki

My coursework for the class, turned into linked notes by a local Gemma harness and reviewed by hand. Start with a project, follow a concept or tool into the other projects that use it, and follow any note back to its original in `raw/`.

- [[Source Catalog]]: every original file, its hash, and the note it feeds

## Projects

- [[Strada Networking Tracker]] (`raw/assign1/`): Strada is a private contact management application that uses Postgres row-level security to enforce data ownership.
- [[Ms Pac-Man DQN Agent]] (`raw/assign2/`): This project README describes a 5,000-episode Deep Q-Network training run for Ms. Pac-Man.
- [[Custom nanoGPT Model]] (`raw/assign3/`): This document describes experiments training a nanoGPT model on different corpora to test its ability to learn negation and spatial relations.
- [[Class Signup Frontend]] (`raw/class2/`): This document describes a single-page frontend application for a classroom signup service.

## Concepts

- [[Ablation]]: An experiment that removes or changes one factor while holding the rest fixed, to see what that factor contributes.
- [[Corpus]]: A collection of texts used for training a language model.
- [[Deep Q-Network]]: A reinforcement learning algorithm used to train an agent to make decisions in an environment.
- [[Dependency Injection]]: Passing a component its collaborators as arguments instead of having it reach for globals.
- [[Ed25519 JWT]]: A type of JSON Web Token using the EdDSA signature algorithm.
- [[Eval Leakage]]: Test prompts or answers leaking into training data, which inflates evaluation scores without real learning.
- [[Experience Replay]]: A technique to break correlation between consecutive frames by sampling random batches of past experiences.
- [[Fixed Evaluation Protocol]]: Measuring a model before and after training under identical, frozen evaluation settings so the comparison is fair.
- [[Hyperparameters]]: Parameters set before the beginning of a training process that control the learning behavior of the model.
- [[Margin]]: The probability of the correct choice minus the probability of the best wrong choice.
- [[Next-Token Scoring]]: Grading a language model by which candidate word it assigns the highest next-token probability.
- [[Out-of-Vocabulary Cases]]: Test cases containing words the model never learned, which it cannot score.
- [[Public Unauthenticated API]]: An endpoint anyone can call without credentials, acceptable only for non-sensitive data.
- [[Row Level Security]]: A security mechanism that restricts database access to specific rows based on user identity.
- [[Transformer]]: A neural network architecture used for language modeling.
- [[UI State Handling]]: Designing distinct loading, empty, success, and error views so every request outcome is visible to the user.
- [[Winner's Curse]]: Picking the best of many noisy measurements inflates its score, so the winner underperforms on fresh data.
- [[XSS Prevention]]: Rendering untrusted input as literal text (e.g. the DOM textContent property, never innerHTML) so injected markup cannot run.

## Tools

- [[Managed Better Auth]]: An authentication service for managing user sessions and sign-in flows.
- [[nanoGPT]]: A simplified implementation of the GPT architecture for language modeling.
- [[Neon Data API]]: Neon's PostgREST-based HTTP interface to a Postgres database, called with the end user's own JWT.
- [[Neon Postgres]]: A managed PostgreSQL database service.
- [[PyTorch]]: An open-source machine learning library used for building and training neural networks.
- [[Vercel]]: A cloud platform for hosting and deploying web applications.
- [[Vite]]: A build tool for modern web development.
- [[Vitest]]: A testing framework for JavaScript/TypeScript/Web APIs.
