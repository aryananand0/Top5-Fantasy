# Top5 Fantasy — Design System

This document is the reference for the visual language and component system. Read it before building any new screen.

---

## Philosophy

**Sports notebook, not sports app.**

The visual metaphor is a well-loved football notebook — cream paper, marker pen annotations, sticker-like position labels, bold handwritten scores. Every element should feel like it was placed deliberately, not generated.

The interface should feel **fun to use** without being childish. **Competitive and social** without being aggressive. **Fast and clear** on a phone screen.

### The one rule to remember

> If it looks like it could be on a betting platform, undo it.

No neon. No dark backgrounds. No aggressive urgency. No gradients that glow.

---

## Color System

### Surfaces

| Token | Hex | Use |
|---|---|---|
| `paper` | `#F7F4EE` | Main page background |
| `paper-dark` | `#EDE9DF` | Secondary surfaces, tab bars, pressed states |
| `paper-darker` | `#E2DDD5` | Tertiary surfaces, deep hover |

The background has a subtle 22px dot grid overlay (set in `globals.css`) that adds paper texture at 5% opacity — barely visible, adds depth.

### Ink

| Token | Hex | Use |
|---|---|---|
| `ink` | `#1C1917` | All borders, primary text, button fills |
| `ink-muted` | `#78716C` | Secondary text, labels, empty state copy |
| `ink-faint` | `#C4BDB3` | Dividers, placeholder text, subtle borders |

All ink tones are **warm** (stone/brown cast), not cold gray. This keeps the palette feeling like paper rather than a screen.

### Marker Accents

Used sparingly — for position tags, league labels, stat highlights, and CTAs only.

| Token | Hex | Semantic meaning |
|---|---|---|
| `marker-green` | `#2DB87A` | Goals, positive scores, success |
| `marker-blue` | `#3B82F6` | Assists, info, links |
| `marker-red` | `#DC4040` | Yellow/red cards, negative scores, danger |
| `marker-yellow` | `#F5C228` | Captain, highlights, gold |
| `marker-purple` | `#8B5CF6` | League labels, premium/special |
| `marker-orange` | `#F07530` | Price, transfer cost, value |

### Tints

Light background fills paired with their marker color for badges, tinted cards, and tinted buttons:

`tint-green`, `tint-blue`, `tint-red`, `tint-yellow`, `tint-purple`, `tint-orange`

---

## Typography

Two fonts loaded via `next/font/google` (zero layout shift, no network request at runtime):

| Font | Weight | Use |
|---|---|---|
| **Syne** | 700, 800 | Headings, display numbers, scores, rankings |
| **Nunito** | 400, 500, 600, 700, 800 | Body text, labels, buttons, inputs |

### Classes to use

- `font-display` → Syne (headings, stat numbers)
- `font-sans` → Nunito (default body — set on `<body>`)
- `num` utility → display font + `font-weight: 800` + tabular numerals + tight tracking
- `label-text` utility → uppercase, wide tracking, small size — for metadata labels

### Hierarchy examples

```
font-display font-extrabold text-5xl   → Score/rank hero number
font-display font-bold text-2xl        → Player name heading
font-display font-semibold text-lg     → Section heading
font-sans text-base                    → Body paragraph
font-sans text-sm text-ink-muted       → Secondary info
label-text text-ink-muted              → "TOTAL POINTS", "GW28"
```

### Golden rule for numbers

Any number that matters (points, rank, price, minutes) gets:
- `num` class — display font, bold, tabular
- Appropriately sized (don't be timid with big scores)

---

## Shadow System

The signature of the design system: **zero-blur offset shadows**. No glow. No soft diffusion. Just a clean block shadow that looks like a rubber stamp.

| Class | Value | Use |
|---|---|---|
| `shadow-sketch-sm` | `2px 2px 0 #1C1917` | Small badges, tight contexts |
| `shadow-sketch` | `3px 3px 0 #1C1917` | Default card, default button |
| `shadow-sketch-md` | `4px 4px 0 #1C1917` | Elevated card, hover state |
| `shadow-sketch-lg` | `6px 6px 0 #1C1917` | Hero elements, modals |

### The press animation

Every interactive element with a sketch shadow should have this hover/active pattern:

```
hover:-translate-x-px hover:-translate-y-px hover:shadow-sketch-md
active:translate-x-px  active:translate-y-px  active:shadow-none
```

On hover, it lifts slightly (shadow grows). On click, it stamps down (shadow disappears, card shifts). This is the most physically satisfying interaction in the system — don't skip it.

---

## Border System

All borders use `border-2` (2px) as the default. Increase to `border-3` (3px) only for emphasis elements. Cards are `border-2 border-ink`.

Never use `border` (1px) — it's too thin to read on the cream background and loses the sketch feel.

---

## Components

### Button

```tsx
<Button variant="primary">Save Squad</Button>
<Button variant="secondary">Make Transfer</Button>
<Button variant="ghost">Cancel</Button>
<Button variant="tinted" color="green">Join League</Button>
<Button variant="destructive">Remove Player</Button>
```

- Minimum touch target: 44px height (enforced by `min-h-[44px]` on size `md`)
- Press effect is built in — don't add external hover/active styles
- `fullWidth` for mobile CTAs at the bottom of the screen

### Card

```tsx
<Card variant="default">…</Card>    // outlined + shadow
<Card variant="elevated">…</Card>  // larger shadow, for hero cards
<Card variant="flat">…</Card>      // outline only, no shadow
<Card variant="tinted" color="yellow">…</Card>  // colored fill
```

- Use `as="article"` or `as="li"` for semantic correctness in lists
- Cards never need an `onClick` — if you need a clickable card, wrap it in a Next.js `<Link>`

### Badge vs Pill

- **Badge**: position labels (GK/DEF/MID/FWD), status tags, key attributes — rectangular, uppercase, thick border
- **Pill**: league names, filter chips, hashtag-style tags — rounded-full, softer

```tsx
<PositionBadge position="FWD" />          // GK/DEF/MID/FWD — auto-colors
<Badge color="purple" variant="tinted">Premier League</Badge>
<Pill color="green">Clean Sheet</Pill>
```

### StatBox

The most important component for the dashboard and scoring screens. The value is always huge. The label is always small and uppercase.

```tsx
<StatBox value="247" label="Total Points" color="green" />
<StatBox value="#15" label="Global Rank"  color="purple" />
<StatBox value="£4.2M" label="In the Bank" color="blue" />
```

- Color applies to the value text, not the box border
- Yellow value → use `color="ink"` instead (yellow text is illegible)

### Tabs

Controlled component — parent manages active state.

```tsx
const [active, setActive] = useState('squad')
<Tabs tabs={tabs} activeTab={active} onChange={setActive} />
```

Tabs have an optional `count` prop for showing a number badge (e.g. transfer slots remaining).

### Input / SearchInput

All inputs are 44px min-height for touch usability. Label, error, and hint are handled by the component.

```tsx
<Input label="League Name" placeholder="e.g. Office Rivals" hint="Max 30 chars" />
<Input label="Email" error="Email already in use" />
<SearchInput placeholder="Search players…" />
```

### PageShell

Wrap every page in PageShell. It handles centering, padding, and bottom clearance for the future mobile nav bar.

```tsx
<PageShell maxWidth="lg">
  <SectionHeader title="My Squad" />
  …
</PageShell>
```

---

## Patterns to Repeat Across Screens

### Player card pattern
```
[PositionBadge]  [Price £X.XM]
[Player Name  ]
[Club · League]
──────────────
[GW label]  [Points num]
```

### Stats row pattern
```
<div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
  <StatBox value="247" label="Points" color="green" />
  <StatBox value="#15" label="Rank" color="purple" />
  …
</div>
```

### Section pattern
```
<SectionHeader title="…" subtitle="…" action={<Button size="sm">…</Button>} />
<Divider style="wavy" spacing="md" />
{/* content */}
```

---

## What to Avoid

| Don't | Do instead |
|---|---|
| Blurry/soft drop shadows | `shadow-sketch` offset shadows |
| Gradients as backgrounds | Flat `bg-paper` + texture from globals.css |
| `border` (1px) | `border-2` minimum |
| `gray-*` Tailwind colors | `ink`, `ink-muted`, `ink-faint` |
| `font-bold` on headings without `font-display` | Always pair heading size with `font-display` |
| `bg-white` | `bg-paper` |
| Dense layouts with no whitespace | Generous `gap-*` and `py-*` |
| Color as decoration | Color only where it communicates meaning |
| Emoji-only icons | Inline SVG for functional icons; emoji only for decorative EmptyState icons |

---

## Adding a New Screen

1. Wrap in `<PageShell>`
2. Use `<SectionHeader>` for each content section
3. Player/entity lists → use `<Card>` grid with `grid-cols-1 sm:grid-cols-2` minimum
4. Numbers that matter → `<StatBox>` or `num` class
5. Filtering/navigation → `<Tabs>` and `<Pill>` chips
6. Empty cases → `<EmptyState>` with a contextual message and CTA
7. Separate sections → `<Divider style="wavy" />`
8. Mobile first: write Tailwind base classes for 390px, add `md:` overrides for desktop
