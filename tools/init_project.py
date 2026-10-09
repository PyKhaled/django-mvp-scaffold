"""Personalize a fresh scaffold checkout using only the Python standard library."""

import argparse
import ast
import json
import keyword
import re
import secrets
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def initialize(root, name, package, repository, dry_run=False):
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", name):
        raise ValueError("Project name must be a lowercase slug, such as my-project.")
    if (not re.fullmatch(r"[a-z][a-z0-9_]*", package)
            or keyword.iskeyword(package) or package in sys.stdlib_module_names):
        raise ValueError("Package must be a lowercase Python identifier, not a reserved name.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Repository must have the form owner/repository.")
    if (root / ".scaffold-init.json").exists() or (root / ".env").exists():
        raise ValueError("Already initialized or .env exists; use a fresh template checkout.")
    if not (root / "product/settings/common.py").is_file():
        raise ValueError("Original product package is missing.")
    if package != "product" and (root / package).exists():
        raise ValueError(f"Destination {package} already exists.")
    paths = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=root
    ).decode().split("\0")
    changes = {}
    display_name = name.replace("-", " ").title()
    for relative in filter(None, paths):
        path = root / relative
        if path.is_symlink():
            raise ValueError(f"Refusing tracked symlink: {relative}")
        if (relative.startswith(("tools/", ".github/"))
                or relative in {"CHANGELOG.md", "THIRD_PARTY_NOTICES.md"}
                or path.suffix not in {".py", ".md", ".toml", ".yml", ".html", ".sh"}
                and relative not in {"Dockerfile", ".env.example"}):
            continue
        old = path.read_text()
        new = old.replace("PyKhaled/django-mvp-scaffold", repository)
        new = new.replace("django-mvp-scaffold", name)
        new = new.replace("Django MVP Scaffold", display_name)
        # Module paths and filesystem paths, without changing words like production.
        new = re.sub(r"\bproduct(?=[./])", package, new)
        if relative in {"Dockerfile", ".env.example"} or path.suffix == ".py":
            new = re.sub(r"\bproduct\b", package, new)
        if path.suffix == ".py":
            ast.parse(new, filename=relative)
        if relative == "pyproject.toml":
            tomllib.loads(new)
        if new != old:
            changes[path] = new
    env = changes.get(root / ".env.example", (root / ".env.example").read_text())
    env = env.replace("SECRET_KEY=\n", f"SECRET_KEY='{secrets.token_urlsafe(48)}'\n", 1)
    env = env.replace(f'# SITE_NAME="{display_name}"', f'SITE_NAME="{display_name}"')
    print(f"Initialize {name}: package {package}, repository {repository}")
    print(f"Update {len(changes)} files; create private .env and initialization record.")
    if dry_run:
        return
    # Exclusive creation ensures existing credentials cannot be overwritten.
    import os

    descriptor = os.open(root / ".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(env)
    for path, content in changes.items():
        path.write_text(content)
    if package != "product":
        (root / "product").rename(root / package)
    (root / ".scaffold-init.json").write_text(json.dumps(
        {"project": name, "package": package, "repository": repository}, indent=2
    ) + "\n")
    print("Initialized. Run make config-check after installing development dependencies.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", help="Project slug, e.g. my-project")
    parser.add_argument("--package", help="Django package, e.g. my_project")
    parser.add_argument("--repository", help="GitHub owner/repository")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        name = args.name or input("Project name (my-project): ").strip()
        package = args.package or input(f"Python package [{name.replace('-', '_')}]: ").strip()
        package = package or name.replace("-", "_")
        repository = args.repository or input("GitHub repository (owner/repository): ").strip()
        initialize(ROOT, name, package, repository, args.dry_run)
    except (ValueError, EOFError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Initialization failed: {exc}\n")


if __name__ == "__main__":
    main()
