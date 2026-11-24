# 5. 安全と費用

## お金の話

この仕組みでは、2種類の費用がかかります。

| 何に | どのくらい | 減らすには |
|---|---|---|
| **Claude の利用** | 有料プランのトークンを使うなら、プランの利用上限の範囲内。API キーなら使った分だけ | 依頼書を具体的に書く、1つの依頼を小さくする |
| **GitHub Actions の実行時間** | 公開リポジトリは無料。非公開リポジトリは、プランごとの無料枠を超えた分が有料 | 必要なときだけ動かす |

このスキル集のワークフローには、使いすぎを防ぐしかけが入っています。

- **時間の上限**：1回の作業は30分（チェックは20分）で自動的に止まります（`timeout-minutes`）
- **やりとりの上限**：Claude が試行錯誤する回数に上限があります（`--max-turns`）
- **二重に動かない**：同じ依頼書で同時に2回動かないようにしています（`concurrency`）

> 最新の料金は [Claude の料金](https://claude.com/pricing) と [GitHub Actions の料金](https://docs.github.com/en/billing/concepts/product-billing/github-actions) で確認してください。

## 安全の話

### Claude は勝手に本番を変えない

- 依頼書から作業したとき、Claude は **下書き用のブランチに作業して、PR を作るリンクを置くだけ** です。PR を作るのも、マージするのも、あなたです
- main（本番）に直接書き込まないよう、CLAUDE.md でも決めています
- 公開リポジトリや GitHub の有料プランなら、`/issue-dev:setup` のステップ 6 で「main は PR 経由でしか変えられない」設定もできます

### 誰が Claude を動かせるか

- Claude を動かせるのは、**そのリポジトリに書き込み権限のある人だけ** です。知らない人が公開リポジトリで `@claude` と書いても動きません
- `claude` ラベルを付けられるのも、権限のある人だけです
- ほかのボットが Claude を呼ぶことも、初期設定ではできません

### 鍵（トークン・API キー）の扱い

- 鍵は **GitHub の secret（金庫）にだけ** しまいます。ファイルに書いたり、チャットに貼ったりしないでください
- うっかり人に見せてしまったら、すぐに作り直します
  - サブスクリプションのトークン：`claude setup-token` で作り直し、`gh secret set CLAUDE_CODE_OAUTH_TOKEN` で入れ替える
  - API キー：https://platform.claude.com でキーを削除して新しく作る

### 公開リポジトリにするときの注意

公開リポジトリは、世界中の誰でも中身を読めます。次のものは入れないでください。

- パスワード、API キー
- 住所や電話番号などの個人情報
- 公開してはいけない仕事の資料

### Claude GitHub App の権限

Claude の GitHub App をインストールすると、ファイルの読み書き、Issue や PR へのコメントなどの権限を渡します。必要なリポジトリにだけインストールするのがおすすめです（インストール時に「Only select repositories」を選ぶ）。

### 仕組みをやめたいとき

1. `.github/workflows/` の `claude.yml`、`claude-review.yml`、`claude-label.yml` を削除する
2. リポジトリの Settings → Secrets and variables → Actions で、鍵を削除する
3. 必要なら、GitHub の Settings → Applications から Claude の App をアンインストールする

次は [困ったとき](06-troubleshooting.md) へ。
