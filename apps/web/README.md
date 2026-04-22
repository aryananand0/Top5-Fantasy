# Top5 Fantasy — Web App (Next.js)

The user-facing frontend. Built with Next.js, styled with Tailwind CSS.

---

## Stack

| Tool | Purpose |
|---|---|
| Next.js 14+ | React framework with SSR and routing |
| Tailwind CSS | Utility-first styling |
| TypeScript | Type safety across components |

---

## Setup

```bash
# From this directory (apps/web)
npm install
npm run dev
# Runs on http://localhost:3000
```

Copy `../../.env.example` → `apps/web/.env.local` and fill in `NEXT_PUBLIC_API_URL`.

---

## Dependency Strategy

### Add now (when initializing the app)

```
next
react
react-dom
typescript
@types/react
@types/node
tailwindcss
postcss
autoprefixer
```

### Add when the need arises

| Package | When |
|---|---|
| `zustand` | If component-level state becomes unwieldy |
| `swr` or `react-query` | If client-side data fetching needs caching/revalidation |
| `react-hook-form` | When forms require complex validation |
| `date-fns` | When date formatting logic becomes repetitive |
| `clsx` | If conditional classname logic gets messy |

### Do not add

- `axios` — use the native `fetch` API
- Any UI component library (MUI, Chakra, Radix) — build to the custom design system
- `redux` or `zustand` before state management is actually a problem
- Animation libraries (`framer-motion`, GSAP) — use CSS transitions only in MVP
- Icon libraries — use inline SVGs or simple doodle-style custom icons

---

## Folder Structure (to be created when building begins)

```
apps/web/
├── app/               Next.js App Router — pages and layouts
├── components/        Reusable UI components
├── lib/               API client, utility functions
├── public/            Static assets (keep small)
├── styles/            Global CSS and Tailwind config
├── types/             TypeScript type definitions
└── .env.local         Local environment variables (not committed)
```

---

## Mobile Responsiveness

Every component and page must be built mobile-first. Start with styles for a 390px viewport, then add `md:` and `lg:` overrides.

Touch targets for interactive elements must be at least 44×44px.

---

## Design System Notes

See [`docs/PROJECT_RULES.md`](../../docs/PROJECT_RULES.md) for the full visual identity guidelines.

Short version: sketch aesthetic, thick outlines, rounded cards, off-white background, sticker-style labels, no glossy gradients.

Tailwind will need custom configuration for: color palette, border-width values, border-radius scale, and typography.
