#!/usr/bin/env python3
"""Project setup script that initializes a Python project using uv."""

import os
import subprocess
import sys
from pathlib import Path


def check_uv_installed() -> None:
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("uv is installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "uv is not installed. Please, install it from: "
            "https://docs.astral.sh/uv/getting-started/installation/#installation-methods"
        )
        sys.exit(1)


def get_user_input() -> tuple[str, str, str]:
    """Get project details from user."""
    project_name = input("Enter project name: ").strip()
    description = input("Enter description [empty]: ").strip() or ""

    default_python_version = "3.11"
    python_version = (
        input(f"Enter Python version (e.g., 3.12) [{default_python_version}]: ").strip()
        or default_python_version
    )
    return project_name, description, python_version


def replace_variables(project_name: str, description: str, python_version: str) -> None:
    """Replace $_$VARIABLE$_$ placeholders in all files."""
    replacements = {
        "$_$PROJECT_NAME$_$": project_name,
        "$_$DESCRIPTION$_$": description,
        "$_$PYTHON_VERSION$_$": python_version,
        "$_$PYTHON_VERSION_MODIFIED$_$": f"py{python_version.replace('.', '')}",
    }

    for root, dirs, files in os.walk("."):
        # Skip .venv and other directories if needed.
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        for file in files:
            # Skip the script itself.
            if file == Path(__file__).name:
                continue

            path = Path(root) / file
            try:
                content = path.read_text(encoding="utf-8")
                new_content = content
                for var, val in replacements.items():
                    new_content = new_content.replace(var, val)
                if new_content != content:
                    path.write_text(new_content, encoding="utf-8")
                    print(f"Updated {path}")
            except (UnicodeDecodeError, OSError):
                # Skip binary files or files that cannot be read.
                pass


def initialise_github_repository(project_name: str) -> None:
    """Initialize a local Git repository and create a remote GitHub repository."""
    try:
        # Check if git is installed
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Git is not installed. Please install Git to initialize the repository.")
        return

    # Check if gh (GitHub CLI) is installed.
    try:
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "GitHub CLI (gh) is not installed. Please install it from: https://cli.github.com/"
        )
        return

    # Check if authenticated with GitHub.
    try:
        subprocess.run(["gh", "auth", "status"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print(
            "You are not authenticated with GitHub. Please run 'gh auth login' first."
        )
        return

    # Check if already a git repository.
    if Path(".git").exists():
        print("Git repository already initialized.")
        # Check if there are commits.
        try:
            subprocess.run(
                ["git", "log", "--oneline", "-1"], check=True, capture_output=True
            )
            has_commits = True
        except subprocess.CalledProcessError:
            has_commits = False
    else:
        # Initialize git repository.
        subprocess.run(["git", "init"], check=True)
        print("Initialized empty Git repository.")
        has_commits = False

    if not has_commits:
        # Add all files.
        subprocess.run(["git", "add", "."], check=True)
        print("Added files to staging area.")

        # Commit.
        try:
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
            print("Created initial commit.")
        except subprocess.CalledProcessError:
            print("No changes to commit or commit failed.")
            return  # Don't create repo if no commit.

    # Ask for repository visibility
    visibility = input("Make the repository public? (y/n) [y]: ").strip().lower()
    visibility_flag = "--public" if visibility in ("", "y", "yes") else "--private"

    # Create a GitHub repository.
    try:
        subprocess.run(
            [
                "gh",
                "repo",
                "create",
                project_name,
                visibility_flag,
                "--source=.",
                "--push",
            ],
            check=True,
        )
        print(f"Created and pushed to GitHub repository: {project_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create GitHub repository: {e}")
        return


def main() -> None:
    """Run the main setup process."""
    check_uv_installed()
    project_name, description, python_version = get_user_input()
    replace_variables(project_name, description, python_version)

    # Remove the script itself.
    Path(__file__).unlink()

    initialise_github_repository(project_name)

    print("The setup script has been removed.")
    print("Project initialized successfully.")


if __name__ == "__main__":
    main()
