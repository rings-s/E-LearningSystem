# 🎨 Premium UI/UX Redesign — Frontend Only

**Stack:** SvelteKit 3.x (Svelte 5) + TailwindCSS v4 · **Backend:** Django 5.2 + DRF v3.16 (untouched)
**Goal:** A cohesive, premium, accessible design across every page, without changing any API calls or backend code.

---

## 🔍 What I found (audit)

1. **Colors are scattered.** Brand tokens sit in plain `:root` variables, `tailwind.config.js` is never loaded (Tailwind v4 ignores it), and pages mix `blue`, `indigo`, `purple` and `primary` for the same purpose.
2. **Dark mode toggle doesn't work.** The store adds a `.dark` class, but Tailwind v4's `dark:` variant follows the OS setting unless told otherwise. `@theme .dark { … }` is also invalid syntax.
3. **Inconsistent visual language.** Button uses `blue-600`, the header uses lavender→mocha gradients, and pages mix `gray`, `blue`, and `indigo`. The brand name is spelled **244SCHOOL**, **249SCHOOL** and **249Sudan** in different places (now unified as **Ilmora**).
4. **Fonts are referenced but never loaded.** That covers Inter, Cairo, and Readex Pro.
5. **Overdone effects.** There are gradients everywhere, plus `hover:scale-105`, floating/glow animations, and glassmorphism. The result looks noisy rather than premium.
6. **Gaps.** `certificates` and `courses/[uuid]/analytics` are empty pages. 11 components are never used (Navbar, Sidebar, MobileMenu, AuthCard, AuthContainer, etc.).
7. **RTL.** The app supports Arabic, but many components use `left/right`, `ml/mr`, and `space-x` instead of logical properties (`start/end`, `ms/me`, `gap`).

---

## 🎯 Proposed design direction (please confirm or adjust)

- **Palette:** One confident brand color (deep **indigo/violet**), neutral **zinc** grays, and semantic success/warning/danger colors. No rainbow gradients, and at most one subtle brand gradient (hero and logo only).
- **Typography:** **Inter** for Latin text and **IBM Plex Sans Arabic** (or Cairo) for Arabic, on a clear type scale with tighter tracking for headings.
- **Surfaces:** White cards with a 1px soft border, subtle shadows, and `rounded-2xl`. Dark mode uses true neutral surfaces (zinc-950/900).
- **Layout:** One **app shell** for signed-in users: a slim collapsible **sidebar** on desktop, a drawer on mobile, and a top bar for search, notifications, and the user menu. Public and auth pages get a clean top header.
- **Motion:** Short, purposeful transitions (150–200ms) with no bouncing or scaling. `prefers-reduced-motion` is respected.
- **Accessibility:** WCAG AA contrast, visible focus rings, 44px touch targets, aria labels, and keyboard-friendly menus and modals.

---

## ✅ TODO Checklist

### Phase 1: Design foundation ✅
- [x] Rewrite `app.css` with a proper Tailwind v4 `@theme` (brand, neutral, and semantic tokens; fonts; radii; shadows)
- [x] Add `@custom-variant dark` so the theme toggle works, and remove the invalid `@theme .dark`
- [x] Load fonts in `app.html` (Inter + Arabic font), and set `theme-color` and base body styles
- [x] Delete the unused `tailwind.config.js` and the leftover "2025 trend" utilities (glass, glow, float)
- [x] Rename the project to **Ilmora** (إلمورا), from Arabic *ʿilm* (knowledge) + *-ora* (light). It replaces 244SCHOOL, 249SCHOOL and 249Sudan across the frontend
- [x] Design a new Ilmora logo mark (replaces the "244" badge)
- [x] Map every `blue`/`indigo` class to `primary` and `purple` to `secondary`, and turn all grays into one cool zinc scale (25 files, class names only)
- [x] Theme defaults to the OS preference on first visit, with no flash on load

### Phase 1.5: Stack upgrade to SvelteKit 3 ✅
_Now on: **SvelteKit 3.1 · Svelte 5.57 · Tailwind 4.3 · Vite 8**_
- [x] Bump dependencies: `@sveltejs/kit` 3, `svelte` 5.57, `vite` 8, `@sveltejs/vite-plugin-svelte` 7, `@sveltejs/adapter-cloudflare` 8 (+ `wrangler`), `typescript` 6, `tailwindcss`/`@tailwindcss/vite` 4.3
- [x] Ran the official codemod `npx sv migrate sveltekit-3` (it also ran Prettier on every file)
- [x] Config: `svelte.config.js` folded into `vite.config.js`; `eslint.config.js` now uses `@sveltejs/load-config`
- [x] `jsconfig.json` extends `$app/tsconfig`
- [x] Imports: `$lib` → `#lib`, `$app/environment` → `$app/env`, `$app/stores` → `$app/state`
- [x] `replaceState(...)` → `goto(url, { shallow: true, replace: true })` (3 files)
- [x] `service-worker.js` uses `$app/env` + `$app/manifest`
- [x] Svelte 5 cleanup: `NotesSection`, `UnifiedDashboard`, `StatsCard` converted to runes. No legacy syntax left
- [x] Fixed broken links that SvelteKit 3 now rejects: `/auth/login` → `/login` (7 places); dashboard links to unbuilt `/schedule` and `/admin/*` pages use a plain page load
- [x] Fixed wrong prop names so these work again: Modal `bind:show`/`bind:isOpen` → `open` + `onClose` (manage page, ShareModal), Tabs `bind:selectedTab` → `bind:activeTab`
- [x] Rebuilt `NotesSection` to match the props the learn page passes (the notes tab used to crash)
- [x] Fixed an attribute quote that Prettier broke in `forgot-password`
- [x] Verify: `npm run build` ✅ · dev smoke test of `/`, `/login`, `/register`, `/courses`, `/dashboard`, `/my-courses`, `/teacher/courses` ✅
- [ ] Follow-ups: ~1500 `npm run check` errors already existed (strict type-checking on untyped JS); `npm run lint` fails because `front/.gitignore` is missing (also already the case)

### Phase 2: Core UI components (`lib/components/common`) ✅
- [x] `Button`: primary / secondary / outline / ghost / danger / success / warning, sizes, loading, focus ring
- [x] `Card`, `Badge`, `Input`, `Select`, `Tabs`, `Modal`, `Steps`: one consistent style with RTL-safe spacing
- [x] `NotificationToast` and `NotificationBell`: refined look, accessible markup, full-width on phones
- [x] New shared pieces: `PageHeader`, `EmptyState`, `Skeleton`, `CourseCover`
- [x] Fixed: toasts never showed (they read the wrong store); Modal and Tabs were passed the wrong prop names; `Steps` crashed the create-course wizard; Badge/Button variants that pages used didn't exist

### Phase 3: Layout and shell ✅
- [x] Signed-in pages use `AppShell`: fixed sidebar on desktop, slide-in drawer on phones, sticky top bar
- [x] Role-aware `Sidebar` (Learn / Teach / Community); new public `Header`; shared `PreferenceToggles` (theme + language)
- [x] Learn pages run in full-screen "focus mode" without global chrome
- [x] Simpler loading screen; removed unused `Navbar` and `MobileMenu`

### Phase 4: Public and auth pages ✅
- [x] Landing page: hero with product preview, features, how it works, CTA band, footer
- [x] Shared split-screen auth layout; login, register, forgot/reset password and verify email rebuilt on it
- [x] Removed unused auth components (`AuthCard`, `AuthContainer`, `AuthButton`, `FormInput`, `StepIndicator`, `CodeInput`)

### Phase 5: Student experience ✅
- [x] Dashboard: KPI cards, continue-learning list, quick actions, honest empty states instead of made-up chart data
- [x] Course catalog: search + filter bar, redesigned `CourseCard`, simple pagination
- [x] Course detail: hero, tabs, sticky enroll card (shown first on phones)
- [x] My Courses: stats, search, sort, pill filters, grid/list views with progress
- [x] Learn pages: lessons load again, fits phones (no sideways scroll), cleaner top bar and progress bar
- [x] Profile fixed (it crashed with an infinite update loop); Forum and Notes inherit the new components
- [x] Certificates page built from `/api/certificates/`
- [ ] Course preview, Notes and Forum pages: only shared-component/responsive fixes, no bespoke redesign yet

### Phase 6: Teacher experience (partly done)
- [x] Teacher courses list: real cover images, removed the on-screen debug line
- [x] Create course / create lesson: new stepper, inputs and buttons via shared components
- [x] Analytics: brand chart colors, charts redraw on data/theme change, tabs scroll on phones
- [ ] Course manage page and Students table: only shared-component fixes, no bespoke redesign yet

### Phase 7: Quality pass ✅
- [x] Dark mode checked on dashboard, catalog, course detail, auth, landing
- [x] RTL (Arabic) checked on dashboard, catalog, login; added 53 missing translation keys
- [x] No horizontal scroll at 390px on any page (checked with a headless browser)
- [x] `npm run build` passes; `npm run check` errors went from 1514 → 1239 (the rest is old JS type noise)
- [x] `back/` has no changes

---

## ✅ Review
**Stack:** SvelteKit 3.1 · Svelte 5.57 (runes everywhere, no legacy syntax left) · Tailwind CSS 4.3 · Vite 8.
**Backend:** Django 5.2 + DRF 3.16 untouched (`git status back/` is empty).

**What changed**
- New design system on the existing tokens: soft rings instead of borders, `rounded-2xl` surfaces, one brand color, calm motion.
- New layout: sidebar app shell for signed-in users, clean public header, split-screen auth, focus-mode learning.
- Rebuilt landing, auth, dashboard, catalog, course detail, My Courses and Certificates pages.
- Removed noisy effects (hover scaling, floating/bouncing animations) and v3-only Tailwind classes.

**Real bugs fixed along the way**
- 40 `$derived(() => …)` values were functions instead of values: the learn page never showed lessons, teacher stats/pagination and publish buttons were wrong.
- Dashboard crashed for students with enrollments (sorted reactive state in place) and showed untitled courses.
- Profile page crashed on load (infinite effect loop).
- Toasts never appeared; several modals could never open; the create-course wizard crashed.

**Translations (English + Arabic)**
- Every page and shared component now uses `$t(...)`: landing, auth, dashboard, catalog, course detail/preview, My Courses, learn, notes, certificates, profile, forum and all teacher pages.
- 1,012 keys in use, none missing; `en.js` and `ar.js` now hold the same set of keys (they had drifted apart before).
- Dates use the selected language; course text from the backend uses `dir="auto"` so English titles read correctly inside Arabic pages.
- Option lists, tabs and greetings are reactive, so switching language updates them immediately.
- `/courses/create` (an unlinked duplicate) now redirects to `/teacher/courses/create`; unused `AnalyticsDashboard` removed.
- Not translated: brand names, example URLs, and the printable PDF analytics report.

**Full-app check after the package updates (2026-10-21)**
- Backend code is unchanged; only `back/requirements.txt` lost its version pins (DRF 3.18, django-redis 7, redis 8, Pillow 13 now installed). `manage.py check` and migration checks are clean.
- API smoke test on an in-memory DB: register, verify, login, profile, courses, publish, enroll, analytics, forum, certificates and password reset all pass.
- Fixed (frontend): registration failed whenever the optional date of birth was skipped (`""` is rejected by the API in DRF 3.16 and 3.18 alike); profile save had the same issue. Registration errors are now shown on the page.
- Fixed (frontend) course creation: the form sent the category UUID but the API expects its numeric id (the 400 in the log). Same for the manage page and the lesson form's module.
- Fixed: catalog category filter sent a UUID; the API filters by category slug.
- Fixed: slugs are now always sent (courses and lessons require one; Arabic titles get a fallback slug).
- Fixed: teachers were redirected away from their own manage/analytics/lesson pages (compared `instructor.uuid`, which the API doesn't return).
- Added: "Add module" dialog on the manage page and per-module "Add lesson" buttons (the old buttons linked to pages that don't exist).
- Email failure is network-level: Gmail drops the SMTP login from this device even for fake accounts.

**Still open**
- Backend security: any signed-in user can create modules in someone else's course (`IsCourseInstructor` is never checked on create). Backend change, not made.
- Bespoke redesign of course preview, notes, forum, course manage and students pages.
- `npm run lint` fails because `front/.gitignore` is missing.
