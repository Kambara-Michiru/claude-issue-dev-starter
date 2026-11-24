---
name: check
description: Issue 駆動の仕組みがいまどうなっているか（作業中の依頼、届いた提出物、関門の判定、失敗した実行）を調べて、開発経験のない人にもわかる言葉で報告する。「Claude の作業どうなった？」「動かない」「状況を教えて」と言われたときに使う。
---

# いまの状況を確認する

リポジトリのフォルダの中で、次を実行して状況を集める（読むだけで、何も変更しない）。

```bash
gh issue list --label claude --state open --limit 20
gh issue list --label claude-auto --state open --limit 20
gh issue list --label needs-info --state open --limit 20
gh pr list --state open --limit 20 --json number,title,labels,isDraft,author
gh run list --limit 15
gh secret list
ls .github/workflows/ .github/harness/ .github/ISSUE_TEMPLATE/ scripts/ 2>/dev/null
git fetch -q origin && git show "origin/HEAD:.github/harness/policy.json" 2>/dev/null | python3 -c 'import json,sys; print("自動マージのモード:", json.load(sys.stdin).get("mode"))'
gh api repos/{owner}/{repo}/actions/permissions/workflow
```

開いている PR それぞれについて、最新の関門コメントの1行目を読む。

```bash
gh api "repos/{owner}/{repo}/issues/<番号>/comments" --jq '[.[] | select(.body | startswith("<!-- harness-gate -->"))][-1].body' | head -3
```

## 報告のしかた

専門用語を避けて、次の見出しでまとめる。

1. **作業中の依頼書**：`claude` / `claude-auto` が付いていて、まだ閉じていないもの
2. **答えを待っている依頼書**：`needs-info` が付いているもの。「質問に答えたら、ラベルを付け直す」と伝える
3. **見てほしい提出物**：開いている PR と、それぞれの関門の判定（✅ 通過／🧪 練習モードで通過／🙋 人の確認が必要）。人の確認が必要なものは、❌ の項目を言い換えて「次にやること」を書く
4. **うまくいかなかった実行**：失敗しているものがあれば `gh run view <ID> --log-failed` の最後のほうを読み、原因を1〜2文で言い換える
5. **仕組みの点検**：鍵（secret）、5つのワークフロー、関門のルール、`scripts/check.sh`、CLAUDE.md がそろっているか。`can_approve_pull_request_reviews` が `false` なら、PR を作れないので直す必要がある

よくある原因の見分け方は `${CLAUDE_SKILL_DIR}/../../docs/06-troubleshooting.md` を使う。
直す必要があるときは、何をするかを伝えて OK をもらってから作業する。鍵の作り直しは相手自身にしてもらう。
