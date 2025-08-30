# Dddit CLI User Manual

**Version:** 1.0.1  
**Author:** Angelo Antonio Prisco

Dddit CLI is a command-line interface (CLI) for managing repositories, resources, branches, and versions, with support for authentication and user invitations.

## 1. Starting the CLI

Run the executable file to start the CLI.  
On startup, you will see something like:

```
~ $
```

The `~` symbol indicates the **current context**.

## 2. Context Navigation (`cd`)

The CLI uses a **context hierarchy** similar to a file system:

```
~                                       → root (home)
~\username                              → user context
~\username\repo                         → repository context
~\username\repo\resource                → resource context
~\username\repo\resource\branch         → branch context
~\username\repo\resource\branch\version → version context
```
The commands available depend on your current location within the context.

### `cd` Command

Used to move between context levels.

**Syntax:**

```
cd <context_name>
```

- `cd ..` → move up one level
- `cd <repository>` → enter a repository
- `cd <resource>` → enter a resource
- `cd <branch>` → enter a branch
- `cd <version>` → enter a version

**Example:**

```
~ $ cd my_repo
~\my_repo $ cd resource1
~\my_repo\resource1 $ cd main
~\my_repo\resource1\main $ cd version1
```

## 3. Working Directory (`cwd`)

Sets the **local folder** where version files are stored and where files to upload are searched.

**Syntax:**

```
cwd <directory_path>
```

**Example:**

```
~ $ cwd C:\Users\Angelo\Documents\Projects
```

To show the current directory:

```
show cwd
```

## 4. Authentication Commands

### `signup <username>`

Create a new user account.

### `login <username>`

Log in with an existing user.

### `logout`

Log out the current user and reset context.

**Example:**

```
~ $ signup angelo
2025-08-30 14:51:07 [PASSWORD]:
~\angelo $ logout
~\angelo $ login angelo
2025-08-30 14:51:07 [PASSWORD]:
```

## 5. Invitation Management (`invite`, `pending`, `accept`)

- **Invite a user to a repository:**

```
invite <username> <repository>
```

- **List pending invitations:**

```
pending
```

- **Accept an invitation:**

```
accept <username> <repository>
```

## 6. Repository Commands

### `init <repository_name>`

Create a new repository (user-level only `~\username`).

### `ls [--o] [--c]`

List repositories:
- `--o` → owned by the user
- `--c` → contributed repositories

**Example:**

```
~\angelo $ init test_project
~\angelo $ ls --o
2025-08-30 14:51:19 [INFO] test_project (owned)
```

## 7. Resource Commands

### `init <resource_name>`

Create a new resource within a repository.

### `ls`

List all resources in the current repository.

### `tree`

Show the version tree of the resource.

## 8. Branch Commands

### `init <branch_name>`

Create a new branch in the current resource.

### `ls`

List all branches of the current resource.

## 9. Version Commands

### `push <version_name> [--m "comment"]`

Upload a local version to the current branch. Optional comment with `-m`.

### `pull`

Download the current version to the local directory.

### `ls`

List all versions of the current branch.

### `metadata`

Show metadata of the current version.

**Example:**

```
~\angelo\repo1\resource1\main $ push v1.0 --m "First version"
~\angelo\repo1\resource1\main\v1.0 $ metadata
```

## 10. Exiting the CLI

```
exit
```
or
```
quit
```

## Practical Tips

- Use `cd ..` to move back in context.
- Always check the working directory with `show cwd`.
- Errors are displayed with `[ERROR]` and system info.
- Navigate repositories, resources, branches, and versions using tab completion.

## Quick Reference Table

| Command                                 | Description                          | Example                                  |
|--|--||
| **cd <name>**                           | Change context                       | `cd my_repo`                             |
| **cd ..**                               | Move up one context level            | `cd ..`                                  |
| **cwd <path>**                          | Set local working folder             | `cwd C:\Users\Angelo\Documents\Projects` |
| **show cwd**                            | Show current working directory       | `show cwd`                               |
| **signup <username>**                   | Create new user                      | `signup angelo`                          |
| **login <username>**                    | Log in user                          | `login angelo`                           |
| **logout**                              | Log out user                         | `logout`                                 |
| **invite <username> <repository>**      | Invite user to repository            | `invite mario repo_test`                 |
| **pending**                             | List pending invites                 | `pending`                                |
| **accept <username> <repository>**      | Accept invite                        | `accept mario repo_test`                 |
| **init <repository_name>**              | Create new repository                | `init test_project`                      |
| **ls [--o] [--c]**                      | List repositories                    | `ls --o`                                 |
| **init <resource_name>**                | Create resource in repository        | `init resource1`                         |
| **ls**                                  | List resources                       | `ls`                                     |
| **tree**                                | Show version tree                    | `tree`                                   |
| **init <branch_name>**                  | Create new branch                    | `init main`                              |
| **ls**                                  | List branches                        | `ls`                                     |
| **push <version_name> [--m "comment"]** | Upload version with optional comment | `push v1.0 --m "First version"`          |
| **pull**                                | Download version                     | `pull`                                   |
| **ls**                                  | List versions                        | `ls`                                     |
| **metadata**                            | Show version metadata                | `metadata`                               |
| **exit / quit**                         | Exit CLI                             | `exit`                                   |


