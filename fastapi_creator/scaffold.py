from pathlib import Path
from rich.console import Console
from rich.tree import Tree
from rich import print as rprint

console = Console()


# ---------------------------------------------------------------------------
# Content of generated files
# ---------------------------------------------------------------------------

TEMPLATES: dict[str, str] = {
    # ── app/ ──────────────────────────────────────────────────────────────
    "app/__init__.py": "",

    "app/main.py": '''\
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.lifespan import lifespan
from app.core.config import settings
from app.core.middleware import register_middlewares
from app.core.exceptions import register_exception_handlers
from app.modules.users.router import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    register_middlewares(app)
    register_exception_handlers(app)

    app.include_router(users_router, prefix="/users", tags=["Users"])

    return app


app = create_app()
''',

    "app/lifespan.py": '''\
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import init_db
from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db()
    yield
    logger.info("Shutting down application...")
''',

    # ── app/core/ ─────────────────────────────────────────────────────────
    "app/core/__init__.py": "",

    "app/core/config.py": '''\
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "FastAPI App"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
''',

    "app/core/logging.py": '''\
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    return logger
''',

    "app/core/exceptions.py": '''\
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )
''',

    "app/core/security.py": '''\
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
''',

    "app/core/database.py": '''\
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
''',

    "app/core/redis.py": '''\
import redis.asyncio as aioredis
from app.core.config import settings

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client
''',

    "app/core/cache.py": '''\
import json
from typing import Any
from app.core.redis import get_redis


async def cache_get(key: str) -> Any | None:
    redis = await get_redis()
    value = await redis.get(key)
    return json.loads(value) if value else None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    redis = await get_redis()
    await redis.set(key, json.dumps(value), ex=ttl)


async def cache_delete(key: str) -> None:
    redis = await get_redis()
    await redis.delete(key)
''',

    "app/core/workers.py": '''\
# Configure Celery or ARQ workers here.
# Example using ARQ:
#
# from arq import create_pool
# from arq.connections import RedisSettings
# from app.core.config import settings
#
# async def get_arq_pool():
#     return await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
''',

    "app/core/middleware.py": '''\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
''',

    "app/core/dependencies.py": '''\
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
''',

    "app/core/utils/__init__.py": "",

    # ── app/modules/ ──────────────────────────────────────────────────────
    "app/modules/__init__.py": "",

    # ── app/workers/ ──────────────────────────────────────────────────────
    "app/workers/__init__.py": "",

    "app/workers/worker.py": '''\
# Worker entry point (e.g., ARQ, Celery).
#
# ARQ example:
# class WorkerSettings:
#     functions = [my_task]
#     redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
''',
}

MODULE_TEMPLATES: dict[str, str] = {
    "__init__.py": "",

    "router.py": '''\
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_{module}():
    return []
''',

    "dependencies.py": '''\
from typing import Annotated
from fastapi import Depends
''',

    "schemas.py": '''\
from pydantic import BaseModel


class {Module}Base(BaseModel):
    pass


class {Module}Create({Module}Base):
    pass


class {Module}Response({Module}Base):
    id: int

    model_config = {{"from_attributes": True}}
''',

    "types.py": '''\
from enum import StrEnum
''',

    "models/__init__.py": '''\
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class {Module}(Base):
    __tablename__ = "{module}s"

    id: Mapped[int] = mapped_column(primary_key=True)
''',

    "repositories/__init__.py": '''\
from sqlalchemy.ext.asyncio import AsyncSession


class {Module}Repository:
    def __init__(self, session: AsyncSession):
        self.session = session
''',

    "services/__init__.py": '''\
from {module_path}.repositories import {Module}Repository


class {Module}Service:
    def __init__(self, repository: {Module}Repository):
        self.repository = repository
''',

    "jobs/__init__.py": "",

    "events/__init__.py": "",
}

SERVICE_TEMPLATE = '''\
class {ServiceClass}:
    def __init__(self, repository):
        self.repository = repository
'''

REPOSITORY_TEMPLATE = '''\
from sqlalchemy.ext.asyncio import AsyncSession


class {RepositoryClass}:
    def __init__(self, session: AsyncSession):
        self.session = session
'''

REPOSITORY_CRUD_TEMPLATE = '''\
from sqlalchemy.ext.asyncio import AsyncSession


class {RepositoryClass}:
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
'''

REQUIREMENTS = """\
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
aiosqlite
redis>=5.0.0
python-jose[cryptography]
passlib[bcrypt]
"""

ENV_EXAMPLE = """\
APP_NAME=FastAPI App
APP_VERSION=0.1.0
DEBUG=True

DATABASE_URL=sqlite+aiosqlite:///./dev.db
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""

GITIGNORE = """\
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
.env
.env.*
!.env.example
*.db
*.sqlite3
.pytest_cache/
.mypy_cache/
.ruff_cache/
"""

README = """\
# FastAPI Project

Project generated with [fastapi-creator](https://github.com/jigordev/fastapi-creator).

## Structure

```
app/
├── core/          # Configuration, database, security, middlewares
├── modules/       # Domain modules (users, products, etc.)
└── workers/       # Async workers (ARQ, Celery)
```

## How to run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_pascal_case(name: str) -> str:
    """Converts snake_case or kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in name.replace("-", "_").split("_"))


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    console.print(f"  [green]✔[/green] {path}")


def _build_module(base: Path, module_name: str) -> None:
    """Creates the structure of a module inside app/modules/<module_name>/."""
    Module = module_name.capitalize()
    module_path_import = f"app.modules.{module_name}"

    for relative, template in MODULE_TEMPLATES.items():
        content = template.format(
            module=module_name,
            Module=Module,
            module_path=module_path_import,
        )
        _write_file(base / relative, content)


def create_project(directory: str, extra_module: str | None = None) -> None:
    root = Path(directory)

    if root.exists() and any(root.iterdir()):
        raise FileExistsError(
            f"The directory '{directory}' already exists and is not empty."
        )

    console.print("\n[bold]Creating project files:[/bold]")

    # Fixed files
    for relative, content in TEMPLATES.items():
        _write_file(root / relative, content)

    # Default module: users
    console.print("\n[bold]Creating module [cyan]users[/cyan]:[/bold]")
    _build_module(root / "app" / "modules" / "users", "users")

    # Optional extra module
    if extra_module:
        console.print(f"\n[bold]Creating module [cyan]{extra_module}[/cyan]:[/bold]")
        _build_module(root / "app" / "modules" / extra_module, extra_module)

    # Root files
    console.print("\n[bold]Creating configuration files:[/bold]")
    _write_file(root / "requirements.txt", REQUIREMENTS)
    _write_file(root / ".env.example", ENV_EXAMPLE)
    _write_file(root / ".gitignore", GITIGNORE)
    _write_file(root / "README.md", README)


def add_module_to_project(directory: str, module_name: str) -> None:
    root = Path(directory)
    modules_dir = root / "app" / "modules"

    if not modules_dir.exists():
        raise FileNotFoundError(
            f"Could not find 'app/modules/' in '{directory}'. "
            "Make sure you are at the root of a fastapi-creator project."
        )

    module_dir = modules_dir / module_name

    if module_dir.exists():
        raise FileExistsError(f"The module '{module_name}' already exists.")

    console.print(f"\n[bold]Creating module [cyan]{module_name}[/cyan]:[/bold]")
    _build_module(module_dir, module_name)


def create_service(directory: str, target: str) -> Path:
    """
    Creates a service file at app/modules/<module>/services/<name>.py.

    `target` must be in the format "<module>/<service_name>".
    Raises FileExistsError if the service already exists.
    """
    if "/" not in target:
        raise ValueError(
            f"Invalid format '{target}'. Use: <module>/<service_name>  "
            "(e.g.: users/authentication)"
        )

    module_name, service_name = target.split("/", 1)

    root = Path(directory)
    services_dir = root / "app" / "modules" / module_name / "services"

    if not services_dir.exists():
        raise FileNotFoundError(
            f"Services directory for module '{module_name}' not found: "
            f"'{services_dir}'. "
            "Make sure the module exists and you are at the project root."
        )

    service_file = services_dir / f"{service_name}.py"

    if service_file.exists():
        raise FileExistsError(
            f"The service '{service_name}' already exists in '{services_dir}'."
        )

    service_class = _to_pascal_case(service_name) + "Service"
    content = SERVICE_TEMPLATE.format(ServiceClass=service_class)

    _write_file(service_file, content)
    return service_file


def create_repository(directory: str, target: str, crud: bool = False) -> Path:
    """
    Creates a repository file at app/modules/<module>/repositories/<name>.py.

    `target` must be in the format "<module>/<repository_name>".
    If `crud=True`, generates standard CRUD methods (find_by_id, find_all, create, update, delete).
    Raises FileExistsError if the repository already exists.
    """
    if "/" not in target:
        raise ValueError(
            f"Invalid format '{target}'. Use: <module>/<repository_name>  "
            "(e.g.: users/user_query)"
        )

    module_name, repository_name = target.split("/", 1)

    root = Path(directory)
    repositories_dir = root / "app" / "modules" / module_name / "repositories"

    if not repositories_dir.exists():
        raise FileNotFoundError(
            f"Repositories directory for module '{module_name}' not found: "
            f"'{repositories_dir}'. "
            "Make sure the module exists and you are at the project root."
        )

    repository_file = repositories_dir / f"{repository_name}.py"

    if repository_file.exists():
        raise FileExistsError(
            f"The repository '{repository_name}' already exists in '{repositories_dir}'."
        )

    repository_class = _to_pascal_case(repository_name) + "Repository"
    template = REPOSITORY_CRUD_TEMPLATE if crud else REPOSITORY_TEMPLATE
    content = template.format(RepositoryClass=repository_class)

    _write_file(repository_file, content)
    return repository_file
