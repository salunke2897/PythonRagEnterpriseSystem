import time
from collections import defaultdict


class MetricsCollector:
    """Simple in-memory metrics collector for latency and token usage."""

    def __init__(self) -> None:
        self.timings: dict[str, list[float]] = defaultdict(list)
        self.counters: dict[str, int] = defaultdict(int)

    def observe(self, metric_name: str, value: float) -> None:
        self.timings[metric_name].append(value)

    def increment(self, metric_name: str, value: int = 1) -> None:
        self.counters[metric_name] += value

    def timer(self, metric_name: str):
        start = time.perf_counter()

        def _stop() -> None:
            self.observe(metric_name, time.perf_counter() - start)

        return _stop

    def snapshot(self) -> dict:
        return {
            "timings": {k: {"count": len(v), "avg": (sum(v) / len(v)) if v else 0} for k, v in self.timings.items()},
            "counters": dict(self.counters),
        }
