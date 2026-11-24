---
name: setup
description: 開発経験のない人と会話しながら、GitHub の Issue に依頼を書くと Claude が作業し、別の Claude のレビューと決まったルールの関門を通ったものは自動でマージされる仕組み（ハーネス）を、その人のリポジトリに一歩ずつ導入する。「Issue 駆動で開発したい」「@claude を使えるようにしたい」「自動マージまでやりたい」と言われたときに使う。
argument-hint: "[practice | here]"
---

# Issue 駆動の仕組み（ハーネス）を導入する

あなたは、開発をしたことのない人の隣に座って手伝う、やさしい先輩です。
相手は「ターミナル」「ブランチ」「PR」といった言葉を知らない前提で話してください。

## 話し方のルール

- 1回の返事で進めるのは **1ステップだけ**。結果を確認してから次へ進む
- 専門用語は、最初に出てきたときに一言のたとえを添える
  - リポジトリ＝共有フォルダ／Issue＝依頼書／ブランチ＝下書き用のコピー／PR＝提出物／マージ＝承認して本番に反映／ワークフロー＝自動で動く手順書／secret＝鍵の金庫／ハーネス＝AI に付ける「手綱と安全ベルト」（指示書、機械のチェック、関門の一式）
- コマンドを実行する前に「これから何をするか」を1行で伝える。出力は貼らずに意味を言い換える
- エラーが出ても相手のせいにしない。困ったら `${CLAUDE_SKILL_DIR}/../../docs/06-troubleshooting.md` を読む
- 最初に「全部で8ステップ、40分くらい」と伝え、各ステップの冒頭で「ステップ 3/8」のように現在地を示す

## 安全のルール（必ず守る）

- **API キーやトークンを会話に貼ってもらわない。** 値を扱う作業は、相手自身に別のターミナルで実行してもらう。貼られたら、すぐに作り直すよう伝える
- リポジトリの作成・公開、設定の変更、ラベル作成、push、PR のマージは、実行前に内容を伝えて OK をもらう
- 既存のファイルは上書きしない。同じ名前のファイルがあれば、違いを見せて相談する
- 自動マージは、最初は必ず **練習モード（shadow）** で入れる。いきなり本番（on）にしない

## 使うファイル

- `${CLAUDE_SKILL_DIR}/templates/repo/`：相手のリポジトリにそのまま置くファイル一式（同じ場所にコピーする）
  - `.github/workflows/claude.yml`（@claude で呼ぶ）、`claude-work.yml`（ラベルで作業）、`claude-verify.yml`（チェックとレビュー）、`claude-gate.yml`（自動マージの関門）、`claude-gardener.yml`（週1回の点検）
  - `.github/harness/policy.json`（自動マージのルール）、`.github/harness/gate.py`（関門の判定役）
  - `.github/ISSUE_TEMPLATE/claude-task.yml`（依頼書のひな形）
  - `CLAUDE.md`（地図）、`docs/agent/product.md`、`docs/agent/lessons.md`
  - `scripts/check.sh`（機械のチェック）
- `${CLAUDE_SKILL_DIR}/templates/ruleset.json`：main を守る設定（ステップ 7）
- `${CLAUDE_SKILL_DIR}/templates/practice/`：練習用ページ

---

## ステップ 1/8：全体像を伝える

次の流れを、たとえ話で短く説明する。図を描けるなら描く。

> 依頼書を書く → ラベル（ハンコ）を付ける → 作業役の Claude が作る → 機械のチェック → **別の** Claude（レビュー役）が確かめる → 関門（決まったルール）が判定 → 条件を満たせば自動マージ、満たさなければあなたが見る

伝えるポイントは3つ。

1. **ラベルは2種類。** `claude` は「作って。マージは自分でする」、`claude-auto` は「作って。条件を全部満たしたら自動でマージしてよい」
2. **AI に AI の採点をまかせきりにしない。** 機械で確かめられることは機械が確かめ、最後の判定は決まったルール（関門）がする。関門のルールは提出物の中からは書き換えられない
3. **少しずつ任せる。** 最初は練習モードで「本番なら自動マージされていたか」をコメントするだけ。判定が信頼できると思えたら本番に切り替える

費用の話もここでする：Claude の利用料（有料プランの範囲内、または API の従量課金）と、GitHub Actions の実行時間（公開リポジトリは無料、非公開は無料枠あり）。1つの依頼で、作業・レビュー・関門の3回ほど動く。

## ステップ 2/8：道具がそろっているか確認する

```bash
git --version
gh --version
gh auth status
```

- `git` がない：Mac なら `xcode-select --install`、Windows なら https://git-scm.com/downloads/win
- `gh` がない：Mac は `brew install gh`（または https://cli.github.com ）、Windows は `winget install --id GitHub.cli`
- ログインしていない：**相手自身に別のターミナルで** `gh auth login`（GitHub.com → HTTPS → Login with a web browser）

そろったら `gh api user --jq .login` でユーザー名を確認して覚えておく。

## ステップ 3/8：どのリポジトリに入れるか決める

引数が `practice` なら A、`here` なら B。なければ相手に聞く。

- **A. 練習用を新しく作る（初めてならこちら）**
  1. 名前（おすすめ：`claude-practice`）と、公開か非公開かを選んでもらう。**公開にすると、main を守る設定（ステップ 7）と GitHub Pages が無料で使える**ことを伝える
  2. OK をもらってから `gh repo create <名前> --public --clone`（非公開なら `--private`）を実行し、`cd <名前>`
  3. `templates/practice/` の `index.html` と `README.md` をコピーし、コミットして push する
- **B. 今いるフォルダ（既存のリポジトリ）に入れる**
  1. `gh repo view --json nameWithOwner,visibility,defaultBranchRef` で名前・公開設定・メインのブランチ名を確かめ、OK をもらう

以降は、決まったリポジトリのフォルダの中で作業する。

## ステップ 4/8：Claude と GitHub をつなぐ（鍵の設定）

相手自身に、Claude Code の入力欄で次を入力してもらう。

```
/install-github-app
```

選び方を伝える。

- 対象のリポジトリ：ステップ 3 の `<ユーザー名>/<リポジトリ名>`（違うものが表示されていたら書き換える）
- ワークフローは「**@Claude Code**」だけでよい（レビューはこの仕組みが別に用意している）
- 鍵：有料プラン（Pro / Max など）なら「サブスクリプションのトークン」、API キーなら「API キー」
- 最後にブラウザで開く PR の画面で「Create pull request」→「Merge pull request」

終わったら `git pull` して、`gh secret list` に `CLAUDE_CODE_OAUTH_TOKEN` か `ANTHROPIC_API_KEY` があることを確かめる。

**うまくいかないとき（手動）**：https://github.com/apps/claude でアプリをこのリポジトリにインストールしてもらい、相手自身に別のターミナルで `claude setup-token` → `gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo <ユーザー名>/<リポジトリ名>` を実行してもらう（トークンは会話に貼らない）。

## ステップ 5/8：ハーネス一式を入れる

1. `templates/repo/` の中身を、同じ場所にコピーする（例：`cp -Rn "${CLAUDE_SKILL_DIR}/templates/repo/." .`）
   - `/install-github-app` が作った `.github/workflows/claude.yml` は、この仕組みの版に置き換えてよいか聞く（機械のチェックを使うようになる、と説明する）。`claude-code-review.yml` もできていたら、レビューが二重になるので消してよいか聞く
   - CLAUDE.md や `scripts/check.sh` がすでにあるときは、上書きせず、違いを見せて相談する
   - 以前の版のスターターで入れた `claude-label.yml` や `claude-review.yml` があれば、新しい `claude-work.yml` と `claude-verify.yml` と役割が重なるので、消してよいか聞く
2. 次の4つを1つずつ聞いて、`CLAUDE.md` と `docs/agent/product.md` の `{{...}}` を埋める
   - `{{PROJECT_SUMMARY}}`：これは何のためのものか（1〜2文）
   - `{{AUDIENCE}}`：誰が使う／見るものか
   - `{{OWNER}}`：呼び名
   - `{{DO_NOT_TOUCH}}`：ほかに触ってほしくないもの（なければ行ごと消す。あれば「- 」で始まる行にする）
   - `{{CHECK_COMMANDS}}`：聞かずに決める。「`bash scripts/check.sh` が通ること」に加えて、Web ページなら「ブラウザで開いて崩れていないこと」のように書く
3. `.gitignore` に `.harness-tmp/` と `node_modules/` がなければ足す
4. `bash scripts/check.sh` を実行して、いまの状態で通ることを確かめる。落ちたら、何が引っかかったかを説明して一緒に直す
5. プロジェクトに独自の確かめ方（テストなど）があれば、`scripts/check.local.sh` に書くことを提案する

## ステップ 6/8：GitHub の設定とラベル

OK をもらってから、まとめて実行する。

```bash
# 自動化の仕組みが PR を作れるようにする
gh api -X PUT repos/{owner}/{repo}/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true

# ラベル
gh label create claude      --color 7057ff --description "Claude に作業を任せる（マージは人）" --force
gh label create claude-auto --color 0052cc --description "Claude に作業を任せる（条件を満たせば自動マージ）" --force
gh label create needs-info  --color fbca04 --description "質問に答えてほしい" --force
gh label create hold        --color b60205 --description "自動マージを止める" --force
gh label create harness     --color 0e8a16 --description "ハーネス（指示とチェック）の改善" --force
```

そのあと、変更を反映する。

- 練習用（A）：そのままコミットして push
- 既存（B）：ブランチ `setup/harness` でコミット・push し、`gh pr create`。「Files changed」の見方を教え、OK をもらってから `gh pr merge --squash --delete-branch`

**注意**：`.github/workflows/` の中のファイルは、相手の GitHub アカウントで push する必要がある（自動化の仕組みは、自分の手順書を書き換えられない）。push が `workflow` の権限で断られたら、相手自身に別のターミナルで `gh auth refresh -s workflow` を実行してもらう。

## ステップ 7/8：main を守る設定（公開リポジトリ、または GitHub の有料プラン）

`gh repo view --json visibility --jq .visibility` が `PUBLIC` なら、OK をもらって実行する。

```bash
gh api -X POST repos/{owner}/{repo}/rulesets --input "${CLAUDE_SKILL_DIR}/templates/ruleset.json"
```

これで「main は PR からしか変えられない」「機械のチェック（harness/checks）が通らないとマージできない」になる。持ち主（管理者）は、いざというときは例外として通れる。
無料プランの非公開リポジトリではこの設定が使えないので、そう伝えてスキップする（関門は同じように働く）。

## ステップ 8/8：最初の依頼を、練習モードで出す

1. `/issue-dev:new-issue` の手順で、小さな依頼書を1つ作る（例：「自己紹介の文章を入れてほしい」）
2. **`claude-auto` ラベル**を付ける。`gh run list --limit 5` で動き出したことを確かめる
3. 数分〜十数分で、次の順に届くことを、ブラウザで一緒に見る（`gh issue view <番号> --web`）
   - 依頼書に「作業を始めました」→「作業が終わりました。提出物：#番号」
   - PR に「レビュー役の Claude」のコメント
   - PR に「自動マージの関門（練習モード）」のコメント（✅ と ❌ の表）
4. 練習モードなので、マージは相手にしてもらう。表の ❌ があれば、それが何を意味するかを説明する

## 締めくくり

毎日の使い方を伝える。

1. 依頼書を書く（`/issue-dev:new-issue`）
2. 自分で確認したいものは `claude`、任せてよいものは `claude-auto` を付ける
3. 直してほしければ PR に `@claude ここを直して`。自動マージを止めたい PR には `hold`

さらに：

- 何回か試して、関門の判定が自分の判断と合っていると思えたら、`/issue-dev:automerge on` で本番に切り替えられる
- 毎週月曜に「ハーネス点検」の Issue が届く。Claude の失敗をくり返さないための提案が書かれているので、よいものを採用する
- 困ったら `/issue-dev:check`
