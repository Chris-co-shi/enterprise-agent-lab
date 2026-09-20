from dataclasses import field, dataclass

from .sink import TraceSink


@dataclass
class TraceConfig:
    enabled: bool = True
    sinks: list[TraceSink] = field(default_factory=list)


_trace_config = TraceConfig()


def configure_trace(config: TraceConfig) -> None:
    global _trace_config
    _trace_config = config


def get_trace_config() -> TraceConfig:
    return _trace_config
