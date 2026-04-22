# Top5 Fantasy — Shared Package

This directory is reserved for code shared between the web app and any future clients (e.g., a React Native mobile app).

**In the MVP, this directory may stay empty or contain only constants.** Do not add code here prematurely.

---

## What belongs here (when the time comes)

- TypeScript type definitions shared between the frontend and a future mobile app
- Constants shared across clients: scoring rules, position names, max squad size, etc.
- Utility functions with zero platform dependencies (pure logic, no DOM, no Node)

## What does NOT belong here

- React components (those are web-specific, live in `apps/web/`)
- Backend logic (that lives in `apps/api/`)
- Anything that imports from `next`, `react-native`, or any platform-specific package
- Database models or API clients

---

## Current Status

Not yet in use. When the first shared constant or type is needed, add it here and document it in this README.
