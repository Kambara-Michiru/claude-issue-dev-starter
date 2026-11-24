---
name: check
description: Issue 駆動の仕組みがいまどうなっているか（作業中の依頼、届いた提出物、失敗した実行）を調べて、開発経験のない人にもわかる言葉で報告する。「Claude の作業どうなった？」「動かない」「状況を教えて」と言われたときに使う。
---

# いまの状況を確認する

リポジトリのフォルダの中で、次を実行して状況を集める（読むだけで、何も変更しない）。

```bash
gh issue list --label claude --state open --limit 20
gh pr list --state open --limit 20
gh run list --limit 10
gh secret list
ls .github/workflows/ .github/ISSUE_TEMPLATE/ 2>/dev/null
test -f CLAUDE.md && echo "CLAUDE.md あり" || echo "CLAUDE.md なし"
```

## 報告のしかた

専門用語を避けて、次の4つの見出しでまとめる。

1. **作業中の依頼書**：`claude` ラベルが付いていて、まだ閉じていない Issue
2. **見てほしい提出物**：開いている PR。それぞれ「何の依頼に対するものか」と「次にやること（中身を見てマージ、または @claude で直してもらう）」を書く
3. **うまくいかなかった実行**：`gh run list` で失敗（failure）になっているもの。あれば `gh run view <ID> --log-failed` でログの最後のほうを読み、原因を1〜2文で言い換える
4. **仕組みの点検**：鍵（secret）、ワークフロー、依頼書テンプレート、CLAUDE.md がそろっているか

よくある原因の見分け方は `${CLAUDE_SKILL_DIR}/../../docs/06-troubleshooting.md` を読んで使う。
直す必要があるときは、何をするかを伝えて OK をもらってから作業する。鍵の作り直しは相手自身にしてもらう。
