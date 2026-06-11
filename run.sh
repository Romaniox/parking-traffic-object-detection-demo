#!/usr/bin/env bash
#
# Запуск всего сервиса локально: backend (FastAPI/uvicorn) + frontend (Vite dev).
# Frontend проксирует /detect и /results на backend (см. frontend/vite.config.ts).
#
# Использование:
#   ./run.sh                 # поднять backend и frontend
#   BACKEND_PORT=9000 ./run.sh
#
# Переменные окружения (с значениями по умолчанию):
#   BACKEND_PORT  (8000)   порт backend
#   FRONTEND_PORT (5173)   порт frontend (Vite)
#   DATA_DIR      (backend/data)  корень данных: models/, images/, db/
#   MODEL_NAME    (yolo)  детектор: stub | yolo
#   MODEL_WEIGHTS (data/models/yolo26l.pt)  путь к весам
#
set -euo pipefail

# Каталог проекта = каталог, где лежит этот скрипт.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
export DATA_DIR="${DATA_DIR:-$ROOT/backend/data}"
export MODEL_NAME="${MODEL_NAME:-yolo}"
export MODEL_WEIGHTS="${MODEL_WEIGHTS:-$DATA_DIR/models/yolo26l.pt}"

VENV_PY="$ROOT/.venv/bin/python"

log()  { printf '\033[1;36m[run]\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m[run]\033[0m %s\n' "$*" >&2; }

# --- проверки окружения ---------------------------------------------------
if [[ ! -x "$VENV_PY" ]]; then
  err "Не найден Python-venv: $VENV_PY"
  err "Создайте окружение, например: uv venv && uv pip install -r backend/requirements.txt"
  exit 1
fi

if ! "$VENV_PY" -c "import fastapi" >/dev/null 2>&1; then
  log "Устанавливаю backend-зависимости..."
  ( cd backend && uv pip install -r requirements.txt )
fi

if [[ ! -d frontend/node_modules ]]; then
  log "Устанавливаю frontend-зависимости..."
  ( cd frontend && npm install )
fi

mkdir -p "$DATA_DIR/images" "$DATA_DIR/models" "$DATA_DIR/db"

# --- запуск и аккуратная остановка ----------------------------------------
# Каждый сервис запускаем в собственной группе процессов (setsid), чтобы при
# остановке убить всё дерево (npm → vite → node), а не только родителя.
PGIDS=()

cleanup() {
  log "Останавливаю сервисы..."
  for pgid in "${PGIDS[@]}"; do
    kill -TERM -- "-$pgid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  log "Остановлено."
}
trap cleanup INT TERM EXIT

log "Backend  → http://localhost:$BACKEND_PORT  (docs: /docs)"
setsid bash -c "cd '$ROOT/backend' && exec '$VENV_PY' -m uvicorn app.main:app --host 0.0.0.0 --port '$BACKEND_PORT'" &
PGIDS+=($!)

log "Frontend → http://localhost:$FRONTEND_PORT"
setsid bash -c "cd '$ROOT/frontend' && exec npm run dev -- --port '$FRONTEND_PORT' --strictPort" &
PGIDS+=($!)

log "Данные: $DATA_DIR | модель: $MODEL_NAME"
log "Откройте http://localhost:$FRONTEND_PORT — нажмите Ctrl+C для остановки."

# Если любой из процессов упадёт — выходим (trap остановит второй).
wait -n
