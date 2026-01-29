# Database & Migrations

## ORM: SQLModel

We use **SQLModel** (which combines Pydantic and SQLAlchemy) for database interactions.

- **Models**: Defined in `src/models/`.
- **Async Support**: All database operations use `async`/`await`.

## Migrations: Alembic

Database schema changes are managed by **Alembic**.

### Initial Setup

When starting a new project from this boilerplate, you must generate the first migration **after defining your models**:

```sh
uv run alembic -c db/alembic.ini revision --autogenerate -m "chore: init"
uv run alembic -c db/alembic.ini upgrade head
```

### Common Commands

**Create a new migration** (after changing models):

```sh
uv run alembic -c db/alembic.ini revision --autogenerate -m "description_of_changes"
```

**Apply migrations**:

```sh
uv run alembic -c db/alembic.ini upgrade head
```

**Revert last migration**:

```sh
uv run alembic -c db/alembic.ini downgrade -1
```

## Repositories

Always access the database through Repositories. Do not use the raw session in Routers or Services if possible.

### Example Repository Methods

**Reading Data:**

```python
async def get_user(self, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    result = await self.session.exec(statement)
    return result.first()
```

**Creating Data (Standard Way):**

```python
async def create(self, sample: SampleCreate) -> Sample:
    data = Sample.model_validate(sample)
    result = (
        await self.db.scalars(
            insert(Sample).values(data.model_dump()).returning(Sample),
        )
    ).one()
    await self.db.commit()
    return result
```
