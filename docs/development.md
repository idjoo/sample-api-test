# Development Workflow

## Dependency Management

This project uses `uv` for fast and reliable dependency management.

- **Add a dependency**: `uv add <package>`
- **Add a dev dependency**: `uv add --dev <package>`
- **Sync environment**: `uv sync`

## Linting & Formatting

We use **Ruff** for both linting and formatting.

- **Check code**: `uv run ruff check .`
- **Fix issues**: `uv run ruff check --fix .`
- **Format code**: `uv run ruff format .`

## Testing

Tests are powered by **pytest**.

- **Run all tests**: `uv run pytest`
- **Run with coverage**: `uv run pytest --cov=src`

## Pre-commit Hooks

Ensure code quality before committing.

1.  Install hooks:
    ```sh
    uv run pre-commit install
    ```
2.  Run manually:
    ```sh
    uv run pre-commit run --all-files
    ```

## Coding Standards

### Import Rules

To maintain a clean and decoupled structure, adhere to the following import rules:

1.  **Import from Parent Package**: When importing a component from another package, import it from the package root (`__init__.py`) rather than the specific module file.
    -   **Correct**: `from src.dependencies import Config`
    -   **Incorrect**: `from src.dependencies.config import Config`

2.  **Explicit Exports in `__init__.py`**: All `__init__.py` files must explicitly export public symbols using redundant aliases. This avoids the implicit behavior of `__all__` and makes refactoring safer.
    -   **Pattern**: `from .module import Class as Class`
    -   **Avoid**: `__all__ = ["Class"]`

3.  **Internal Package Imports**: Within the same package (e.g., inside `src/dependencies`), use relative imports to avoid circular dependencies and maintain clarity.
    -   **Correct**: `from .config import Config`