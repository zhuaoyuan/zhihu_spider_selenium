#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
  echo "未找到虚拟环境 python: $PYTHON_BIN"
  exit 1
fi

usage() {
  cat <<'EOF'
用法:
  ./run.sh login
  ./run.sh check
  ./run.sh update-data [--output-dir DIR]
  ./run.sh user <username> <contents...> [--time-begin "YYYY-MM-DD HH:MM:SS"] [--output-dir DIR]
  ./run.sh column <column_id> [--time-begin "YYYY-MM-DD HH:MM:SS"] [--output-dir DIR]

示例:
  ./run.sh login
  ./run.sh check
  ./run.sh update-data
  ./run.sh user xi-bi-tang posts answers
  ./run.sh user xi-bi-tang pins --time-begin "2026-01-01 00:00:00"
  ./run.sh column c_1494255546366226432
EOF
}

cmd="${1:-}"
case "$cmd" in
  login)
    "$PYTHON_BIN" crawler.py login
    ;;
  check)
    "$PYTHON_BIN" crawler.py check-cookie
    ;;
  update-data)
    shift
    "$PYTHON_BIN" crawler.py update-data "$@"
    ;;
  user)
    shift
    if [ "$#" -lt 2 ]; then
      usage
      exit 1
    fi
    username="$1"
    shift

    contents=()
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --*)
          break
          ;;
        *)
          contents+=("$1")
          shift
          ;;
      esac
    done

    if [ "${#contents[@]}" -eq 0 ]; then
      echo "缺少 contents（可选: pins posts answers）"
      exit 1
    fi

    "$PYTHON_BIN" crawler.py crawl --user "$username" --contents "${contents[@]}" "$@"
    ;;
  column)
    shift
    if [ "$#" -lt 1 ]; then
      usage
      exit 1
    fi
    column_id="$1"
    shift
    "$PYTHON_BIN" crawler.py crawl --column-id "$column_id" "$@"
    ;;
  *)
    usage
    exit 1
    ;;
esac
