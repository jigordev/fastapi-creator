# FastAPI Creator

`fastapi-creator` is a command-line interface (CLI) to easily scaffold and manage modular FastAPI projects. It automates the creation of standard folder structures, boilerplate code, and helps you keep your application organized as it scales.

## Installation

As this is a Python project, it can be installed via pip (or your favorite dependency manager like `uv`, `poetry`, etc.):

```bash
# If installing locally from the cloned repository
pip install -e .
```

After installation, the CLI will be available as `fastc`.

---

## Commands Overview

The CLI revolves around the `create` command group, which allows you to generate new projects from scratch, or add components to existing projects.

### 1. Create a New Project

Creates a complete FastAPI project structure in the specified directory, including core settings, database connection setup, security utilities, and a default `users` module.

**Usage:**
```bash
fastc create project <directory>
fastc create project ./my-app --module products
```

**Options:**
- `--module`, `-m`: Name of an additional module to be created together with the default `users` module.

**Generated Structure Example:**
```text
my-app/
├── app/
│   ├── main.py              # FastAPI application initialization
│   ├── lifespan.py          # Application startup and shutdown events
│   ├── core/                # Core components (config, DB, security, etc.)
│   ├── workers/             # Async background workers (e.g. ARQ, Celery)
│   └── modules/             # Domain modules
│       └── users/           # Default module generated automatically
│           ├── router.py
│           ├── schemas.py
│           ├── models/
│           ├── repositories/
│           └── services/
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### 2. Add a New Module

Adds a new domain module to an already existing project.

**Usage:**
```bash
# Make sure you are at the project root
fastc create module payments
fastc create module orders --dir ./my-app
```

**Options:**
- `--dir`, `-d`: Root directory of the FastAPI project (defaults to current directory).

### 3. Create a Service

Scaffolds a service class file inside the `services/` directory of the specified module. Services are meant to hold your business logic.

**Usage:**
```bash
fastc create service users/authentication
fastc create service products/inventory_manager
```

**What it generates (e.g., `users/authentication`):**
```python
# app/modules/users/services/authentication.py
class AuthenticationService:
    def __init__(self, repository):
        self.repository = repository
```

**Options:**
- `--dir`, `-d`: Root directory of the FastAPI project (defaults to current directory).

### 4. Create a Repository

Scaffolds a repository class inside the `repositories/` directory of the given module. Repositories handle data access and database sessions.

**Usage:**
```bash
fastc create repository users/user_query
```

**With standard CRUD methods:**
You can append the `--crud` flag to generate empty boilerplate methods for generic CRUD operations.

```bash
fastc create repository users/user_query --crud
```

**What it generates with `--crud`:**
```python
# app/modules/users/repositories/user_query.py
from sqlalchemy.ext.asyncio import AsyncSession


class UserQueryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, id: str):
        ...

    async def find_all(self):
        ...

    async def create(self, data):
        ...

    async def update(self, id: str, data):
        ...

    async def delete(self, id: str):
        ...
```

**Options:**
- `--crud`: Generate standard CRUD methods (`find_by_id`, `find_all`, `create`, `update`, `delete`).
- `--dir`, `-d`: Root directory of the FastAPI project (defaults to current directory).

---

## Getting Started with the Generated Project

Once you generate a new project using `fastc create project my-app`, go into the directory and run it:

```bash
cd my-app
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` to see your FastAPI Swagger interface up and running!
