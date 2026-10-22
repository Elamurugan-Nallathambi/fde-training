#!/usr/bin/env bash
# FDE Training Program site: build.py writes public/index.html and learn.py the lesson pages from content/*.json.
# Served locally with python http.server; deployed to Cloudflare Pages.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="fde-training"
PORT="${PORT:-4321}"
PID_FILE="/tmp/${NAME}-dev.pid"
LOG_FILE="/tmp/${NAME}-dev.log"
# Deploy settings live in .env (never committed); see .env.example.
[[ -f "$ROOT/.env" ]] && { set -a; . "$ROOT/.env"; set +a; }
CF_PROJECT="${CF_PROJECT:-fde-training-program}"
CF_ACCOUNT_ID="${CF_ACCOUNT_ID:-}"

log()  { printf '\033[34m[%s]\033[0m %s\n' "$NAME" "$*"; }
ok()   { printf '\033[32m[ok]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m %s\n' "$*"; }
err()  { printf '\033[31m[error]\033[0m %s\n' "$*" >&2; }

prereqs() { for t in python3 curl lsof; do command -v "$t" >/dev/null || { err "missing prerequisite: $t"; exit 1; }; done; ok "prerequisites present"; }
is_running() { [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; }
check_port() { lsof -nP -iTCP:"$PORT" -sTCP:LISTEN -t 2>/dev/null || true; }
kill_port() {
  local pids; pids="$(check_port)"; [[ -z "$pids" ]] && return 0
  if ps -p "$pids" -o args= 2>/dev/null | grep -qF -- "$ROOT/public"; then kill $pids; sleep 0.5; ok "freed port $PORT"
  else err "port $PORT is used by another process ($pids). Set PORT to a free port."; exit 1; fi
}
build() { log "building"; python3 "$ROOT/build.py"; }
check() {
  local urls="/tmp/${NAME}-urls.txt"
  python3 "$ROOT/tools/check_content.py" "$urls"
  log "verifying links"; python3 "$ROOT/tools/verify_links.py" "$urls" | tee "/tmp/${NAME}-links.log"
  if grep -q '^NO' "/tmp/${NAME}-links.log"; then err "some links failed, see /tmp/${NAME}-links.log"; return 1; fi
  ok "content and links OK"
}
start() {
  if is_running; then ok "already running at http://127.0.0.1:$PORT/"; return 0; fi
  build; kill_port
  nohup python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT/public" >>"$LOG_FILE" 2>&1 &
  echo $! >"$PID_FILE"
  for _ in $(seq 1 30); do curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1 && { ok "serving http://127.0.0.1:$PORT/"; return 0; }; sleep 0.2; done
  err "server did not start, see $LOG_FILE"; return 1
}
stop() { if is_running; then kill "$(cat "$PID_FILE")" 2>/dev/null || true; ok "stopped"; else warn "not running"; fi; rm -f "$PID_FILE"; }
status() { if is_running; then ok "running at http://127.0.0.1:$PORT/"; else warn "not running"; fi; }
deploy() {
  [[ -n "$CF_ACCOUNT_ID" ]] || { err "set CF_ACCOUNT_ID in .env (see .env.example)"; exit 1; }
  build
  log "deploying public/ to Cloudflare Pages project $CF_PROJECT"
  (cd "$ROOT" && CLOUDFLARE_ACCOUNT_ID="$CF_ACCOUNT_ID" npx wrangler pages deploy public --project-name "$CF_PROJECT" --branch main --commit-dirty=true)
}
usage() {
  cat <<EOF
Usage: ./setup.sh <command>
  setup     check prerequisites, build and start (port $PORT)
  start     build and start the local server
  stop      stop the local server
  restart   stop then start
  status    server status
  logs      tail the server log
  build     rebuild the overview and lesson pages
  check     validate content/*.json and re-verify every lesson link
  deploy    build and deploy to Cloudflare Pages ($CF_PROJECT)
  help      this help
EOF
}
case "${1:-help}" in
  setup) prereqs; start ;;
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  logs) touch "$LOG_FILE"; tail -f "$LOG_FILE" ;;
  build) build ;;
  check) check ;;
  deploy) deploy ;;
  help|-h|--help) usage ;;
  *) err "unknown command: $1"; usage; exit 1 ;;
esac
