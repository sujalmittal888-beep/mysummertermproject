#!/usr/bin/env bash
# TaskFlow — start all services (WSL / Linux)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.wslvenv"
PIDS_FILE="$SCRIPT_DIR/.pids"
export PYTHONPATH="$SCRIPT_DIR/src"

if [ ! -f "$VENV/bin/python" ]; then
  echo "WSL venv not found. Run setup first:"
  echo "  python3 -m venv .wslvenv --without-pip"
  echo "  curl -sS https://bootstrap.pypa.io/get-pip.py | .wslvenv/bin/python3"
  echo "  .wslvenv/bin/pip install -e ."
  echo "  .wslvenv/bin/pip install streamlit"
  exit 1
fi

cd "$SCRIPT_DIR"

echo "Starting FastAPI backend on http://localhost:8000 ..."
"$VENV/bin/uvicorn" taskflow.presentation.api.app:create_app \
  --factory --host 0.0.0.0 --port 8000 --reload \
  > /tmp/taskflow-api.log 2>&1 &
echo $! > "$PIDS_FILE"

# wait for backend to be ready
echo -n "  Waiting for API..."
for i in $(seq 1 15); do
  sleep 1
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo " ready."
    break
  fi
  echo -n "."
done

echo "Starting Streamlit UI on http://localhost:8501 ..."
"$VENV/bin/streamlit" run ui.py \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false \
  > /tmp/taskflow-ui.log 2>&1 &
echo $! >> "$PIDS_FILE"

echo -n "  Waiting for UI..."
for i in $(seq 1 15); do
  sleep 1
  if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo " ready."
    break
  fi
  echo -n "."
done

# get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "  UI   → http://localhost:8501"
echo "  API  → http://localhost:8000/docs"
echo "  Network → http://${LOCAL_IP}:8501"
echo ""
echo "Logs: tail -f /tmp/taskflow-api.log /tmp/taskflow-ui.log"
echo "Stop: ./stop.sh"
