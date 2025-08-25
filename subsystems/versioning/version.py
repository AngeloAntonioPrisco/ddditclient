import mimetypes
import requests
import typer
import os
from rich.text import Text
from pathlib import Path
from datetime import datetime
from json import decoder
from requests_toolbelt.multipart import decoder
from rich.console import Console
from subsystems.local.token_manager import load_token

# -------- CONFIGURATION --------
BASE_URL = "http://localhost:8080/versions"

console = Console()

app = typer.Typer(help="Versions management commands")

# -------- CLI COMMANDS --------

@app.command()
def push(
        repository_name: str = typer.Argument(..., help="Name of the repository to push to"),
        resource_name: str = typer.Argument(..., help="Name of the resource to push to"),
        branch_name: str = typer.Argument(..., help="Name of the branch to push to"),
        version_name: str = typer.Argument(..., help="Name of the version to push"),
        comment_option: bool = typer.Option(..., help="Use this flag to add a comment to the push"),
        comment: str = typer.Argument(..., help="Comment describing the push"),
        is_mesh: bool = typer.Argument(..., help="Set True if the version is a mesh, False if it is a material"),
        WORKING_DIRECTORY: Path = typer.Argument(..., help="Local working directory path")
):
    from subsystems.local import context_manager

    start_path = Path(WORKING_DIRECTORY)
    matches = list(start_path.rglob(version_name))
    version_path = matches[0].resolve()

    files = []
    data = {
        "repositoryName": repository_name,
        "resourceName": resource_name,
        "branchName": branch_name,
        "versionName": version_name.split(".")[0] if is_mesh else version_name,
        "comment": comment if comment_option else " "
    }

    if version_path.is_file() and is_mesh:
        mime_type, _ = mimetypes.guess_type(version_path)
        files.append(
            ("mesh", (version_path.name, open(version_path, "rb"), mime_type or "application/octet-stream"))
        )
    elif version_path.is_dir() and not is_mesh:
        for f in version_path.iterdir():
            if f.is_file():
                mime_type, _ = mimetypes.guess_type(f)
                files.append(
                    ("material", (f.name, open(f, "rb"), mime_type or "application/octet-stream"))
                )

    token = load_token()

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/push", data=data, files=files, headers=headers)
    data =  response.json()

    message = data.get("message")
    error = data.get("error")

    if message:
        parts = data.get('message').split()
        generated_version_name = parts[6]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        context_manager.add_version(repository_name, resource_name, branch_name, generated_version_name)
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")

@app.command("ls")
def list_versions(
        repository_name: str = typer.Argument(..., help="Name of the repository containing the branch"),
        resource_name: str = typer.Argument(..., help="Name of the resource containing the branch"),
        branch_name: str = typer.Argument(..., help="Name of the branch whose versions to list")
):
    from subsystems.local import context_manager

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Versions found successfully "
                  f"for {branch_name} branch for {resource_name} resource in {repository_name} repository")

    versions = context_manager.list_versions(repository_name, resource_name, branch_name)
    for version in versions:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] {version}")


@app.command()
def pull(
        repository_name: str = typer.Argument(..., help="Name of the repository containing the branch"),
        resource_name: str = typer.Argument(..., help="Name of the resource containing the branch"),
        branch_name: str = typer.Argument(..., help="Name of the branch containing the version"),
        version_name: str = typer.Argument(..., help="Name of the version to pull"),
        WORKING_DIRECTORY: Path = typer.Argument(..., help="Local working directory path")
):
    data = {
        "repositoryName": repository_name,
        "resourceName": resource_name,
        "branchName": branch_name,
        "versionName": version_name,
        "comment": " "
    }

    pull_path = WORKING_DIRECTORY.joinpath(version_name)

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/pull", data=data, headers=headers)

    if response.status_code == 200 and 'multipart' in response.headers.get('Content-Type', ''):
        os.makedirs(pull_path, exist_ok=True)
        multipart_data = decoder.MultipartDecoder(response.content, response.headers['Content-Type'])

        for part in multipart_data.parts:
            cd = part.headers.get(b'Content-Disposition', b'').decode()
            ct = part.headers.get(b'Content-Type', b'application/octet-stream').decode()

            if 'name="message"' in cd:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {part.text}")
                continue

            if 'filename=' in cd:
                import re
                match = re.search(r'filename="(.+?)"', cd)
                filename = match.group(1) if match else "unknown_file"

                file_path = os.path.join(pull_path, filename)
                with open(file_path, 'wb') as f:
                    f.write(part.content)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] Saved file {filename} ({len(part.content)} byte, {ct})")
    else:
        error = response.json().get("error")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")


@app.command("metadata")
def show_version_metadata(
        repository_name: str = typer.Argument(..., help="Name of the repository containing the branch"),
        resource_name: str = typer.Argument(..., help="Name of the resource containing the branch"),
        branch_name: str = typer.Argument(..., help="Name of the branch containing the version"),
        version_name: str = typer.Argument(..., help="Name of the version whose metadata to show")
):
    data = {
        "repositoryName": repository_name,
        "resourceName": resource_name,
        "branchName": branch_name,
        "versionName": version_name,
        "comment": None
    }

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/metadata", data=data, headers=headers)

    data = response.json()

    message = data.get("message")
    error = data.get("error")
    version_name = data.get("versionName")
    username = data.get("username")
    pushed_at = data.get("pushedAt")
    comment = data.get("comment")
    tags = data.get("tags")

    dt = datetime.fromisoformat(str(pushed_at))
    pushed_at = dt.strftime("%Y-%m-%d %H:%M:%S")

    if not comment or not comment.strip():
        comment = "No comment associated with this version"

    if not tags or len(tags) == 0:
        tags = "No AI tags associated with this version"

    if message:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        text = Text()
        text.append(f"{now} ", style="white")
        text.append("[INFO]", style="cyan")
        text.append(f" Version {version_name} pushed by {username} at {pushed_at}")
        console.print(text)
        console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] Additional comment - {comment}")
        console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] AI tags - {tags}")
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")


