#!/usr/bin/env bash
# scripts/check.sh（機械のチェック）のテスト：よい例は通り、悪い例は落ちることを確かめる
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$ROOT/skills/setup/templates"
work="$(mktemp -d)"
trap 'rm -rf -- "$work"' EXIT

setup() {
  local d="$work/$1"
  mkdir -p "$d/scripts" && cd "$d" && git init -q
  cp "$T/practice/index.html" .
  cp "$T/repo/CLAUDE.md" .
  cp "$T/repo/scripts/check.sh" scripts/
}

fails=0
expect() { # expect <名前> <0|1>
  local out code
  out=$(bash scripts/check.sh 2>&1); code=$?
  if { [ "$2" = 0 ] && [ $code -eq 0 ]; } || { [ "$2" = 1 ] && [ $code -ne 0 ]; }; then
    echo "ok   $1"
  else
    echo "FAIL $1 (exit=$code)"; echo "$out" | sed 's/^/     /'; fails=1
  fi
}

setup good;    expect "練習用ページはそのまま通る" 0
setup secret;  echo 'token=sk-ant-api03-AAAAAAAAAAAAAAAAAAAAAAAAAAAA' > notes.txt; expect "鍵が書かれていたら落ちる" 1
setup json;    echo '{"a": 1,}' > data.json; expect "壊れた JSON は落ちる" 1
setup html;    printf '<html><head><title>x</title></head><body><img src="a.png"></body></html>\n' > index.html; expect "HTML の基本がなければ落ちる" 1
setup conflict; printf 'a\n<<<<<<< HEAD\nb\n=======\nc\n>>>>>>> other\n' > doc.md; expect "衝突の印が残っていたら落ちる" 1
setup heading; printf '見出し\n=======\n本文\n' > doc.md; expect "Markdown の見出し線は衝突の印とみなさない" 0
setup long;    for i in $(seq 1 160); do echo "line $i"; done >> CLAUDE.md; expect "長すぎる CLAUDE.md は落ちる" 1
setup local;   printf 'echo "独自チェック失敗"; exit 1\n' > scripts/check.local.sh; expect "独自のチェックが落ちたら落ちる" 1
setup policy;  mkdir -p .github/harness && cp "$T/repo/.github/harness/policy.json" .github/harness/; expect "テンプレートの policy.json は通る" 0

exit $fails
