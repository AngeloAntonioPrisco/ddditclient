import typer
import requests
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from subsystems.auth.dto.UserDTO import UserDTO
from subsystems.local.context_manager import create_context, user_data
from subsystems.local.token_manager import save_token, load_token, clear_token
from subsystems.local.working_directory_manager import clear_working_directory

# -------- CONFIGURATION --------
BASE_URL = "http://localhost:8080/auth"

console = Console()

app = typer.Typer(help="Authentication commands")

# -------- CLI COMMANDS --------

@app.command()
def signup(
        username: str = typer.Argument(..., help="Username to register a new account")
) -> bool:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    password = Prompt.ask(f"[white]{now}[/white] [PASSWORD]", password=True)

    user = UserDTO(username=username, password=password)

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/signup", json=user.__dict__, headers=headers)
    data = response.json()

    new_token = data.get("token")
    if new_token:
        save_token(new_token)

    message = data.get('message')
    error = data.get('error')

    if message:
        create_context(new_token)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        return True
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")
        return False

@app.command()
def login(
        username: str = typer.Argument(..., help="Username to log in to the account")
) -> bool:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    password = Prompt.ask(f"[white]{now}[/white] [[cyan]PASSWORD[/cyan]]", password=True)

    user = UserDTO(username=username, password=password)

    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/login", json=user.__dict__, headers=headers)
    data = response.json()

    new_token = data.get("token")
    if new_token:
        save_token(new_token)

    message = data.get('message')
    error = data.get('error')

    if message:
        create_context(new_token)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        return True
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")
        return False

@app.command()
def logout() -> bool:
    token = load_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    data = response.json()

    if response.status_code == 200:
        clear_token()

    message = data.get('message')
    error = data.get('error')

    if message:
        user_data.clear()
        user_data["username"] = None
        user_data["repositories"] = []

        clear_working_directory()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[green]SUCCESS[/green]] {message}")
        return True
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error}")
        return False
