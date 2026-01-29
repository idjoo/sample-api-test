# Getting Started

## Prerequisites

Ensure you have the following installed:

- **Python 3.13+** (Required)
- **Docker** & **Docker Compose** (for containerization and local DB)
- **uv** (Required for dependency management)

## Installation

1.  **Clone the repository:**

    ```sh
    git clone <your-repo-url>
    cd <repo-name>
    ```

2.  **Configure Environment:**

    The application uses a flexible configuration system. You can set configuration via:
    - `config.yaml` (default)
    - Environment variables
    - `.env` file

    Copy the example configuration:

    ```sh
    cp config.example.yaml config.yaml
    ```

    Modify `config.yaml` in the project root to set your service name and database credentials if needed.

3.  **Install Dependencies:**

    Install dependencies using [uv](https://github.com/astral-sh/uv):

    ```sh
    uv sync
    ```

## Running Locally

1.  **Start Infrastructure (Database):**

    Use Docker Compose to spin up the local PostgreSQL database (defined in `docker-compose.yml`):

    ```sh
    docker-compose up -d
    ```

2.  **Initialize Database (Important):**

    Since this is a boilerplate, you need to generate the initial migration to create the tables for your models:

    ```sh
    # Generate the first migration file based on the models
    uv run alembic -c db/alembic.ini revision --autogenerate -m "chore: init"

    # Apply the migration to the database
    uv run alembic -c db/alembic.ini upgrade head
    ```

3.  **Run the Application:**

    Start the server using `uv`:

    ```sh
    uv run app
    ```

    The server will start at `http://0.0.0.0:8080`.

4.  **Access Documentation:**
    - Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)
    - Redoc: [http://localhost:8080/redoc](http://localhost:8080/redoc)

    _Note: API documentation is enabled by default in `local` and `dev` environments._
