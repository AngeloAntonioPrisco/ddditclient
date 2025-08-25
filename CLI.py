import typer
import shlex
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from rich.console import Console
from datetime import datetime
from subsystems.auth import auth
from subsystems.invitation import invitation
from subsystems.local import context_manager
from subsystems.local.context_manager import user_data
from subsystems.local.token_manager import load_token
from subsystems.local.working_directory_manager import load_working_directory, save_working_directory
from subsystems.versioning import repository, resource, branch, version
from subsystems.versioning.resource import show_version_tree

# -------- CONFIGURATION --------
console = Console()

app = typer.Typer(help="Dddit CLI [v0.0.1]")

CONTEXT_STRING = "~"

WORKING_DIRECTORY = load_working_directory()

# -------- PRINT PARAMETERS ERROR FUNCTION --------

def print_parameters_error():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Missing parameters")

# -------- CONTEXT STRING MANAGEMENT FUNCTIONS --------

def reset_context_string():
    global CONTEXT_STRING
    CONTEXT_STRING = "~"

def add_context_point(context_point: str):
    global CONTEXT_STRING
    CONTEXT_STRING = CONTEXT_STRING + "\\" + context_point

def remove_last_context_point():
    global CONTEXT_STRING
    pos = CONTEXT_STRING.rfind("\\")
    if pos != -1:
        CONTEXT_STRING = CONTEXT_STRING[:pos]

# -------- WORKING DIRECTORY MANAGEMENT FUNCTION --------

def check_version_name(version_name: str):
    global WORKING_DIRECTORY
    base_path = Path(WORKING_DIRECTORY)

    matches = list(base_path.rglob(version_name))

    if not matches:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Version not found in file system")
        return None

    if len(matches) > 1:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] More than one result found for {version_name} version name")
        for m in matches:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] {m}")
        return None

    target = matches[0]

    if target.is_file():
        return True
    elif target.is_dir():
        contents = list(target.iterdir())
        if all(c.is_file() for c in contents):
            return False
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Material version {target} contains other directories")
            return None
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {target} is neither a file nor a directory")
        return None

# -------- AUTO COMPLETION MANAGEMENT CLASS --------

class CDCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        if not text.lower().startswith("cd "):
            return

        parts = text.split()
        prefix = parts[-1] if len(parts) > 1 else ""

        level = CONTEXT_STRING.count("\\")
        options = []
        if level == 1:
            options = [r['name'] for r in user_data["repositories"]]
        elif level == 2:
            parts_ctx = CONTEXT_STRING.split("\\")
            options = context_manager.list_resources(parts_ctx[-1])
        elif level == 3:
            parts_ctx = CONTEXT_STRING.split("\\")
            options = context_manager.list_branches(parts_ctx[-2], parts_ctx[-1])
        elif level == 4:
            parts_ctx = CONTEXT_STRING.split("\\")
            options = context_manager.list_versions(parts_ctx[-3], parts_ctx[-2], parts_ctx[-1])

        for opt in options:
            if prefix == "" or opt.startswith(prefix):
                start_pos = -len(prefix) if prefix else 0
                yield Completion(opt, start_position=start_pos)

# -------- CLI --------

def repl():
    global CONTEXT_STRING
    global WORKING_DIRECTORY

    console.print("[white]Dddit CLI v1.0.1 (c) Angelo Antonio Prisco[/white]\n")
    context_manager.create_context(load_token())

    if context_manager.user_data["username"] is None:
        CONTEXT_STRING = "~"
    else:
        CONTEXT_STRING = CONTEXT_STRING + "\\" + context_manager.user_data.get("username")

    session = PromptSession(completer=CDCompleter())

    while True:
        cmd = session.prompt(f"{CONTEXT_STRING} $ ").strip()
        if not cmd:
            continue

        if cmd.lower() in ("exit", "quit"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"[white]{now}[/white] [[green]SUCCESS[/green] Successfully exited")
            break

        parts = shlex.split(cmd, posix=False)
        command = parts[0].lower()

        try:
            # -------- CHANGE DIRECTORY COMMAND --------
            if command == "cd":
                if len(parts) < 2:
                    print_parameters_error()
                    continue

                step = parts[1]

                if CONTEXT_STRING.count("\\") == 0:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Current context is empty")
                    continue

                if step == "..":
                    if CONTEXT_STRING.count("\\") == 1:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Use logout command to clear context")
                        continue

                    remove_last_context_point()
                    console.print()

                elif CONTEXT_STRING.count("\\") == 1:
                    repositories = [r['name'] for r in user_data["repositories"]]
                    if step not in repositories:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {step} does not exist in current context point")
                        continue
                    else:
                        add_context_point(step)
                        console.print()

                elif CONTEXT_STRING.count("\\") == 2:
                    parts = CONTEXT_STRING.split("\\")
                    resources = context_manager.list_resources(parts[-1])
                    if step not in resources:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {step} does not exist in current context point")
                        continue
                    else:
                        add_context_point(step)
                        console.print()

                elif CONTEXT_STRING.count("\\") == 3:
                    parts = CONTEXT_STRING.split("\\")
                    branches = context_manager.list_branches(parts[-2], parts[-1])
                    if step not in branches:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {step} does not exist in current context point")
                        continue
                    else:
                        add_context_point(step)
                        console.print()

                elif CONTEXT_STRING.count("\\") == 4:
                    parts = CONTEXT_STRING.split("\\")
                    versions = context_manager.list_versions(parts[-3], parts[-2], parts[-1])
                    if step not in versions:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {step} does not exist in current context point")
                        continue
                    else:
                        add_context_point(step)
                        console.print()

                elif CONTEXT_STRING.count("\\") == 5:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Cannot select additional items after a version has been selected")
                    continue

            # -------- DIRECTORY COMMANDS --------
            elif command == "cwd":
                if len(parts) < 2:
                    print_parameters_error()
                    continue

                path = parts[1].strip()

                if len(path) == 2 and path[1] == ":":
                    path += "\\"

                p = Path(path)

                if p.exists() and p.is_dir():
                    WORKING_DIRECTORY = p.resolve()
                    save_working_directory(str(WORKING_DIRECTORY))
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(
                        f"[white]{now}[/white] [[green]SUCCESS[/green]] Working directory set to {WORKING_DIRECTORY}")
                else:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Invalid path to use as working directory")

            elif command == "show":
                if len(parts) < 2:
                    print_parameters_error()
                    continue

                subcommand = parts[1]
                if subcommand == "cwd":
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(f"[white]{now}[/white] [[cyan]INFO[/cyan]] Current working directory is {WORKING_DIRECTORY}")
                else:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {subcommand} is not a subcommand for {command} command")

            # -------- AUTH COMMANDS --------
            elif command == "signup":
                if len(parts) < 2:
                    print_parameters_error()
                    continue

                username = parts[1]
                if auth.signup(username):
                    add_context_point(username)

            elif command == "login":
                if len(parts) < 2:
                    print_parameters_error()
                    continue

                username = parts[1]
                if auth.login(username):
                    add_context_point(username)

            elif command == "logout":
                if auth.logout():
                    reset_context_string()

            # -------- INVITATION COMMANDS --------
            elif command == "invite":
                if len(parts) < 3:
                    print_parameters_error()
                    continue

                username = parts[1]
                repository_name = parts[2]
                invitation.send_invitation(username, repository_name)

            elif command == "pending":
                if len(parts) < 1:
                    print_parameters_error()
                    continue

                invitation.list_pending_invitations()

            elif command == "accept":
                if len(parts) < 3:
                    print_parameters_error()
                    continue

                username = parts[1]
                repository_name = parts[2]
                invitation.accept_invitation(username, repository_name)

            # -------- REPO COMMANDS --------
            elif command == "init" and CONTEXT_STRING.count("\\") == 1:
                if len(parts) < 2:
                    print_parameters_error()
                    continue

                repository_name = parts[1]
                repository.init(repository_name)

            elif command == "ls" and CONTEXT_STRING.count("\\") == 1:
                owned = "--o" in parts
                contrib = "--c" in parts
                repository.list_repos(o=owned, c=contrib)

            # -------- RESOURCE COMMANDS --------
            elif command == "init" and CONTEXT_STRING.count("\\") == 2:
                if len(parts) < 2:
                    print_parameters_error()
                    continue

                repository_name = CONTEXT_STRING.split("\\")[-1]
                resource_name = parts[1]

                resource.init(repository_name, resource_name)

            elif command == "ls" and CONTEXT_STRING.count("\\") == 2:
                repository_name = CONTEXT_STRING.split("\\")[-1]

                resource.list_resources(repository_name)

            elif command == "tree" and CONTEXT_STRING.count("\\") == 3:
                repository_name = CONTEXT_STRING.split("\\")[-2]
                resource_name = CONTEXT_STRING.split("\\")[-1]

                show_version_tree(repository_name, resource_name)

            # -------- BRANCH COMMANDS --------
            elif command == "init" and CONTEXT_STRING.count("\\") == 3:
                repository_name = CONTEXT_STRING.split("\\")[-2]
                resource_name = CONTEXT_STRING.split("\\")[-1]
                branch_name = parts[1]

                branch.init(repository_name, resource_name, branch_name)

            elif command == "ls" and CONTEXT_STRING.count("\\") == 3:
                repository_name = CONTEXT_STRING.split("\\")[-2]
                resource_name = CONTEXT_STRING.split("\\")[-1]

                branch.list_branches(repository_name, resource_name)

            # -------- VERSION COMMANDS --------
            elif command == "push" and CONTEXT_STRING.count("\\") == 4:
                comment_option = "--m" in parts

                if comment_option and len(parts) < 4:
                    print_parameters_error()
                    continue

                elif comment_option and len(parts) > 4:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(f"[white]{now}[/white] [[red]ERROR[/red]] More parameters than expected")
                    continue

                elif not comment_option and len(parts) > 2:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(f"[white]{now}[/white] [[red]ERROR[/red]] More parameters than expected")
                    continue

                elif len(parts) < 2:
                    print_parameters_error()
                    continue

                repository_name = CONTEXT_STRING.split("\\")[-3]
                resource_name = CONTEXT_STRING.split("\\")[-2]
                branch_name = CONTEXT_STRING.split("\\")[-1]

                if len(parts) == 2:
                    version_name = parts[1]
                    result_checking = check_version_name(version_name)
                    if result_checking is None:
                        continue

                    if result_checking:
                        version.push(repository_name, resource_name, branch_name, version_name, comment_option, "", True, WORKING_DIRECTORY)
                    else:
                        version.push(repository_name, resource_name, branch_name, version_name, comment_option, "", False, WORKING_DIRECTORY)
                elif len(parts) == 4:
                    version_name = parts[1]
                    comment = parts[3].replace("\"", "")
                    result_checking = check_version_name(version_name)
                    if result_checking is None:
                        continue

                    if result_checking:
                        version.push(repository_name, resource_name, branch_name, version_name, comment_option, comment,True, WORKING_DIRECTORY)
                    else:
                        version.push(repository_name, resource_name, branch_name, version_name, comment_option, comment,False, WORKING_DIRECTORY)

            elif command == "ls" and CONTEXT_STRING.count("\\") == 4:
                repository_name = CONTEXT_STRING.split("\\")[-3]
                resource_name = CONTEXT_STRING.split("\\")[-2]
                branch_name = CONTEXT_STRING.split("\\")[-1]

                version.list_versions(repository_name, resource_name, branch_name)

            elif command == "pull" and CONTEXT_STRING.count("\\") == 5:
                repository_name = CONTEXT_STRING.split("\\")[-4]
                resource_name = CONTEXT_STRING.split("\\")[-3]
                branch_name = CONTEXT_STRING.split("\\")[-2]
                version_name = CONTEXT_STRING.split("\\")[-1]

                version.pull(repository_name, resource_name, branch_name, version_name, WORKING_DIRECTORY)

            elif command == "metadata" and CONTEXT_STRING.count("\\") == 5:
                repository_name = CONTEXT_STRING.split("\\")[-4]
                resource_name = CONTEXT_STRING.split("\\")[-3]
                branch_name = CONTEXT_STRING.split("\\")[-2]
                version_name = CONTEXT_STRING.split("\\")[-1]

                version.show_version_metadata(repository_name, resource_name, branch_name, version_name)

            # -------- ERROR MANAGEMENT --------
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Command {command} not found")

        except Exception as e:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {e}")

if __name__ == "__main__":
    repl()
