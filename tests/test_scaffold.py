"""
Testes unitários para as funções de scaffold.
Cobre: create_project, add_module_to_project, create_service, create_repository.
"""
import pytest
from pathlib import Path
from fastapi_creator.scaffold import (
    create_project,
    add_module_to_project,
    create_service,
    create_repository,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _project(tmp_path: Path) -> Path:
    """Cria um projeto de exemplo e retorna o seu Path."""
    target = tmp_path / "myapp"
    create_project(str(target))
    return target


# ============================================================================
# create_project
# ============================================================================

class TestCreateProject:
    def test_creates_root_files(self, tmp_path):
        target = tmp_path / "proj"
        create_project(str(target))

        assert (target / "requirements.txt").exists()
        assert (target / ".env.example").exists()
        assert (target / ".gitignore").exists()
        assert (target / "README.md").exists()

    def test_creates_app_structure(self, tmp_path):
        target = tmp_path / "proj"
        create_project(str(target))

        assert (target / "app" / "__init__.py").exists()
        assert (target / "app" / "main.py").exists()
        assert (target / "app" / "lifespan.py").exists()

    def test_creates_core_files(self, tmp_path):
        target = tmp_path / "proj"
        create_project(str(target))

        core = target / "app" / "core"
        for filename in [
            "__init__.py", "config.py", "logging.py", "exceptions.py",
            "security.py", "database.py", "redis.py", "cache.py",
            "workers.py", "middleware.py", "dependencies.py",
        ]:
            assert (core / filename).exists(), f"core/{filename} não foi criado"

        assert (core / "utils" / "__init__.py").exists()

    def test_creates_workers(self, tmp_path):
        target = tmp_path / "proj"
        create_project(str(target))

        workers = target / "app" / "workers"
        assert (workers / "__init__.py").exists()
        assert (workers / "worker.py").exists()

    def test_creates_default_users_module(self, tmp_path):
        target = tmp_path / "proj"
        create_project(str(target))

        users = target / "app" / "modules" / "users"
        for rel in [
            "__init__.py", "router.py", "dependencies.py",
            "schemas.py", "types.py",
        ]:
            assert (users / rel).exists(), f"users/{rel} não foi criado"

        for subdir in ["models", "repositories", "services", "jobs", "events"]:
            assert (users / subdir / "__init__.py").exists(), \
                f"users/{subdir}/__init__.py não foi criado"

    def test_creates_extra_module(self, tmp_path):
        target = tmp_path / "proj"
        create_project(str(target), extra_module="products")

        products = target / "app" / "modules" / "products"
        assert products.exists()
        assert (products / "__init__.py").exists()
        assert (products / "router.py").exists()

    def test_raises_if_directory_not_empty(self, tmp_path):
        target = tmp_path / "proj"
        target.mkdir()
        (target / "file.txt").write_text("conflict")

        with pytest.raises(FileExistsError, match="não está vazio"):
            create_project(str(target))

    def test_module_files_have_correct_class_names(self, tmp_path):
        target = tmp_path / "proj"
        create_project(str(target), extra_module="orders")

        schemas = (target / "app" / "modules" / "orders" / "schemas.py").read_text()
        assert "class OrdersBase" in schemas
        assert "class OrdersCreate" in schemas
        assert "class OrdersResponse" in schemas

    def test_router_file_has_correct_function_name(self, tmp_path):
        target = tmp_path / "proj"
        create_project(str(target))

        router = (target / "app" / "modules" / "users" / "router.py").read_text()
        assert "async def list_users" in router


# ============================================================================
# add_module_to_project
# ============================================================================

class TestAddModuleToProject:
    def test_adds_module_successfully(self, tmp_path):
        proj = _project(tmp_path)
        add_module_to_project(str(proj), "products")

        module = proj / "app" / "modules" / "products"
        assert module.exists()
        assert (module / "__init__.py").exists()
        assert (module / "router.py").exists()
        assert (module / "schemas.py").exists()

    def test_adds_all_subdirs(self, tmp_path):
        proj = _project(tmp_path)
        add_module_to_project(str(proj), "payments")

        module = proj / "app" / "modules" / "payments"
        for subdir in ["models", "repositories", "services", "jobs", "events"]:
            assert (module / subdir / "__init__.py").exists(), \
                f"payments/{subdir}/__init__.py ausente"

    def test_raises_if_modules_dir_missing(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()

        with pytest.raises(FileNotFoundError, match="app/modules/"):
            add_module_to_project(str(empty), "products")

    def test_raises_if_module_already_exists(self, tmp_path):
        proj = _project(tmp_path)

        with pytest.raises(FileExistsError, match="users"):
            add_module_to_project(str(proj), "users")


# ============================================================================
# create_service
# ============================================================================

class TestCreateService:
    def test_creates_service_file(self, tmp_path):
        proj = _project(tmp_path)
        service_file = create_service(str(proj), "users/authentication")

        assert service_file.exists()
        assert service_file.name == "authentication.py"

    def test_service_is_inside_correct_dir(self, tmp_path):
        proj = _project(tmp_path)
        service_file = create_service(str(proj), "users/token")

        expected = proj / "app" / "modules" / "users" / "services" / "token.py"
        assert service_file == expected

    def test_service_has_correct_class(self, tmp_path):
        proj = _project(tmp_path)
        create_service(str(proj), "users/authentication")

        content = (
            proj / "app" / "modules" / "users" / "services" / "authentication.py"
        ).read_text()
        assert "class AuthenticationService" in content
        assert "def __init__(self, repository)" in content

    def test_pascal_case_conversion(self, tmp_path):
        proj = _project(tmp_path)
        create_service(str(proj), "users/password_reset")

        content = (
            proj / "app" / "modules" / "users" / "services" / "password_reset.py"
        ).read_text()
        assert "class PasswordResetService" in content

    def test_raises_if_format_invalid(self, tmp_path):
        proj = _project(tmp_path)

        with pytest.raises(ValueError, match="Formato inválido"):
            create_service(str(proj), "authentication")

    def test_raises_if_module_not_found(self, tmp_path):
        proj = _project(tmp_path)

        with pytest.raises(FileNotFoundError, match="products"):
            create_service(str(proj), "products/listing")

    def test_raises_if_service_already_exists(self, tmp_path):
        proj = _project(tmp_path)
        create_service(str(proj), "users/authentication")

        with pytest.raises(FileExistsError, match="authentication"):
            create_service(str(proj), "users/authentication")


# ============================================================================
# create_repository
# ============================================================================

class TestCreateRepository:
    def test_creates_repository_file(self, tmp_path):
        proj = _project(tmp_path)
        repo_file = create_repository(str(proj), "users/user_query")

        assert repo_file.exists()
        assert repo_file.name == "user_query.py"

    def test_repository_is_inside_correct_dir(self, tmp_path):
        proj = _project(tmp_path)
        repo_file = create_repository(str(proj), "users/user_query")

        expected = proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        assert repo_file == expected

    def test_repository_has_correct_class(self, tmp_path):
        proj = _project(tmp_path)
        create_repository(str(proj), "users/user_query")

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        ).read_text()
        assert "class UserQueryRepository" in content
        assert "def __init__(self, session: AsyncSession)" in content

    def test_repository_without_crud_has_no_methods(self, tmp_path):
        proj = _project(tmp_path)
        create_repository(str(proj), "users/user_query")

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        ).read_text()
        assert "find_by_id" not in content
        assert "find_all" not in content

    def test_repository_with_crud_has_all_methods(self, tmp_path):
        proj = _project(tmp_path)
        create_repository(str(proj), "users/user_query", crud=True)

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        ).read_text()
        for method in ["find_by_id", "find_all", "create", "update", "delete"]:
            assert f"async def {method}" in content, f"Método '{method}' ausente"

    def test_repository_crud_methods_have_ellipsis_body(self, tmp_path):
        proj = _project(tmp_path)
        create_repository(str(proj), "users/user_query", crud=True)

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        ).read_text()
        # Cada método deve ter ... como corpo
        assert content.count("        ...") == 5

    def test_pascal_case_conversion(self, tmp_path):
        proj = _project(tmp_path)
        create_repository(str(proj), "users/order_history", crud=True)

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "order_history.py"
        ).read_text()
        assert "class OrderHistoryRepository" in content

    def test_raises_if_format_invalid(self, tmp_path):
        proj = _project(tmp_path)

        with pytest.raises(ValueError, match="Formato inválido"):
            create_repository(str(proj), "user_query")

    def test_raises_if_module_not_found(self, tmp_path):
        proj = _project(tmp_path)

        with pytest.raises(FileNotFoundError, match="products"):
            create_repository(str(proj), "products/listing")

    def test_raises_if_repository_already_exists(self, tmp_path):
        proj = _project(tmp_path)
        create_repository(str(proj), "users/user_query")

        with pytest.raises(FileExistsError, match="user_query"):
            create_repository(str(proj), "users/user_query")
