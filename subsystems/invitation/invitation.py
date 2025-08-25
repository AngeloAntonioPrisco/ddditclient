import requests
import typer
from datetime import datetime
from rich.console import Console
from subsystems.invitation.dto.InvitationDTO import InvitationDTO
from subsystems.local.token_manager import load_token

# -------- CONFIGURATION --------
BASE_URL = "http://localhost:8080/invitations"

console = Console()

app = typer.Typer(help="Invitations management commands")

# -------- CLI COMMANDS --------

@app.command("invite")
def send_invitation(
        to_username: str = typer.Argument(..., help="Username of the user to send the invitation to"),
        repository_name: str = typer.Argument(..., help="Name of the repository for the invitation")
):
    invitation_dto = InvitationDTO(to_username, repository_name)

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/invite", json=invitation_dto.__dict__, headers=headers)
    data = response.json()

    message = data.get('message')
    error = data.get('error')

    if message:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")

@app.command("pending")
def list_pending_invitations():

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.get(f"{BASE_URL}/list", headers=headers)
    print(response.json())
    json_data = response.json()

    error = json_data.get("error")
    if error:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")
        return None

    data = json_data.get("invitations", [])
    message = json_data.get('message')

    if message:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")

        if not data:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] No invitations received")

            return None

        for invitation in data:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            console.print(
                f"[white]{now}[/white] [[cyan]INFO[/cyan]] Received invitation from "
                f"{invitation.get('toUsername')} "
                f"for {invitation.get('repositoryName')} repository")

@app.command("accept")
def accept_invitation(
        from_username: str = typer.Argument(..., help="Username of the user who sent the invitation"),
        repository_name: str = typer.Argument(..., help="Name of the repository for the accepted invitation")
):
    from subsystems.local import context_manager

    invitation_dto = InvitationDTO(from_username, repository_name)

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/accept", json=invitation_dto.__dict__, headers=headers)
    data = response.json()

    message = data.get('message')
    error = data.get('error')

    if message:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        context_manager.update_context_after_invitation(token, repository_name)

    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")