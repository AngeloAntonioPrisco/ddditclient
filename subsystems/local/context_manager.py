import requests
import jwt
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from subsystems.versioning.dto.RepositoryDTO import RepositoryDTO
from subsystems.versioning.dto.ResourceDTO import ResourceDTO

# -------- CONFIGURATION --------
BASE_URL = "http://localhost:8080"

console = Console()

user_data: Dict = {
    "username": None,
    "repositories": []
}

# -------- CONTEXT CREATION --------

def create_context(token):
    try:
        username = jwt.decode(token, options={"verify_signature": False}).get("sub")
        set_username(username)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Initializing local context 0%")

    repositories = get_repositories(token)

    if repositories is None or len(repositories) == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Initializing local context 100%")
        console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Context initialized")
        return None

    repository_counter = 0
    for repository_name in repositories:
        repository_counter += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Initializing local context {repository_counter/len(repositories) * 100:.2f}%")
        resources = get_resources(token, repository_name)

        if resources is None:
            return None

        for resource_name in resources:
            get_branches_and_versions(token, repository_name, resource_name)

    console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Context initialized")
    return None

# -------- CONTEXT UPDATE --------

def update_context_after_invitation(token, repository_name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Updating local context 0%")

    add_repository(repository_name, False)
    resources = get_resources(token, repository_name)

    if resources is None or len(resources) == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Updating local context 100%")

    resource_counter = 0
    for resource_name in resources:
        resource_counter += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Updating local context {resource_counter / len(resources) * 100:.2f}%")
        get_branches_and_versions(token, repository_name, resource_name)

    console.print(f"[white]{now}[/white] [yellow][SYS_INFO][/yellow] Context updated")
    return None

# -------- CONTEXT RETRIEVING FUNCTIONS --------

def get_repositories(token) -> list[str] | None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response_owned = requests.get(f"{BASE_URL}/repositories/owned", headers=headers)
    response_contributed = requests.get(f"{BASE_URL}/repositories/contributed", headers=headers)

    json_owned = response_owned.json()
    json_contributed = response_contributed.json()

    error_message_owned = json_owned.get("error")
    error_message_contributed = json_contributed.get("error")

    if error_message_owned or error_message_contributed:
        user_data.clear()
        user_data["username"] = None
        user_data["repositories"] = []

        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Error during context initialization")

        if error_message_owned:
            console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error_message_owned}")

        if error_message_contributed:
            console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error_message_contributed}")

        return None

    repositories = []

    for repository in json_owned.get("ownedRepositories", []):
        repository_name = repository.get("repositoryName")
        add_repository(repository_name, owned=True)
        repositories.append(repository_name)

    for repository in json_contributed.get("contributedRepositories", []):
        repository_name = repository.get("repositoryName")
        add_repository(repository_name, owned=False)
        repositories.append(repository_name)

    return repositories

def get_resources(token, repository_name) -> list[str] | None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    repository_dto = RepositoryDTO(repository_name)

    response = requests.post(f"{BASE_URL}/resources/list", json=repository_dto.__dict__, headers=headers)

    error_message = response.json().get("error")

    if error_message:
        user_data.clear()
        user_data["username"] = None
        user_data["repositories"] = []

        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Error during context initialization")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error_message}")

        return None

    data = response.json()["resources"]

    resources = []

    for resource in data:
        resource_name = resource.get("resourceName")
        add_resource(repository_name, resource_name)
        resources.append(resource_name)

    return resources

def get_branches_and_versions(token, repository_name, resource_name) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    resource_dto = ResourceDTO(repository_name, resource_name)

    response = requests.post(f"{BASE_URL}/resources/tree", json=resource_dto.__dict__, headers=headers)

    error_message = response.json().get("error")

    if error_message:
        user_data.clear()
        user_data["username"] = None
        user_data["repositories"] = []

        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] Error during context initialization")
        console.print(f"[white]{now}[/white] [[red]ERROR[/red]] {error_message}")

        return None
    
    data = response.json().get("versionTree")

    for branch_name, versions in data.items():
        add_branch(repository_name, resource_name, branch_name)
        
        for version_name in versions:
            add_version(repository_name, resource_name, branch_name, version_name)

    return None

# -------- CONTEXT WRITING FUNCTIONS --------

def set_username(username: str):
    user_data["username"] = username

def add_repository(repository_name: str, owned: bool):
    if not any(r["name"] == repository_name for r in user_data["repositories"]):
        user_data["repositories"].append({
            "name": repository_name,
            "owned": owned,
            "resources": []
        })

def add_resource(repository_name: str, resource_name: str):
    repository = next((r for r in user_data["repositories"] if r["name"] == repository_name), None)
    if repository:
        if not any(res["name"] == resource_name for res in repository["resources"]):
            repository["resources"].append({
                "name": resource_name,
                "branches": []
            })

def add_branch(repository_name: str, resource_name: str, branch_name: str):
    repository = next((r for r in user_data["repositories"] if r["name"] == repository_name), None)
    if repository:
        resource = next((res for res in repository["resources"] if res["name"] == resource_name), None)
        if resource:
            if not any(b["name"] == branch_name for b in resource["branches"]):
                resource["branches"].append({
                    "name": branch_name,
                    "versions": []
                })

def add_version(repository_name: str, resource_name: str, branch_name: str, version_name: str):
    repository = next((r for r in user_data["repositories"] if r["name"] == repository_name), None)
    if repository:
        resource = next((res for res in repository["resources"] if res["name"] == resource_name), None)
        if resource:
            branch = next((b for b in resource["branches"] if b["name"] == branch_name), None)
            if branch and version_name not in branch["versions"]:
                branch["versions"].append(version_name)

# -------- CONTEXT READING FUNCTIONS --------

def list_repositories(filter_type: str = "all") -> List[str]:
    result = []
    for r in user_data["repositories"]:
        if filter_type == "all" or (filter_type == "owned" and r["owned"]) or (
                filter_type == "contributed" and not r["owned"]):
            result.append(f"{r['name']} ({'owned' if r['owned'] else 'contributed'})")
    return result

def list_resources(repository_name: str) -> List[str]:
    repository = next((r for r in user_data["repositories"] if r["name"] == repository_name), None)
    return [res["name"] for res in repository["resources"]] if repository else []

def list_branches(repository_name: str, resource_name: str) -> List[str]:
    repository = next((r for r in user_data["repositories"] if r["name"] == repository_name), None)
    if repository:
        resource = next((res for res in repository["resources"] if res["name"] == resource_name), None)
        if resource:
            return [b["name"] for b in resource["branches"]]
    return []

def list_versions(repository_name: str, resource_name: str, branch_name: str) -> List[str]:
    repository = next((r for r in user_data["repositories"] if r["name"] == repository_name), None)
    if repository:
        resource = next((res for res in repository["resources"] if res["name"] == resource_name), None)
        if resource:
            branch = next((b for b in resource["branches"] if b["name"] == branch_name), None)
            if branch:
                return branch["versions"]
    return []

# -------- CONTEXT DEBUG FUNCTION --------

def print_structure():
    import json
    print(json.dumps(user_data, indent=4))
