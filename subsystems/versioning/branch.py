import requests
import typer
from datetime import datetime
from rich.console import Console
from subsystems.local.context_manager import add_branch
from subsystems.local.token_manager import load_token
from subsystems.versioning.dto.BranchDTO import BranchDTO

# -------- CONFIGURATION --------
BASE_URL = "http://localhost:8080/branches"

console = Console()

app = typer.Typer(help="Branches management commands")

# -------- CLI COMMANDS ----------

@app.command()
def init(
        repository_name: str = typer.Argument(..., help="Name of the repository where the branch will be created"),
        resource_name: str = typer.Argument(..., help="Name of the resource for which the branch will be created"),
        branch_name: str = typer.Argument(..., help="Name of the branch to create")
):
    branch_dto = BranchDTO(repository_name, resource_name, branch_name)

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/create", json=branch_dto.__dict__, headers=headers)
    data = response.json()

    message = data.get('message')
    error = data.get('error')

    if message:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        add_branch(repository_name, resource_name, branch_name)
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")


@app.command("ls")
def list_branches(
        repository_name: str = typer.Argument(..., help="Name of the repository containing the resource"),
        resource_name: str = typer.Argument(..., help="Name of the resource whose branches will be listed")
):
    from subsystems.local import context_manager

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Branches found successfully for "
        f"{resource_name} resource in {repository_name} repository")

    branches = context_manager.list_branches(repository_name, resource_name)
    for branch in branches:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] {branch}")