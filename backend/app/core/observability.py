import logging
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

logger = logging.getLogger(__name__)


def setup_observability(app: FastAPI) -> None:
    resource = Resource.create({'service.name': 'activia-trace'})
    provider = TracerProvider(resource=resource)

    otel_endpoint = os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')
    if otel_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )
            exporter = OTLPSpanExporter(endpoint=otel_endpoint)
        except ImportError:
            logger.warning(
                'OTLP endpoint set but exporter not installed; using console exporter'
            )
            exporter = ConsoleSpanExporter()
    else:
        exporter = ConsoleSpanExporter()

    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
