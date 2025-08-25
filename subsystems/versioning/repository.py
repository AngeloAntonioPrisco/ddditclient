import requests
import typer
from datetime import datetime
from rich.console import Console
from subsystems.local.context_manager import add_repository
from subsystems.local.token_manager import load_token
from subsystems.versioning.dto.RepositoryDTO import RepositoryDTO

# -------- CONFIGURATION --------
BASE_URL = "http://localhost:8080/repositories"

console = Console()

app = typer.Typer(help="Repository management commands")

# -------- CLI COMMANDS --------

@app.command()
def init(
        repository_name: str = typer.Argument(..., help="Name of the repository to create")
):
    repository = RepositoryDTO(repository_name)

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/create", json=repository.__dict__, headers=headers)
    data = response.json()

    message = data.get('message')
    error = data.get('error')

    if message:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        add_repository(repository_name, True)
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")


@app.command("ls")
def list_repos(
        o: bool = typer.Option(False, "--o", help="List only owned repositories"),
        c: bool = typer.Option(False, "--c", help="List only contributed repositories")
):
    from subsystems.local import context_manager

    if o:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Owned repositories found successfully")
        repositories = context_manager.list_repositories("owned")

    elif c:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Contributed repositories found successfully")
        repositories = context_manager.list_repositories("contributed")

    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Owned repositories found successfully")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Contributed repositories found successfully")
        repositories = context_manager.list_repositories()

    for repository_name in repositories:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] {repository_name}")