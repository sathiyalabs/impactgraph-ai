from pathlib import Path
import ast


def find_python_files(repository_path: str) -> list[Path]:
    """
    Find all Python files inside a repository.
    """
    root = Path(repository_path)

    if not root.exists():
        raise FileNotFoundError(
            f"Repository does not exist: {repository_path}"
        )

    return list(root.rglob("*.py"))


def extract_imports(file_path: Path) -> list[str]:
    """
    Extract imported modules from a Python file.
    """
    source = file_path.read_text(encoding="utf-8")

    tree = ast.parse(source)

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports