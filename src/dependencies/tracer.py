import inspect
from collections.abc import Callable, Iterator
from contextlib import asynccontextmanager, contextmanager

import wrapt
from opentelemetry import trace
from opentelemetry.sdk.resources import Attributes, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import Span
from opentelemetry.trace.status import StatusCode

from .config import Config, aget_config, get_config


async def init():
    config: Config = await aget_config()

    tracer_provider = TracerProvider(
        resource=Resource.create({"service.name": config.service}),
    )

    trace.set_tracer_provider(tracer_provider)


@asynccontextmanager
async def track(
    name: str,
    attributes: Attributes | None = None,
) -> Iterator[Span]:
    config: Config = await aget_config()
    tracer = trace.get_tracer(config.service)

    with tracer.start_as_current_span(
        name,
        kind=SpanKind.INTERNAL,
        record_exception=True,
        set_status_on_exception=True,
        end_on_exit=True,
        attributes=attributes,
    ) as span:
        yield span
        span.set_status(StatusCode.OK)


@contextmanager
def create_span(func: Callable):
    config: Config = get_config()
    tracer = trace.get_tracer(config.service)

    with tracer.start_as_current_span(
        func.__qualname__,
        kind=SpanKind.INTERNAL,
        record_exception=True,
        set_status_on_exception=True,
        end_on_exit=True,
    ) as span:
        span.set_attribute(SpanAttributes.CODE_FUNCTION, func.__qualname__)
        span.set_attribute(SpanAttributes.CODE_NAMESPACE, func.__module__)
        span.set_attribute(SpanAttributes.CODE_FILEPATH, inspect.getfile(func))
        yield span
        span.set_status(StatusCode.OK)


@wrapt.decorator
def _observe(wrapped, instance, args, kwargs):
    if inspect.iscoroutinefunction(wrapped):

        async def _awrapper():
            with create_span(wrapped):
                return await wrapped(*args, **kwargs)

        return _awrapper()
    else:
        with create_span(wrapped):
            return wrapped(*args, **kwargs)


def observe(wrapped=None):
    if wrapped is None:
        return _observe
    return _observe(wrapped)


__all__ = ["observe", "track"]
