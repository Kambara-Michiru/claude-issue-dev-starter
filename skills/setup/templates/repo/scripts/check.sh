#!/usr/bin/env bash
# =====================================================================
# 機械のチェック（ハーネスの「センサー」）
#
# 機械で確かめられることは、AI の判断に頼らず、ここで毎回確かめます。
# Claude も作業の最後にこれを実行し、GitHub でも PR ごとに実行されます。
# 失敗したときは「何が悪いか」と「どう直すか」を書いて終わります。
#
# プロジェクト独自のチェックは scripts/check.local.sh に書いてください
# （このファイルから自動で呼ばれます）。
# =====================================================================
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

failed=0
pass() { printf '✅ %s\n' "$1"; }
fail() { failed=1; printf '❌ %s\n   → 直し方：%s\n' "$1" "$2"; }
skip() { printf '➖ %s\n' "$1"; }

# 調べる対象：Git が管理している（またはこれから管理する）ファイル。作業用の .harness-tmp は除く
mapfile -d '' FILES < <(git ls-files -z -co --exclude-standard -- . ':!:.harness-tmp/**' 2>/dev/null)

echo "== 機械のチェック =="

# 1. 鍵（パスワードや API キー）が書かれていないか
secret_re='(sk-ant-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'
hits=""
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  [ "$f" = "scripts/check.sh" ] && continue
  if grep -IqE "$secret_re" -- "$f" 2>/dev/null; then hits+="$f "; fi
done
if [ -n "$hits" ]; then
  fail "鍵のような文字列が入っています：$hits" "その行を消し、鍵は GitHub の Settings → Secrets にしまう。すでに push したなら、その鍵は無効にして作り直す"
else
  pass "鍵（API キーなど）が書かれていない"
fi

# 2. 大きすぎるファイルがないか（5MB まで）
big=""
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  size=$(wc -c < "$f" 2>/dev/null || echo 0)
  [ "$size" -gt 5242880 ] && big+="$f "
done
if [ -n "$big" ]; then
  fail "5MB を超えるファイルがあります：$big" "画像なら縮小する。動画や大きなデータは GitHub に置かず、別の場所に置いてリンクする"
else
  pass "大きすぎるファイルがない"
fi

# 3. 衝突のあと（<<<<<<< などの印）が残っていないか
conf=""
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  if grep -IqE '^(<<<<<<< |>>>>>>> )' -- "$f" 2>/dev/null; then conf+="$f "; fi
done
if [ -n "$conf" ]; then
  fail "変更の衝突の印が残っています：$conf" "<<<<<<< から >>>>>>> までを見て、残したいほうだけにする"
else
  pass "変更の衝突の印が残っていない"
fi

# 4. HTML の基本（文字コード、言語、タイトル、スマホ対応、画像の代わりの文章）
html_files=()
for f in "${FILES[@]}"; do case "$f" in *.html|*.htm) [ -f "$f" ] && html_files+=("$f");; esac; done
if [ ${#html_files[@]} -gt 0 ]; then
  if python3 - "${html_files[@]}" <<'PY'
import sys
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has = set(); self.noalt = 0; self.stack = []; self.errors = []
    VOID = {"area","base","br","col","embed","hr","img","input","link","meta","source","track","wbr"}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html" and a.get("lang"): self.has.add("lang")
        if tag == "meta" and (a.get("charset") or "").lower() == "utf-8": self.has.add("charset")
        if tag == "meta" and a.get("name") == "viewport": self.has.add("viewport")
        if tag == "title": self.has.add("title")
        if tag == "img" and "alt" not in a: self.noalt += 1
        if tag not in self.VOID: self.stack.append((tag, self.getpos()[0]))
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for t, line in self.stack[i+1:]:
                    if t not in ("p","li","td","tr","th","option","dt","dd"):
                        self.errors.append(f"<{t}>（{line}行目）が閉じられていない")
                del self.stack[i:]
                return
        self.errors.append(f"</{tag}>（{self.getpos()[0]}行目）に対応する開始タグがない")

bad = False
for path in sys.argv[1:]:
    p = P()
    p.feed(open(path, encoding="utf-8", errors="replace").read())
    probs = []
    need = {"charset": '<meta charset="UTF-8"> を <head> に入れる',
            "lang": '<html lang="ja"> のように言語を書く',
            "title": "<title>ページ名</title> を <head> に入れる",
            "viewport": '<meta name="viewport" content="width=device-width, initial-scale=1"> を入れる（スマホ対応）'}
    for k, fix in need.items():
        if k not in p.has: probs.append(fix)
    if p.noalt: probs.append(f'alt のない画像が {p.noalt} 枚：<img alt="画像の説明"> のように書く')
    probs += [e + "：対応するタグを足すか消す" for e in p.errors[:5]]
    for t, line in p.stack:
        if t not in ("html","body","head","p","li"): probs.append(f"<{t}>（{line}行目）が閉じられていない：</{t}> を足す")
    if probs:
        bad = True
        print(f"   {path}:")
        for x in probs: print(f"     - {x}")
sys.exit(1 if bad else 0)
PY
  then pass "HTML の基本ができている（${#html_files[@]} ファイル）"
  else fail "HTML に直したほうがいいところがあります（上の一覧）" "一覧の「- 」のあとに書かれた通りに直す"
  fi
else
  skip "HTML ファイルはない"
fi

# 5. JSON が壊れていないか
json_bad=""
for f in "${FILES[@]}"; do
  case "$f" in *.json) [ -f "$f" ] && ! python3 -m json.tool "$f" >/dev/null 2>&1 && json_bad+="$f ";; esac
done
if [ -n "$json_bad" ]; then
  fail "JSON の書き方がまちがっています：$json_bad" "カンマの付けすぎ・付け忘れ、かっこの閉じ忘れを確認する"
else
  pass "JSON ファイルが壊れていない"
fi

# 6. CLAUDE.md が長くなりすぎていないか（地図として短く保つ）
if [ -f CLAUDE.md ]; then
  n=$(wc -l < CLAUDE.md)
  if [ "$n" -gt 150 ]; then
    fail "CLAUDE.md が $n 行あります（150 行まで）" "細かい内容は docs/agent/ のファイルに移して、CLAUDE.md にはその場所だけ書く"
  else
    pass "CLAUDE.md が短く保たれている（$n 行）"
  fi
fi

# 7. Node.js のプロジェクトなら、用意されたチェックを実行する
if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  scripts=$(python3 -c 'import json;print(" ".join(json.load(open("package.json")).get("scripts",{}).keys()))' 2>/dev/null || true)
  ran=0
  for s in lint typecheck test build; do
    if [[ " $scripts " == *" $s "* ]]; then
      if [ ! -d node_modules ]; then
        (npm ci --no-audit --no-fund >/dev/null 2>&1 || npm install --no-audit --no-fund >/dev/null 2>&1) || true
      fi
      ran=1
      if npm run -s "$s" >/tmp/harness-npm-$s.log 2>&1; then
        pass "npm run $s が通った"
      else
        tail -n 30 /tmp/harness-npm-$s.log | sed 's/^/   | /'
        fail "npm run $s が失敗しました（上がその最後の部分）" "表示されたエラーの場所を直して、もう一度 bash scripts/check.sh を実行する"
      fi
    fi
  done
  [ $ran -eq 0 ] && skip "package.json に lint / typecheck / test / build がない"
fi

# 8. プロジェクト独自のチェック
if [ -f scripts/check.local.sh ]; then
  if bash scripts/check.local.sh; then pass "独自のチェック（scripts/check.local.sh）が通った"
  else fail "独自のチェック（scripts/check.local.sh）が失敗しました" "上に表示されたメッセージに従って直す"
  fi
fi

echo
if [ $failed -ne 0 ]; then
  echo "結果：❌ 直すところがあります。上の「→ 直し方」を見てください。"
  exit 1
fi
echo "結果：✅ すべて通りました"
