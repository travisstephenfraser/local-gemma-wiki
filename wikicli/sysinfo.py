"""Facts about the machine and runtime that go into every evidence record."""

from __future__ import annotations

import json
import platform
import re
import shutil
import socket
import subprocess
from pathlib import Path

LMS = shutil.which("lms") or str(Path.home() / ".lmstudio/bin/lms")


def network_online(timeout: float = 1.0) -> bool:
    """True if a public DNS server is reachable. Recorded, never required."""
    for host in ("1.1.1.1", "8.8.8.8"):
        try:
            socket.create_connection((host, 53), timeout=timeout).close()
            return True
        except OSError:
            continue
    return False


def _run(cmd: list[str], timeout: int = 20) -> str:
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def device() -> dict:
    mem = _run(["sysctl", "-n", "hw.memsize"]).strip()
    return {
        "os": f"macOS {platform.mac_ver()[0]}"
        if platform.system() == "Darwin"
        else platform.platform(),
        "chip": _run(["sysctl", "-n", "machdep.cpu.brand_string"]).strip()
        or platform.processor(),
        "unified_memory_gb": round(int(mem) / 2**30) if mem.isdigit() else None,
        "python": platform.python_version(),
    }


def lms_version() -> str:
    out = _run([LMS, "version"])
    m = re.search(r"(?:CLI commit|version)[:\s]+(\S+)", out, re.I)
    return m.group(1) if m else "unknown"


def loaded_models() -> list[dict]:
    try:
        return json.loads(_run([LMS, "ps", "--json"]) or "[]")
    except json.JSONDecodeError:
        return []


def model_info(model_key: str) -> dict:
    for m in loaded_models():
        if m.get("identifier") == model_key or m.get("modelKey") == model_key:
            return {
                "model": m.get("modelKey"),
                "format": m.get("format"),
                "quantization": (m.get("quantization") or {}).get("name"),
                "weights_gb": round(m.get("sizeBytes", 0) / 1e9, 2),
                "context_length": m.get("contextLength"),
            }
    return {"model": model_key, "loaded": False}


def lmstudio_footprint_gb() -> float | None:
    """Physical memory footprint of all LM Studio processes (includes MLX/Metal allocations)."""
    pids = [
        p
        for p in _run(["pgrep", "-f", "LM Studio|lmstudio|llmworker"]).split()
        if p.isdigit()
    ]
    total = 0
    for pid in pids:
        out = _run(["footprint", "-p", pid], timeout=30)
        m = re.search(r"Footprint:\s*([\d.]+)\s*([KMG])B", out)
        if m:
            total += (
                float(m.group(1)) * {"K": 1 / 2**20, "M": 1 / 2**10, "G": 1}[m.group(2)]
            )
    return round(total, 2) if pids else None


def load_model(model_key: str, context_length: int) -> None:
    """Load exactly one chat model so memory numbers belong to it."""
    for m in loaded_models():
        if m.get("type") == "llm" and m.get("identifier") != model_key:
            _run([LMS, "unload", m["identifier"]], timeout=60)
    if not any(m.get("identifier") == model_key for m in loaded_models()):
        _run(
            [LMS, "load", model_key, "--context-length", str(context_length), "-y"],
            timeout=600,
        )
