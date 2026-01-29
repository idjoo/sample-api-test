# Configuration

The project uses `pydantic-settings` to manage configuration, supporting multiple sources and environments.

## Configuration Sources

Configuration is loaded in the following order of precedence (highest to lowest):

1.  Environment Variables
2.  `.env` file
3.  `config.yaml` (copied from `config.example.yaml`)
4.  `config.json`
5.  `config.toml`
6.  Default values in code

## `config.yaml`

The primary configuration file. Start by copying the example:

```bash
cp config.example.yaml config.yaml
```

Example structure:

```yaml
service: "my-service"
environment: "local" # local, dev, prd
port: 8080

logging:
  level: "info" # debug, info, warning, error

database:
  url: "postgresql+psycopg://user:pass@localhost:5432/db"
  # Or breakdown:
  username: "user"
  password: "password"
  host: "localhost"
  port: 5432
  name: "db"
```

## Environment Variables

You can override any setting using environment variables. The delimiter is `__` (double underscore).

- `service` -> `SERVICE`
- `logging.level` -> `LOGGING__LEVEL`
- `database.host` -> `DATABASE__HOST`

## Environments

The `Environment` enum (`src/dependencies/config.py`) controls behavior:

- `local`: Reload enabled, Docs enabled.
- `dev`: Docs enabled.
- `prd`: Docs disabled, optimizations enabled.
