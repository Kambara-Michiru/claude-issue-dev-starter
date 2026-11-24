# 6. 困ったとき

まずは Claude Code で `/issue-dev:check` と入力してください。いまの状況を調べて、わかる言葉で教えてくれます。

それでもわからないときは、下の表から近いものを探してください。

## ラベルを付けても、@claude と書いても反応しない

| 確かめること | 見る場所 | 直し方 |
|---|---|---|
| Claude の GitHub App が入っているか | https://github.com/apps/claude →「Configure」 | このリポジトリを選んでインストールする |
| 鍵が金庫に入っているか | リポジトリの Settings → Secrets and variables → Actions | `CLAUDE_CODE_OAUTH_TOKEN` か `ANTHROPIC_API_KEY` がなければ、`/issue-dev:setup` のステップ 4 をやり直す |
| ワークフローのファイルがあるか | リポジトリの `.github/workflows/` | なければ `/issue-dev:setup` のステップ 5 をやり直す |
| ワークフローが main に入っているか | 同上（main ブランチで見る） | セットアップの PR がマージされていなければマージする |
| Actions が止められていないか | Actions タブ | 「I understand my workflows, go ahead and enable them」が出ていれば押す |
| ラベルの名前が合っているか | Issue の Labels | 小文字の `claude` ちょうど。`Claude` や `claude-ai` では動かない |
| 書き方が合っているか | コメント | `@claude` は半角で、前後にスペース。`＠claude`（全角）や `/claude` では動かない |
| 自分に書き込み権限があるか | Settings → Collaborators | 持ち主か、書き込み権限のある人だけが Claude を動かせる |

## Actions タブで ✗（失敗）になっている

Actions タブで失敗した実行を開くと、どこで止まったかが表示されます。よくある原因はこちらです。

| 表示されている言葉 | 意味 | 直し方 |
|---|---|---|
| `authentication`、`401`、`invalid x-api-key`、`token` | 鍵が間違っている、または期限切れ | 鍵を作り直して金庫に入れ直す（[安全と費用](05-safety-and-cost.md#鍵トークンapi-キーの扱い)） |
| `credit balance is too low` | API の残高が足りない | https://platform.claude.com で残高を追加する |
| `usage limit`、`rate limit` | 利用上限に達した | 少し時間をおいてから、もう一度ラベルを付け直す |
| `The job running on runner ... has exceeded the maximum execution time` | 30分の上限で止まった | 依頼が大きすぎる可能性。依頼書を小さく分ける |
| `max turns` | やりとりの上限に達した | 依頼を小さくするか、ワークフローの `--max-turns` の数字を少し増やす |
| `does not have write permissions` | 動かした人に権限がない | 書き込み権限のある人がラベルを付ける |

## Claude の作業がイメージと違う

- **完成の条件** を具体的にして、PR に `@claude 完成の条件の2つ目ができていないので直して` と書く
- 同じ間違いをくり返すなら、**CLAUDE.md の「これまでに覚えたこと」** に1行足す（例：「画像は images/ フォルダに置く」）
- どうしても合わないときは、PR を閉じて（Close pull request）、依頼書を書き直してからラベルを付け直す

## もう一度やり直したい

ラベルを一度外してから、付け直します。Claude が新しく作業を始めます。

## PR のチェックだけ動かない

- 下書き（Draft）の PR はチェックされません。「Ready for review」を押してください
- すでに Claude がコメントした PR は、再チェックされないことがあります。`@claude もう一度見て` と書くと見てくれます

## それでも解決しないとき

- 公式の [Claude Code GitHub Actions のトラブル対応](https://code.claude.com/docs/en/github-actions#troubleshooting)
- [claude-code-action の FAQ](https://github.com/anthropics/claude-code-action/blob/main/docs/faq.md)
- このリポジトリの [Issues](https://github.com/Kambara-Michiru/claude-issue-dev-starter/issues) で質問する
