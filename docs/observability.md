# Observability

The boilerplate comes with production-grade observability built-in, designed for Google Cloud Platform (GCP) but adaptable to other providers.

## Logging

We use **Structured Logging** (`google-cloud-logging`) to output logs in JSON format. This allows for powerful querying and filtering in log management systems.

### Usage

Inject the logger into your components:

```python
from src.dependencies import Logger

@router.get("/")
async def root(logger: Logger):
    logger.info("Handling root request", extra={"user_id": 123})
```

## Tracing

**OpenTelemetry** is integrated for distributed tracing. By default, it uses the GCP Trace exporter.

### Automatic Instrumentation

We provide a custom `@observe` decorator (`src.dependencies.tracer.observe`) to automatically trace functions.

```python
from src.dependencies import observe, track

@observe
async def complex_calculation(data):
    # This execution will be visible in the trace timeline
    ...
```

### Manual Spans

For finer control, you can use the `track` context manager:

```python


async def process():
    async with track("processing_step"):
        # custom span logic
        ...
```
