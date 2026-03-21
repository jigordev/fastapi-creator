import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="fastc",
    help="🚀 CLI to generate scaffold for modular FastAPI projects.",
    add_completion=False,
)

# Subcommands group "create"
create_app = typer.Typer(help="Create FastAPI projects, modules or components.")
app.add_typer(create_app, name="create")

console = Console()


# ---------------------------------------------------------------------------
# create project <directory>
# ---------------------------------------------------------------------------

@create_app.command("project")
def create_project_cmd(
    directory: str = typer.Argument(
        ...,
        help="Directory where the project scaffold will be created.",
    ),
    module: str = typer.Option(
        None,
        "--module",
        "-m",
        help="Name of an additional module to be created together (e.g., products).",
    ),
):
    """
    Generate the full structure of a modular FastAPI project in the given directory.
    """
    from fastapi_creator.scaffold import create_project

    console.print(
        Panel.fit(
            "[bold cyan]FastAPI Creator[/bold cyan] 🚀\n"
            "[dim]Generating project scaffold...[/dim]",
            border_style="cyan",
        )
    )

    try:
        create_project(directory, extra_module=module)
        console.print(
            f"\n[bold green]✔ Project successfully created at:[/bold green] [yellow]{directory}[/yellow]\n"
        )
        console.print("[dim]To get started:[/dim]")
        console.print(f"  [cyan]cd {directory}[/cyan]")
        console.print("  [cyan]pip install -r requirements.txt[/cyan]")
        console.print("  [cyan]uvicorn app.main:app --reload[/cyan]\n")
    except Exception as e:
        console.print(f"\n[bold red]✖ Error creating project:[/bold red] {e}")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# create module <name>
# ---------------------------------------------------------------------------

@create_app.command("module")
def create_module_cmd(
    name: str = typer.Argument(..., help="Name of the module to add."),
    directory: str = typer.Option(
        ".",
        "--dir",
        "-d",
        help="Root directory of the FastAPI project (default: current directory).",
    ),
):
    """
    Add a new module to an existing FastAPI project structure.
    """
    from fastapi_creator.scaffold import add_module_to_project

    console.print(
        Panel.fit(
            f"[bold cyan]FastAPI Creator[/bold cyan] 🚀\n"
            f"[dim]Adding module '[bold]{name}[/bold]'...[/dim]",
            border_style="cyan",
        )
    )

    try:
        add_module_to_project(directory, name)
        console.print(
            f"\n[bold green]✔ Module '[yellow]{name}[/yellow]' successfully created![/bold green]\n"
        )
    except Exception as e:
        console.print(f"\n[bold red]✖ Error creating module:[/bold red] {e}")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# create service <module/service_name>
# ---------------------------------------------------------------------------

@create_app.command("service")
def create_service_cmd(
    target: str = typer.Argument(
        ...,
        help="Path in the format <module>/<service_name> (e.g., users/authentication).",
    ),
    directory: str = typer.Option(
        ".",
        "--dir",
        "-d",
        help="Root directory of the FastAPI project (default: current directory).",
    ),
):
    """
    Create a new service inside the services/ directory of the specified module.

    Example:

        fastc create service users/authentication
    """
    from fastapi_creator.scaffold import create_service

    module_name = target.split("/")[0] if "/" in target else target
    service_name = target.split("/", 1)[1] if "/" in target else ""

    console.print(
        Panel.fit(
            f"[bold cyan]FastAPI Creator[/bold cyan] 🚀\n"
            f"[dim]Creating service '[bold]{service_name}[/bold]' "
            f"in module '[bold]{module_name}[/bold]'...[/dim]",
            border_style="cyan",
        )
    )

    try:
        service_file = create_service(directory, target)
        console.print(
            f"\n[bold green]✔ Service successfully created:[/bold green] [yellow]{service_file}[/yellow]\n"
        )
    except (ValueError, FileNotFoundError, FileExistsError) as e:
        console.print(f"\n[bold red]✖ Error:[/bold red] {e}")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# create repository <module/repository_name>
# ---------------------------------------------------------------------------

@create_app.command("repository")
def create_repository_cmd(
    target: str = typer.Argument(
        ...,
        help="Path in the format <module>/<repository_name> (e.g., users/user_query).",
    ),
    directory: str = typer.Option(
        ".",
        "--dir",
        "-d",
        help="Root directory of the FastAPI project (default: current directory).",
    ),
    crud: bool = typer.Option(
        False,
        "--crud",
        help="Generate standard CRUD methods (find_by_id, find_all, create, update, delete).",
    ),
):
    """
    Create a new repository inside the repositories/ directory of the specified module.

    Examples:

        fastc create repository users/user_query

        fastc create repository users/user_query --crud
    """
    from fastapi_creator.scaffold import create_repository

    module_name = target.split("/")[0] if "/" in target else target
    repository_name = target.split("/", 1)[1] if "/" in target else ""

    crud_label = " [dim](+ CRUD methods)[/dim]" if crud else ""

    console.print(
        Panel.fit(
            f"[bold cyan]FastAPI Creator[/bold cyan] 🚀\n"
            f"[dim]Creating repository '[bold]{repository_name}[/bold]' "
            f"in module '[bold]{module_name}[/bold]'...[/dim]{crud_label}",
            border_style="cyan",
        )
    )

    try:
        repository_file = create_repository(directory, target, crud=crud)
        console.print(
            f"\n[bold green]✔ Repository successfully created:[/bold green] [yellow]{repository_file}[/yellow]\n"
        )
    except (ValueError, FileNotFoundError, FileExistsError) as e:
        console.print(f"\n[bold red]✖ Error:[/bold red] {e}")
        raise typer.Exit(code=1)

