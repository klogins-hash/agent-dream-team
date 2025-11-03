"""Distributed tracing with Jaeger."""

import os
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor


def setup_tracing(app, service_name="agent-dream-team"):
    """Setup distributed tracing with Jaeger.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service for tracing
    """
    # Create Jaeger exporter
    jaeger_host = os.getenv("JAEGER_HOST", "localhost")
    jaeger_port = int(os.getenv("JAEGER_PORT", "6831"))
    
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    
    # Create tracer provider
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })
    
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(processor)
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument other libraries
    RequestsInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    RedisInstrumentor().instrument()
    
    return trace.get_tracer(__name__)


def trace_agent_execution(tracer, agent_name: str, task: str):
    """Create a span for agent execution.
    
    Args:
        tracer: OpenTelemetry tracer
        agent_name: Name of the agent
        task: Task description
        
    Returns:
        Span context manager
    """
    return tracer.start_as_current_span(
        f"agent.{agent_name}.execute",
        attributes={
            "agent.name": agent_name,
            "task.description": task
        }
    )


def trace_tool_execution(tracer, tool_name: str, **kwargs):
    """Create a span for tool execution.
    
    Args:
        tracer: OpenTelemetry tracer
        tool_name: Name of the tool
        **kwargs: Tool parameters
        
    Returns:
        Span context manager
    """
    return tracer.start_as_current_span(
        f"tool.{tool_name}",
        attributes={
            "tool.name": tool_name,
            **{f"tool.param.{k}": str(v) for k, v in kwargs.items()}
        }
    )


def trace_database_query(tracer, operation: str, table: str):
    """Create a span for database operations.
    
    Args:
        tracer: OpenTelemetry tracer
        operation: Database operation (SELECT, INSERT, etc.)
        table: Table name
        
    Returns:
        Span context manager
    """
    return tracer.start_as_current_span(
        f"db.{operation}",
        attributes={
            "db.operation": operation,
            "db.table": table
        }
    )
