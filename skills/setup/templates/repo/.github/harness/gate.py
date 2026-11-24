#!/usr/bin/env python3
"""自動マージの関門（ゲート）。

AI の判断だけでマージを決めないための、決まりきったルールの判定役です。
claude-gate.yml から、main ブランチの版がそのまま実行されます
（PR の中でこのファイルを書き換えても、判定には影響しません）。

入力（すべて JSON ファイル）:
  --policy  .github/harness/policy.json
  --pr      gh pr view の結果
  --checks  チェックの結果 {"result": "success" | "failure" | ...}
  --review  レビュー役の Claude の結果（structured_output）
  --issue   つながっている Issue の情報（なければ {}）
  --run     チェックを実行したときの情報 {"head_sha": "..."}

出力: 判定結果の JSON を標準出力に出す。
  {"mode": "...", "eligible": bool, "merge": bool, "checks": [{"ok": bool, "text": "..."}]}
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path


def load(path: str) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8") or "{}")
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def matches(path: str, pattern: str) -> bool:
    if fnmatch.fnmatch(path, pattern):
        return True
    # "**/" で始まるパターンは、いちばん上の階層のファイルにも当てはめる
    if pattern.startswith("**/") and fnmatch.fnmatch(path, pattern[3:]):
        return True
    return False


def linked_issue_number(body: str) -> int | None:
    m = re.search(r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", body or "")
    return int(m.group(1)) if m else None


def evaluate(policy: dict, pr: dict, checks: dict, review: dict, issue: dict, run: dict) -> dict:
    mode = policy.get("mode", "off")
    if mode not in ("off", "shadow", "on"):
        mode = "off"
    results: list[dict] = []

    def check(ok: bool, text: str) -> None:
        results.append({"ok": bool(ok), "text": text})

    labels = {lbl.get("name") for lbl in pr.get("labels", []) if isinstance(lbl, dict)}
    auto_label = policy.get("auto_label", "claude-auto")
    hold_label = policy.get("hold_label", "hold")

    # --- 対象かどうか（対象外なら、静かに終わる） ---
    applies = auto_label in labels
    if not applies:
        return {"mode": mode, "applies": False, "eligible": False, "merge": False, "checks": []}

    # --- PR の状態 ---
    check(pr.get("state") == "OPEN", "PR が開いている")
    check(not pr.get("isDraft", False), "下書き（Draft）ではない")
    check(hold_label not in labels, f"「{hold_label}」ラベルが付いていない")

    author = (pr.get("author") or {}).get("login", "")
    check(author in policy.get("trusted_authors", []), f"作ったのが自動化の仕組み（{author or '不明'}）である")

    prefix = policy.get("branch_prefix", "claude/")
    check(str(pr.get("headRefName", "")).startswith(prefix), f"ブランチ名が {prefix} で始まる")

    head = pr.get("headRefOid", "")
    check(bool(head) and head == run.get("head_sha"), "チェックとレビューのあとに、中身が変わっていない")

    # --- 依頼書 ---
    issue_no = linked_issue_number(pr.get("body", ""))
    check(issue_no is not None, "依頼書（Issue）とつながっている（Closes #番号）")
    assoc = issue.get("author_association", "")
    check(assoc in policy.get("trusted_issue_authors", []), "依頼書を書いたのが、このリポジトリのメンバーである")

    # --- 機械のチェック（センサー） ---
    check(checks.get("result") == "success", "機械のチェック（scripts/check.sh）がすべて通った")

    # --- レビュー役の Claude（判断） ---
    verdict = review.get("verdict")
    check(verdict == "approve", f"レビュー役の Claude が承認した（結果：{verdict or 'なし'}）")
    risk = review.get("risk")
    allowed = policy.get("allowed_risk", ["low"])
    check(risk in allowed, f"危険度が {'/'.join(allowed)} である（判定：{risk or 'なし'}）")
    blocking = set(policy.get("blocking_severities", ["blocker", "major"]))
    serious = [f for f in review.get("findings", []) if isinstance(f, dict) and f.get("severity") in blocking]
    check(not serious, f"重大な指摘がない（{len(serious)} 件）")
    if policy.get("require_all_criteria_met", True):
        criteria = [c for c in review.get("criteria", []) if isinstance(c, dict)]
        unmet = [c for c in criteria if not c.get("met")]
        check(bool(criteria) and not unmet, f"完成の条件をすべて満たしている（未達 {len(unmet)} / {len(criteria)}）")

    # --- 変更の大きさと場所（影響範囲） ---
    files = [f for f in pr.get("files", []) if isinstance(f, dict)]
    changed_files = int(pr.get("changedFiles", len(files)) or 0)
    max_files = int(policy.get("max_changed_files", 10))
    check(changed_files <= max_files, f"変更したファイルが {max_files} 個以下（{changed_files} 個）")
    lines = int(pr.get("additions", 0) or 0) + int(pr.get("deletions", 0) or 0)
    max_lines = int(policy.get("max_changed_lines", 300))
    check(lines <= max_lines, f"変更した行数が {max_lines} 行以下（{lines} 行）")
    # ファイル一覧が途中で切れている（100 件を超える）ときは、安全側に倒す
    check(len(files) >= changed_files, "変更したファイルの一覧をすべて確認できた")
    protected = policy.get("protected_paths", [])
    touched = sorted({f.get("path", "") for f in files if any(matches(f.get("path", ""), p) for p in protected)})
    check(not touched, "守るべきファイルに触れていない" + (f"（触れたもの：{', '.join(touched)}）" if touched else ""))

    eligible = all(r["ok"] for r in results)
    return {
        "mode": mode,
        "applies": True,
        "eligible": eligible,
        "merge": eligible and mode == "on",
        "pr_number": pr.get("number"),
        "head_sha": head,
        "issue_number": issue_no,
        "merge_method": policy.get("merge_method", "squash"),
        "checks": results,
    }


def render(decision: dict) -> str:
    """PR に書くコメント（日本語）。"""
    if not decision.get("applies"):
        return ""
    mode = decision["mode"]
    if decision["merge"]:
        head = "### 🤖 自動マージの関門：通過 → マージします"
    elif decision["eligible"] and mode == "shadow":
        head = "### 🧪 自動マージの関門（練習モード）：本番なら自動マージされていました"
    elif decision["eligible"] and mode == "off":
        head = "### ⏸️ 自動マージの関門：条件は満たしていますが、自動マージは止めてあります"
    else:
        head = "### 🙋 自動マージの関門：人の確認が必要です"
    rows = "\n".join(f"| {'✅' if r['ok'] else '❌'} | {r['text']} |" for r in decision["checks"])
    tail = {
        "shadow": "いまは**練習モード**なので、マージは人がしてください。判定が信頼できると思えたら `/issue-dev:automerge` で本番（on）に切り替えられます。",
        "off": "自動マージは**オフ**です。マージは人がしてください。",
        "on": "止めたいときは、この PR に `hold` ラベルを付けてください。",
    }[mode]
    return f"<!-- harness-gate -->\n{head}\n\n| | 条件 |\n|---|---|\n{rows}\n\n{tail}\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    for name in ("policy", "pr", "checks", "review", "issue", "run"):
        ap.add_argument(f"--{name}", required=True)
    ap.add_argument("--comment-out", help="PR に書くコメントの保存先")
    a = ap.parse_args()
    decision = evaluate(load(a.policy), load(a.pr), load(a.checks), load(a.review), load(a.issue), load(a.run))
    if a.comment_out:
        Path(a.comment_out).write_text(render(decision), encoding="utf-8")
    json.dump(decision, sys.stdout, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
