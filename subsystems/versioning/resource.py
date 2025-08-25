import requests
import typer
from datetime import datetime
from rich.console import Console
from subsystems.local.context_manager import add_resource
from subsystems.local.token_manager import load_token
from subsystems.versioning.dto.ResourceDTO import ResourceDTO

# -------- CONFIGURATION --------
BASE_URL = "http://localhost:8080/resources"

console = Console()

app = typer.Typer(help="Resources management commands")

# -------- CLI COMMANDS --------

@app.command()
def init(
        repository_name: str = typer.Argument(..., help="Name of the repository where the resource will be created"),
        resource_name: str = typer.Argument(..., help="Name of the resource to create")
):
    resource_dto = ResourceDTO(repository_name, resource_name)

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/create", json=resource_dto.__dict__, headers=headers)
    data = response.json()

    message = data.get('message')
    error = data.get('error')

    if "message" in data:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        add_resource(repository_name, resource_name)
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")

@app.command("ls")
def list_resources(
        repository_name: str = typer.Argument(..., help="Name of the repository containing the resources")
):
    from subsystems.local import context_manager

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Resources found successfully in {repository_name} repository")

    resources = context_manager.list_resources(repository_name)
    for resource in resources:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] {resource}")

@app.command("tree")
def show_version_tree(
        repository_name: str = typer.Argument(..., help="Name of the repository containing the resource"),
        resource_name: str = typer.Argument(..., help="Name of the resource whose version tree will be displayed")
):
    from subsystems.local import context_manager

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Version tree found successfully "
                  f"for {resource_name} resource in {repository_name} repository")

    resources = context_manager.list_resources(repository_name)
    for resource in resources:
        if resource == resource_name:
            branches = context_manager.list_branches(repository_name, resource)

            for branch in branches:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] {branch}")

                versions = context_manager.list_versions(repository_name, resource, branch)
                versions_string = ""
                for version in versions:
                    versions_string += version + " -> "

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] {versions_string[:-4]}")