✅ Refactor Plan: Fix SvelteKit Frontend (Preserve Django Backend)
1. Understand the Project Structure
Carefully review the current codebase.

Identify integration points between SvelteKit (v2.x / Svelte 5) and Django (DRF v3.16).

Determine where the frontend needs adjustments without touching the backend logic or structure.

2. Create and Maintain todo.md
Write a checklist in todo.md with frontend-related TODO items only.

Keep backend items only if explicitly requested.

The checklist must allow tracking progress as tasks get completed.

3. Approval Before Execution
Before doing any actual development:

Share the todo.md plan.

Wait for your review and approval.

After approval, start working step-by-step.

4. Work Process
If both frontend (SvelteKit) and backend (Django) code are available:

Start by understanding and mapping the backend API responses.

Do not change the backend code.

Refactor and build the frontend based on the backend's structure, fields, and endpoints.

5. Communication Style
Every change must come with a simple, high-level summary.

No deep technical explanations unless specifically requested.

Follow the principle of clarity > cleverness.

6. Frontend Guidelines (SvelteKit + TailwindCSS v4)
Use clean, responsive, minimal design.

Avoid unnecessary complexity — use the simplest SvelteKit code possible.

Stick to modern UI/UX design standards.

Single-page layout if the app is small or a dashboard.

TailwindCSS v4 should be used efficiently and semantically.

7. Final Review Section in todo.md
After completing tasks, add a "✅ Review" section:

Summarize what was changed.

Mention if the frontend used SvelteKit 2.x (Svelte 5) and Tailwind v4.

Confirm that the backend remained untouched (Django 5.2 + DRF v3.16).