"""The same shape on the real OpenTelemetry SDK (illustration, compile-checked only).

Needs `pip install opentelemetry-sdk`; not a test dependency. Pin the version you
build against: the GenAI semantic conventions are still in Development.
"""
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# --8<-- [start:telemetry-otel]
provider = TracerProvider()
# Batch export, so telemetry never blocks the agent loop.
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
tracer = provider.get_tracer("listing-studio")

with tracer.start_as_current_span("invoke_agent listing-studio") as root:
    root.set_attribute("gen_ai.operation.name", "invoke_agent")
    with tracer.start_as_current_span("chat claude-sonnet-5-5") as chat:
        chat.set_attribute("gen_ai.operation.name", "chat")
        chat.set_attribute("gen_ai.provider.name", "anthropic")
        chat.set_attribute("gen_ai.usage.input_tokens", 412)
        chat.set_attribute("gen_ai.usage.output_tokens", 96)
        # No gen_ai.input.messages here: content stays off unless you opt in.
# --8<-- [end:telemetry-otel]
