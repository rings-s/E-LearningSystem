# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack e-learning platform built for Sudanese people affected by war, offering free accessible education. The architecture consists of:

- **Backend**: Django 5.2 with REST API, real-time WebSocket support, and background tasks
- **Frontend**: SvelteKit with Tailwind CSS v4, supporting Arabic/English languages
- **Database**: SQLite (development), PostgreSQL (production)
- **Cache/Broker**: Redis for caching and Celery task queue
- **Analytics**: Plotly + Pandas for learning analytics and data visualization
- **Deployment**: Cloudflare Pages (frontend), Django with WhiteNoise (backend)

## Common Development Commands

### Backend (Django)
```bash
# Navigate to backend
cd back

# Install dependencies
pip install -r requirements.txt

# Setup media directories
python create_media_dirs.py

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Testing
python manage.py test                    # All tests
python manage.py test accounts          # Specific app
python manage.py test accounts.tests.TestUserModel  # Specific test

# Database debugging
python manage.py shell                  # Django shell
python manage.py dbshell                # Database shell
python manage.py showmigrations         # Migration status

# Background tasks
celery -A back worker -l info           # Start worker
celery -A back beat -l info             # Start scheduler
celery -A back flower                   # Monitoring (if installed)

# Static files (production)
python manage.py collectstatic
```

### Frontend (SvelteKit)
```bash
# Navigate to frontend
cd front

# Install dependencies
npm install

# Development server
npm run dev

# Build and preview
npm run build
npm run preview

# Code quality
npm run lint
npm run format
npm run check                           # Type checking
npm run check:watch                     # Watch mode

# Build analysis
npm run build -- --analyze             # Bundle analysis
```

## Project Architecture

### Backend Structure
- **`accounts/`** - User authentication, roles (student/teacher/moderator/manager), profiles
- **`courses/`** - Course management, modules, lessons, quizzes, certificates, progress tracking
- **`core/`** - Notifications, analytics, WebSocket consumers, discussion forums
  - **`analytics/`** - Plotly-based data visualization and learning analytics
  - **`consumers.py`** - WebSocket consumers for real-time features

### Frontend Structure
- **`src/lib/apis/`** - API client services for backend communication
- **`src/lib/components/`** - Reusable UI components organized by feature
- **`src/lib/stores/`** - Svelte stores for state management
- **`src/lib/services/`** - Business logic services
- **`src/routes/(auth)/`** - Authentication pages (login, register, reset)
- **`src/routes/(app)/`** - Protected application pages

### Key Features
- **Authentication**: JWT-based with refresh tokens, role-based access control
- **Course System**: Hierarchical structure (Course → Module → Lesson) with progress tracking
- **Real-time**: WebSocket connections for notifications and live features
- **Analytics**: Learning analytics dashboard with Plotly visualizations
- **Internationalization**: Arabic/English support with RTL text handling
- **Certificates**: Auto-generated certificates with QR code verification
- **Media Handling**: Organized file uploads with type restrictions and processing

## Svelte 5 Specific Patterns

### Runes Usage
- **`$state()`** - Reactive state variables
- **`$derived()`** - Computed values based on state
- **`$effect()`** - Side effects and lifecycle management
- **`$bindable()`** - Two-way binding in component props

### Component Patterns
```svelte
<!-- Props with bindable -->
let { value = $bindable(), disabled = false } = $props();

<!-- Animation directives must wrap components -->
<div in:fly={{ y: 20, duration: 300 }}>
  <Card>Content</Card>
</div>

<!-- NOT directly on components -->
<!-- <Card in:fly={{ y: 20 }}>Content</Card> WRONG -->
```

### Snippets
```svelte
<!-- Define snippets for reusable content -->
{#snippet tabContent(tab)}
  <div>{tab.content}</div>
{/snippet}

<!-- Use with @render -->
{@render tabContent(activeTab)}
```

## Development Workflow

### Making Changes
1. **Backend changes**: Always run migrations after model changes
2. **Frontend changes**: Use existing component patterns from `src/lib/components/`
3. **API changes**: Update both Django views and frontend API services
4. **Database changes**: Create migrations, never edit migration files directly
5. **WebSocket changes**: Update consumers and test real-time functionality

### Testing Strategies
- **Backend**: Django test framework with factory patterns
- **Frontend**: Svelte component testing with `npm run check`
- **API**: Use Django's APIClient for endpoint testing
- **WebSocket**: Test consumers with channels testing utilities

### Code Style
- **Backend**: Follow Django conventions, use UUID primary keys
- **Frontend**: Use Tailwind CSS v4 classes, follow SvelteKit patterns
- **API**: RESTful design with consistent endpoints
- **Components**: Prefer composition over inheritance, use TypeScript-style JSDoc

## Important Technical Details

### Authentication Flow
- JWT tokens with refresh mechanism in localStorage
- Role-based permissions: student < teacher < moderator < manager
- Email verification required for new accounts
- Middleware handles token refresh automatically

### Real-time Features
- WebSocket consumers in `core/consumers.py`
- Channel layers for group messaging
- Real-time notifications via `NotificationConsumer`
- Live lesson streaming capabilities through WebRTC integration

### Analytics System
- **Plotly Integration**: Server-side chart generation with `plotly` and `pandas`
- **Data Processing**: `core/analytics/` contains chart generators and data processors
- **Visualization Types**: Progress charts, activity feeds, performance radars
- **Export Capabilities**: Static image export using `kaleido`

### File Structure & Media Handling
- **Media Organization**: `/media/courses/`, `/media/certificates/`, `/media/lessons/`
- **Upload Restrictions**: File type validation, size limits, virus scanning
- **Static Files**: WhiteNoise for production static file serving
- **Processing**: Automatic thumbnail generation for course images

### Database Schema
- **Custom User Model**: UUID primary keys, role-based permissions
- **Hierarchical Structure**: Course → Module → Lesson with foreign keys
- **Progress Tracking**: Detailed analytics with completion percentages
- **Soft Deletes**: Important data retention using `is_active` flags

### Environment Configuration
- **Development**: SQLite, Redis (optional), debug mode enabled
- **Production**: PostgreSQL, Redis required, security headers enabled
- **Environment Variables**: Load from `.env` file using `python-dotenv`

## Troubleshooting

### Common Svelte 5 Issues
- **Directive Errors**: Animation directives (in:fly, in:fade) cannot be used directly on components
- **Rune Migration**: Convert `let` to `$state()`, computed to `$derived()`
- **Snippet Syntax**: Use `{@render snippet()}` instead of slot-based patterns

### WebSocket Debugging
```bash
# Check Redis connection
redis-cli ping

# Monitor WebSocket connections
python manage.py shell
# Check active connections in Django admin or logs
```

### Django Model Issues
```bash
# Reset migrations (development only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate

# Check model relationships
python manage.py shell
# >>> from accounts.models import CustomUser
# >>> user = CustomUser.objects.first()
# >>> user.enrolled_courses.all()
```

### Media File Issues
- **Missing Files**: Check `MEDIA_ROOT` and `MEDIA_URL` settings
- **Upload Failures**: Verify directory permissions and disk space
- **Serving Issues**: Ensure WhiteNoise configuration for production

### Frontend Build Issues
- **Type Errors**: Run `npm run check` for detailed error information
- **Import Errors**: Check file paths and ensure exports are correct
- **Tailwind Issues**: Verify Tailwind v4 configuration in `tailwind.config.js`

## Production Deployment

### Backend Requirements
- PostgreSQL database with proper encoding
- Redis for caching and Celery message broker
- Environment variables for sensitive configuration
- WhiteNoise for static file serving
- Gunicorn + Nginx for production serving

### Frontend Deployment
- Cloudflare Pages adapter configured in `svelte.config.js`
- Build command: `npm run build`
- Output directory: `build/`
- Environment variables for API endpoints

### Celery Production Setup
```bash
# Worker process
celery -A back worker --loglevel=info --detach

# Scheduler process
celery -A back beat --loglevel=info --detach

# Monitoring (optional)
celery -A back flower --port=5555
```