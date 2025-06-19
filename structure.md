// front/FRONTEND_STRUCTURE.md
/*
E-LEARNING SYSTEM FRONTEND ARCHITECTURE

├── src/
│   ├── lib/
│   │   ├── apis/          # API endpoints and fetch wrappers
│   │   │   ├── auth.js
│   │   │   ├── courses.js
│   │   │   ├── users.js
│   │   │   ├── core.js
│   │   │   └── index.js
│   │   │
│   │   ├── services/      # Business logic and data processing
│   │   │   ├── auth.service.js
│   │   │   ├── course.service.js
│   │   │   ├── notification.service.js
│   │   │   └── analytics.service.js
│   │   │
│   │   ├── stores/        # Svelte stores for state management
│   │   │   ├── auth.store.js
│   │   │   ├── user.store.js
│   │   │   ├── course.store.js
│   │   │   ├── ui.store.js
│   │   │   └── notification.store.js
│   │   │
│   │   ├── utils/         # Helper functions and utilities
│   │   │   ├── validators.js
│   │   │   ├── formatters.js
│   │   │   ├── constants.js
│   │   │   └── helpers.js
│   │   │
│   │   └── i18n/          # Internationalization
│   │       ├── index.js
│   │       ├── ar.js
│   │       └── en.js
│   │
│   ├── components/        # Reusable components
│   │   ├── common/        # Shared UI components
│   │   ├── auth/          # Authentication components
│   │   ├── course/        # Course-related components
│   │   ├── dashboard/     # Dashboard components
│   │   └── layout/        # Layout components
│   │
│   ├── routes/           # SvelteKit routes
│   │   ├── (app)/        # Authenticated routes
│   │   ├── (auth)/       # Auth routes (login, register)
│   │   └── (public)/     # Public routes
│   │
│   └── app.css           # Global styles
*/