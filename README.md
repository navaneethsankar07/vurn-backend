# Vurn Backend

Backend service for **Vurn**, an AI-native engineering workspace for modern software teams.

Built with **Django** and **Django REST Framework**, following a modular monolith architecture with a layered internal structure.

## Current Status

Authentication and the initial profile module are implemented. Profile management and organization management are currently in development.

## Technology Stack

| Category | Technology |
| --- | --- |
| Language | Python |
| Framework | Django |
| API | Django REST Framework |
| Database | PostgreSQL |
| Cache | Redis |
| Authentication | JWT |
| OAuth | Google OAuth |
| Email | SMTP |
| CORS | django-cors-headers |

## Architecture

### High-Level Architecture

Vurn follows a **Modular Monolith** architecture.

```text
Client
  |
  v
Django Backend
  |
  +-- Accounts Module
  |
  +-- Profiles Module
  |
  +-- Organization Module
  |
  +-- Other Domain Modules
  |
  v
PostgreSQL
```

Each Django application represents a distinct business domain while remaining part of the same backend application.

### Low-Level Architecture

Within each module, the backend follows a **Layered Architecture** with a service layer.

```text
Request
  |
  v
APIView
  |
  v
Serializer / Validator
  |
  v
Service Layer
  |
  v
Django ORM
  |
  v
PostgreSQL / Redis
```

- **Views** handle HTTP requests and responses.
- **Serializers and validators** handle input validation and data representation.
- **Services** contain business and application logic.
- **ORM** handles database interaction.
- **PostgreSQL** stores persistent application data.
- **Redis** handles temporary and cache-based data.

## API

All APIs are versioned under:

```text
/api/v1/
```

## Project Structure

```text
backend/
├── apps/
│   ├── accounts/
│   └── profiles/
├── config/
│   └── settings/
│       ├── base.py
│       ├── development.py
│       ├── production.py
│       └── test.py
├── manage.py
├── requirements.txt
└── README.md
```

## Configuration

Environment-specific Django settings are separated into:

```text
config/settings/
├── base.py
├── development.py
├── production.py
└── test.py
```
Environment-specific values are provided through environment variables.

### Project Context

Vurn is an AI-native engineering workspace designed to bring the essential workflows of modern software development teams into a single platform. It provides a centralized environment for managing teams, projects, planning, issues, documentation, and engineering workflows.

The backend provides the core application infrastructure and business logic that powers the platform. It is designed around modular domain boundaries, allowing features to be developed independently while remaining within a unified application.

The system is being developed incrementally, with authentication and identity forming the foundation for user profiles, organizations, projects, and the broader engineering workspace.

---

*Currently under active development.*