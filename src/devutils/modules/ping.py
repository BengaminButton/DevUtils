
from __future__ import annotations
import time
import requests
from statistics import mean


def http_ping(url: str, count: int = 4, timeout: float = 3.0) -> dict:
    samples = []
    for _ in range(count):
        t0 = time.perf_counter()
        ok = False
        status = None
        try:
            r = requests.get(url, timeout=timeout)
            status = r.status_code
            ok = r.ok
        except requests.RequestException:
            ok = False
        dt = (time.perf_counter() - t0) * 1000.0
        samples.append({"ok": ok, "status": status, "ms": dt})
    received = sum(1 for s in samples if s["ok"])
    ms_values = [s["ms"] for s in samples]
    stats = {
        "sent": count,
        "received": received,
        "loss": (count - received) / count if count else 0.0,
        "min_ms": min(ms_values) if ms_values else 0.0,
        "avg_ms": mean(ms_values) if ms_values else 0.0,
        "max_ms": max(ms_values) if ms_values else 0.0,
    }
    return {"samples": samples, "stats": stats}
