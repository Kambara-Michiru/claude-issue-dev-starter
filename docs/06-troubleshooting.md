# 6. 困ったとき

まずは Claude Code で `/issue-dev:check` と入力してください。いまの状況を調べて、わかる言葉で教えてくれます。

それでもわからないときは、下の表から近いものを探してください。

## ラベルを付けても、@claude と書いても反応しない

| 確かめること | 見る場所 | 直し方 |
|---|---|---|
| Claude の GitHub App が入っているか | https://github.com/apps/claude →「Configure」 | このリポジトリを選んでインストールする |
| 鍵が金庫に入っているか | リポジトリの Settings → Secrets and variables → Actions | `CLAUDE_CODE_OAUTH_TOKEN` か `ANTHROPIC_API_KEY` がなければ、`/issue-dev:setup` のステップ 4 をやり直す |
| ワークフローのファイルがあるか | リポジトリの `.github/workflows/` | `claude.yml`、`claude-work.yml`、`claude-verify.yml`、`claude-gate.yml` がなければ、`/issue-dev:setup` のステップ 5 をやり直す |
| ワークフローが main に入っているか | 同上（main ブランチで見る） | セットアップの PR がマージされていなければマージする |
| Actions が止められていないか | Actions タブ | 「I understand my workflows, go ahead and enable them」が出ていれば押す |
| ラベルの名前が合っているか | Issue の Labels | 小文字の `claude` か `claude-auto` ちょうど。`Claude` や `claude-ai` では動かない |
| 書き方が合っているか | コメント | `@claude` は半角で、前後にスペース。`＠claude`（全角）や `/claude` では動かない |
| 自分に書き込み権限があるか | Settings → Collaborators | 持ち主か、書き込み権限のある人だけが Claude を動かせる |

## Actions タブで ✗（失敗）になっている

Actions タブで失敗した実行を開くと、どこで止まったかが表示されます。よくある原因はこちらです。

| 表示されている言葉 | 意味 | 直し方 |
|---|---|---|
| `authentication`、`401`、`invalid x-api-key`、`token` | 鍵が間違っている、または期限切れ | 鍵を作り直して金庫に入れ直す（[安全と費用](05-safety-and-cost.md#鍵トークンapi-キーの扱い)） |
| `credit balance is too low` | API の残高が足りない | https://platform.claude.com で残高を追加する |
| `usage limit`、`rate limit` | 利用上限に達した | 少し時間をおいてから、もう一度ラベルを付け直す |
| `The job running on runner ... has exceeded the maximum execution time` | 時間の上限（作業 45 分、レビュー 20 分）で止まった | 依頼が大きすぎる可能性。依頼書を小さく分ける |
| `max turns` | やりとりの上限に達した | 依頼を小さくするか、ワークフローの `--max-turns` の数字を少し増やす |
| `does not have write permissions` | 動かした人に権限がない | 書き込み権限のある人がラベルを付ける |

## 「作業が終わりました」のあと、PR ができない

| 表示されている言葉 | 意味 | 直し方 |
|---|---|---|
| `GitHub Actions is not permitted to create or approve pull requests` | 自動化の仕組みに PR を作る許可がない | Settings → Actions → General のいちばん下で「Allow GitHub Actions to create and approve pull requests」にチェックを入れて保存。または `/issue-dev:setup` のステップ 6 をやり直す |
| `refusing to allow a GitHub App to create or update workflow` | Claude が `.github/workflows/` を変えようとした | 自動化の仕組みは、自分の手順書を書き換えられません。依頼書から仕組みの変更を外すか、`claude` ラベルにして、手順書の変更は人がする |
| 「ファイルは変わりませんでした」 | Claude が変える必要はないと判断した | 依頼書の「完成の条件」をもっと具体的にして、ラベルを付け直す |

## 関門のコメントに ❌ がある

関門は、❌ が1つでもあれば自動マージしません（そういう設計です）。よくある ❌ と、その意味です。

| ❌ の行 | 意味 | どうするか |
|---|---|---|
| レビュー役の Claude が承認した | レビューで直したほうがいい点が見つかった | レビューのコメントを読み、`@claude 指摘を直して` |
| 危険度が low である | レビュー役が「中」か「高」と判断した | 「危険度の根拠」を読んで、自分で確認してマージする |
| 完成の条件をすべて満たしている | 条件のどれかができていない | `@claude 完成の条件の〇つ目ができていないので直して` |
| 守るべきファイルに触れていない | 仕組みや設定、鍵に関係するファイルが変わった | 変わったファイルを確認。意図どおりなら自分でマージ |
| 変更したファイル／行数が〇以下 | 変更が大きい | 自分で確認してマージ。次からは依頼を小さく分ける |
| チェックとレビューのあとに、中身が変わっていない | 確認の途中で新しい変更が入った | 少し待つと、新しい中身で判定し直されます |
| 依頼書を書いたのが、このリポジトリのメンバーである | 外の人が書いた依頼書 | 中身を確認して、自分でマージ |

## 練習モードのまま、本番にならない

`.github/harness/policy.json` の `"mode"` が `"shadow"` のままです。`/issue-dev:automerge on` で切り替えの PR を作り、マージしてください。**main に入った時点から**本番になります。

## 自動マージしたあと、サイトに反映されない

自動マージは GitHub の自動化の仕組み（`GITHUB_TOKEN`）が行うため、「main に push されたら動く」ほかのワークフロー（サイトの公開など）が動かないことがあります。その場合は、公開のワークフローに `workflow_run`（関門のあとに動く）を足すか、Actions タブから手動で動かしてください。

## Claude の作業がイメージと違う

- **完成の条件** を具体的にして、PR に `@claude 完成の条件の2つ目ができていないので直して` と書く
- 同じ間違いをくり返すなら、**CLAUDE.md の「これまでに覚えたこと」** に1行足す（例：「画像は images/ フォルダに置く」）
- どうしても合わないときは、PR を閉じて（Close pull request）、依頼書を書き直してからラベルを付け直す

## もう一度やり直したい

ラベルを一度外してから、付け直します。Claude が新しく作業を始めます。

## PR のチェックだけ動かない

- 下書き（Draft）の PR は、レビュー役の Claude が読みません（関門も通しません）。「Ready for review」を押してください
- 外の人のコピー（フォーク）からの PR は、安全のためチェックしません
- もう一度動かしたいときは、Actions タブで該当の実行を開き「Re-run jobs」を押します

## それでも解決しないとき

- 公式の [Claude Code GitHub Actions のトラブル対応](https://code.claude.com/docs/en/github-actions#troubleshooting)
- [claude-code-action の FAQ](https://github.com/anthropics/claude-code-action/blob/main/docs/faq.md)
- このリポジトリの [Issues](https://github.com/Kambara-Michiru/claude-issue-dev-starter/issues) で質問する
