# FastAPI Production Boilerplate

A scalable, production-ready FastAPI backend boilerplate designed for high performance, maintainability, and developer experience.

## 🚀 Key Features

- **FastAPI** & **SQLModel**: Modern, async, type-safe Python web framework and ORM.
- **Clean Architecture**: Modular structure separating Routers, Services, Repositories, and Models.
- **Observability**: Built-in **Google Cloud Logging** and **OpenTelemetry** tracing.
- **Production Ready**: Docker, Cloud Build config, and structured logging.
- **Developer Experience**:
  - **uv** for fast dependency management.
  - **ruff** for linting/formatting.
  - **pre-commit** hooks.
- **Configuration**: Type-safe settings using `pydantic-settings` (YAML/Env/JSON).

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [**Getting Started**](docs/getting_started.md): Setup, installation, and running locally.
- [**Architecture**](docs/architecture.md): Understanding the folder structure and design patterns.
- [**Configuration**](docs/configuration.md): Managing settings and environments.
- [**Database & Migrations**](docs/database.md): Working with SQLModel and Alembic.
- [**Observability**](docs/observability.md): Logging and Tracing guide.
- [**Development**](docs/development.md): Testing, linting, and workflow.
- [**Deployment**](docs/deployment.md): Docker and Cloud Build instructions.

## ⚡ Quick Start

1.  **Clone & Install**

    ```sh
    git clone <repo-url>
    cd <repo-name>
    uv sync
    ```

2.  **Configure**

    ```sh
    cp config.example.yaml config.yaml
    ```

3.  **Run Database**

    ```sh
    docker-compose up -d
    ```

4.  **Generate Initial Migration**

    ```sh
    uv run alembic -c db/alembic.ini revision --autogenerate -m "chore: init"
    ```

5.  **Start Server**
    ```sh
    uv run app
    ```
    Visit [http://localhost:8080/docs](http://localhost:8080/docs) for API docs.

## 📄 License

MIT
