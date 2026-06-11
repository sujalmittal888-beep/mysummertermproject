"""Ollama management endpoints — list models, pull new ones."""
from __future__ import annotations

import shutil
import subprocess
import threading
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/ollama", tags=["ollama"])

_jobs: dict[str, dict[str, Any]] = {}

# Windows: Ollama installs to AppData\Local\Programs\Ollama and is NOT always on PATH
# when the server process was started from a terminal that predates the install.
_FALLBACK_PATHS = [
    Path.home() / "AppData/Local/Programs/Ollama/ollama.exe",
    Path("C:/Program Files/Ollama/ollama.exe"),
]


def _ollama_exe() -> str:
    """Return the ollama executable path, raising a clear error if not found."""
    found = shutil.which("ollama")
    if found:
        return found
    for p in _FALLBACK_PATHS:
        if p.exists():
            return str(p)
    raise FileNotFoundError(
        "Ollama not found. Download from https://ollama.com/download"
    )


def _run_ollama(*args: str, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_ollama_exe(), *args],
        capture_output=True, text=True, timeout=timeout,
    )


class PullRequest(BaseModel):
    model: str


@router.get("/models", summary="List locally installed Ollama models")
def list_models() -> dict:
    try:
        r = _run_ollama("list")
        if r.returncode != 0:
            return {"models": [], "error": r.stderr.strip() or "ollama list failed"}
        lines = r.stdout.strip().splitlines()
        models = []
        for line in lines[1:]:  # skip header row
            parts = line.split()
            if parts:
                models.append({
                    "name": parts[0],
                    "id":   parts[1] if len(parts) > 1 else "",
                    "size": parts[2] if len(parts) > 2 else "",
                })
        return {"models": models}
    except FileNotFoundError as exc:
        return {"models": [], "error": str(exc)}
    except subprocess.TimeoutExpired:
        return {"models": [], "error": "ollama list timed out"}


@router.post("/pull", summary="Pull an Ollama model (non-blocking, returns job_id)")
def pull_model(req: PullRequest) -> dict:
    model = req.model.strip()
    if not model:
        raise HTTPException(422, "model name is required")

    # resolve exe path eagerly so we can surface a clear error before spawning
    try:
        exe = _ollama_exe()
    except FileNotFoundError as exc:
        raise HTTPException(400, str(exc)) from exc

    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status": "starting", "lines": [], "done": False, "error": None}

    def _run() -> None:
        try:
            proc = subprocess.Popen(
                [exe, "pull", model],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            _jobs[job_id]["status"] = "pulling"
            for line in proc.stdout:  # type: ignore[union-attr]
                line = line.rstrip()
                if line:
                    _jobs[job_id]["lines"].append(line)
                    _jobs[job_id]["status"] = line
            proc.wait()
            if proc.returncode == 0:
                _jobs[job_id]["done"] = True
                _jobs[job_id]["status"] = "done"
            else:
                last = _jobs[job_id]["lines"][-1] if _jobs[job_id]["lines"] else ""
                _jobs[job_id]["error"] = last or f"pull failed (exit {proc.returncode})"
                _jobs[job_id]["done"] = True
        except Exception as exc:
            _jobs[job_id]["error"] = str(exc)
            _jobs[job_id]["done"] = True

    threading.Thread(target=_run, daemon=True).start()
    return {"job_id": job_id}


@router.get("/pull/{job_id}", summary="Poll a pull job for progress")
def pull_status(job_id: str) -> dict:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    return job
