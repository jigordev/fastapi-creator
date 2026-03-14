"""
Testes de integração do CLI via typer.testing.CliRunner.
Cobre: create project, create module, create service, create repository.
"""
import pytest
from pathlib import Path
from typer.testing import CliRunner
from fastapi_creator.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _invoke(*args):
    """Atalho para invocar o CLI com uma lista de argumentos."""
    return runner.invoke(app, list(args))


def _project(tmp_path: Path, name: str = "myapp") -> Path:
    """Cria um projeto via CLI e retorna o Path."""
    target = str(tmp_path / name)
    _invoke("create", "project", target)
    return Path(target)


# ============================================================================
# create project
# ============================================================================

class TestCLICreateProject:
    def test_exits_zero_on_success(self, tmp_path):
        result = _invoke("create", "project", str(tmp_path / "proj"))
        assert result.exit_code == 0

    def test_success_output_contains_directory(self, tmp_path):
        target = str(tmp_path / "proj")
        result = _invoke("create", "project", target)
        assert "proj" in result.output

    def test_creates_directory_and_files(self, tmp_path):
        target = tmp_path / "proj"
        _invoke("create", "project", str(target))
        assert (target / "app" / "main.py").exists()
        assert (target / "requirements.txt").exists()

    def test_with_extra_module_option(self, tmp_path):
        target = tmp_path / "proj"
        result = _invoke("create", "project", str(target), "--module", "products")
        assert result.exit_code == 0
        assert (target / "app" / "modules" / "products").exists()

    def test_exits_nonzero_on_nonempty_directory(self, tmp_path):
        target = tmp_path / "proj"
        target.mkdir()
        (target / "conflict.txt").write_text("x")

        result = _invoke("create", "project", str(target))
        assert result.exit_code != 0

    def test_error_output_on_failure(self, tmp_path):
        target = tmp_path / "proj"
        target.mkdir()
        (target / "conflict.txt").write_text("x")

        result = _invoke("create", "project", str(target))
        assert "Erro" in result.output


# ============================================================================
# create module
# ============================================================================

class TestCLICreateModule:
    def test_exits_zero_on_success(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "module", "payments", "--dir", str(proj))
        assert result.exit_code == 0

    def test_success_output_contains_module_name(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "module", "payments", "--dir", str(proj))
        assert "payments" in result.output

    def test_creates_module_structure(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "module", "payments", "--dir", str(proj))

        module = proj / "app" / "modules" / "payments"
        assert module.exists()
        assert (module / "__init__.py").exists()
        assert (module / "router.py").exists()

    def test_exits_nonzero_if_module_exists(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "module", "users", "--dir", str(proj))
        assert result.exit_code != 0

    def test_exits_nonzero_if_not_a_project(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = _invoke("create", "module", "anything", "--dir", str(empty))
        assert result.exit_code != 0


# ============================================================================
# create service
# ============================================================================

class TestCLICreateService:
    def test_exits_zero_on_success(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "service", "users/authentication", "--dir", str(proj))
        assert result.exit_code == 0

    def test_success_output_contains_service_name(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "service", "users/authentication", "--dir", str(proj))
        assert "authentication" in result.output

    def test_creates_service_file(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "service", "users/authentication", "--dir", str(proj))

        service = proj / "app" / "modules" / "users" / "services" / "authentication.py"
        assert service.exists()

    def test_service_class_name_in_file(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "service", "users/password_reset", "--dir", str(proj))

        content = (
            proj / "app" / "modules" / "users" / "services" / "password_reset.py"
        ).read_text()
        assert "class PasswordResetService" in content

    def test_exits_nonzero_if_format_invalid(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "service", "authentication", "--dir", str(proj))
        assert result.exit_code != 0

    def test_exits_nonzero_if_module_not_found(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "service", "unknown/my_service", "--dir", str(proj))
        assert result.exit_code != 0

    def test_exits_nonzero_if_service_already_exists(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "service", "users/auth", "--dir", str(proj))
        result = _invoke("create", "service", "users/auth", "--dir", str(proj))
        assert result.exit_code != 0


# ============================================================================
# create repository
# ============================================================================

class TestCLICreateRepository:
    def test_exits_zero_on_success(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "repository", "users/user_query", "--dir", str(proj))
        assert result.exit_code == 0

    def test_success_output_contains_repository_name(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "repository", "users/user_query", "--dir", str(proj))
        assert "user_query" in result.output

    def test_creates_repository_file(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "repository", "users/user_query", "--dir", str(proj))

        repo = proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        assert repo.exists()

    def test_repository_class_name_in_file(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "repository", "users/user_query", "--dir", str(proj))

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        ).read_text()
        assert "class UserQueryRepository" in content

    def test_without_crud_flag_no_crud_methods(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "repository", "users/user_query", "--dir", str(proj))

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        ).read_text()
        assert "find_by_id" not in content

    def test_with_crud_flag_exits_zero(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "repository", "users/user_query", "--dir", str(proj), "--crud")
        assert result.exit_code == 0

    def test_with_crud_flag_generates_methods(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "repository", "users/user_query", "--dir", str(proj), "--crud")

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        ).read_text()
        for method in ["find_by_id", "find_all", "create", "update", "delete"]:
            assert f"async def {method}" in content

    def test_with_crud_methods_have_ellipsis_body(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "repository", "users/user_query", "--dir", str(proj), "--crud")

        content = (
            proj / "app" / "modules" / "users" / "repositories" / "user_query.py"
        ).read_text()
        assert content.count("        ...") == 5

    def test_exits_nonzero_if_format_invalid(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "repository", "user_query", "--dir", str(proj))
        assert result.exit_code != 0

    def test_exits_nonzero_if_module_not_found(self, tmp_path):
        proj = _project(tmp_path)
        result = _invoke("create", "repository", "unknown/repo", "--dir", str(proj))
        assert result.exit_code != 0

    def test_exits_nonzero_if_repository_already_exists(self, tmp_path):
        proj = _project(tmp_path)
        _invoke("create", "repository", "users/user_query", "--dir", str(proj))
        result = _invoke("create", "repository", "users/user_query", "--dir", str(proj))
        assert result.exit_code != 0
