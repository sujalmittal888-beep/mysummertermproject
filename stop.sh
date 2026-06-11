#!/usr/bin/env bash
# TaskFlow — stop all services (WSL / Linux)
PIDS_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.pids"

if [ -f "$PIDS_FILE" ]; then
  while read -r pid; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid"
      echo "Stopped PID $pid"
    fi
  done < "$PIDS_FILE"
  rm "$PIDS_FILE"
else
  # fallback: kill by port
  for port in 8000 8501; do
    pid=$(lsof -ti tcp:"$port" 2>/dev/null)
    if [ -n "$pid" ]; then
      kill "$pid" && echo "Stopped process on port $port (PID $pid)"
    fi
  done
fi

echo "All TaskFlow services stopped."
