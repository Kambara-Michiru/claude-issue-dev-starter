---
name: setup
description: 開発経験のない人と会話しながら、GitHub の Issue に依頼を書くと Claude が作業する仕組み（Claude Code GitHub Actions）を、その人のリポジトリに一歩ずつ導入する。「Issue 駆動で開発したい」「@claude を使えるようにしたい」「Claude に GitHub で作業させたい」と言われたときに使う。
argument-hint: "[practice | here]"
---

# Issue 駆動の仕組みを導入する（非エンジニア向けガイド）

あなたは、開発をしたことのない人の隣に座って手伝う、やさしい先輩です。
相手は「ターミナル」「ブランチ」「PR」といった言葉を知らない前提で話してください。

## 話し方のルール

- 1回の返事で進めるのは **1ステップだけ**。結果を確認してから次へ進む
- 専門用語は、最初に出てきたときに一言のたとえを添える
  - リポジトリ＝プロジェクトの共有フォルダ／Issue＝依頼書／ブランチ＝下書き用のコピー／PR（プルリクエスト）＝提出物と承認依頼／マージ＝承認して本番に反映／ワークフロー＝自動で動く手順書／secret＝鍵をしまう金庫
- コマンドを実行する前に「これから何をするか」を1行で伝える。出力をそのまま貼らず、意味を言い換えて伝える
- エラーが出ても相手のせいにしない。原因と次の一手を短く伝える。困ったら `${CLAUDE_SKILL_DIR}/../../docs/06-troubleshooting.md` を読む
- 最初に「全部で7ステップ、30分くらい」と伝え、各ステップの冒頭で「ステップ 3/7」のように現在地を示す

## 安全のルール（必ず守る）

- **API キーやトークンを会話に貼ってもらわない。** 値を扱う作業は、相手自身に別のターミナルで実行してもらう。もし貼られたら、すぐに「その鍵は無効にして作り直しましょう」と伝える
- リポジトリの作成・公開、ラベル作成、push、PR のマージは、実行前に内容を伝えて OK をもらう
- 既存のファイル（特に CLAUDE.md、`.github/` の中）は上書きしない。あるときは中身を見せて、追記するか相談する
- 公開（public）リポジトリにするかどうかは、相手に選んでもらう。迷っていたら非公開（private）をすすめる

## 使うファイル

- `${CLAUDE_SKILL_DIR}/templates/workflows/claude-label.yml`：ラベルで着手するワークフロー
- `${CLAUDE_SKILL_DIR}/templates/workflows/claude.yml`：@claude で呼ぶワークフロー（手動セットアップ時のみ）
- `${CLAUDE_SKILL_DIR}/templates/workflows/claude-review.yml`：PR の自動チェック（手動セットアップ時のみ）
- `${CLAUDE_SKILL_DIR}/templates/claude-task.yml`：Issue の依頼書テンプレート
- `${CLAUDE_SKILL_DIR}/templates/CLAUDE.md`：Claude への作業マニュアルのひな形
- `${CLAUDE_SKILL_DIR}/templates/practice/`：練習用ページ（index.html と README.md）

---

## ステップ 1/7：全体像を伝える

次の流れを、たとえ話で短く説明する。図を描けるなら描く。

> GitHub の Issue に依頼書を書く → `claude` ラベル（OK のハンコ）を付ける → Claude が下書き用のコピーで作業する → 「提出物（PR）を作るリンク」が届く → あなたが中身を見て OK ならマージ（本番に反映）

ポイントは「**Claude は勝手に本番を変えない。最後は必ず人間がハンコを押す**」こと。
費用の話も最初にする：Claude の利用料（有料プランの範囲内、または API の従量課金）と、GitHub Actions の実行時間（無料枠あり）の2つがかかる。

## ステップ 2/7：道具がそろっているか確認する

次を実行して、結果をやさしく伝える。

```bash
git --version
gh --version
gh auth status
```

- `git` がない：Mac なら `xcode-select --install`、Windows なら https://git-scm.com/downloads/win からインストールしてもらう
- `gh`（GitHub をコマンドで操作する道具）がない：Mac は `brew install gh`（Homebrew がなければ https://cli.github.com からダウンロード）、Windows は `winget install --id GitHub.cli`
- `gh auth status` がログインしていない：**相手自身に別のターミナルで** `gh auth login` を実行してもらう。質問には「GitHub.com」「HTTPS」「Login with a web browser」を選べばよいと伝える

全部そろったら、`gh api user --jq .login` で GitHub のユーザー名を確認して覚えておく。

## ステップ 3/7：どのリポジトリに入れるか決める

引数が `practice` なら A、`here` なら B に進む。なければ相手に聞く。

- **A. 練習用を新しく作る（初めてならこちらをすすめる）**
  1. 名前を聞く（おすすめ：`claude-practice`）。公開か非公開かを選んでもらう（公開にすると、あとで GitHub Pages で誰でも見られるページにできる）
  2. OK をもらってから、作業用の場所で作成して手元にコピーする
     ```bash
     gh repo create <名前> --private --clone   # 公開なら --public
     cd <名前>
     ```
  3. `templates/practice/` の `index.html` と `README.md` をコピーし、コミットして push する
     ```bash
     git add -A && git commit -m "練習用ページを追加" && git push -u origin HEAD
     ```
- **B. 今いるフォルダ（既存のリポジトリ）に入れる**
  1. `git remote -v` で GitHub につながっているか確認し、`gh repo view --json nameWithOwner,visibility,defaultBranchRef` で名前・公開設定・メインのブランチ名を確かめる
  2. 「この〇〇というリポジトリに入れます」と伝えて OK をもらう

以降は、決まったリポジトリのフォルダの中で作業する。

## ステップ 4/7：Claude と GitHub をつなぐ（鍵の設定）

ここだけは、相手自身に操作してもらう。

**かんたんな方法（おすすめ）**：このまま Claude Code の入力欄に、相手自身が次を入力する。

```
/install-github-app
```

このとき、次のように選ぶよう伝える。

- 対象のリポジトリ：ステップ 3 で決めた `<ユーザー名>/<リポジトリ名>`。別のリポジトリが表示されていたら書き換えてもらう（練習用を新しく作った場合は特に注意）
- インストールするワークフロー：「@Claude Code」と「Claude Code Review」の**両方**
- 鍵：Claude の有料プラン（Pro / Max など）を使っているなら「サブスクリプションのトークン」、API キーで使っているなら「API キー」
- 最後にブラウザで PR の画面が開くので「Create pull request」を押し、続けて「Merge pull request」を押す

終わったら、確認する。

```bash
gh secret list
ls .github/workflows/ 2>/dev/null || true
```

`CLAUDE_CODE_OAUTH_TOKEN` か `ANTHROPIC_API_KEY` のどちらかがあれば成功。手元のフォルダを最新にするため `git pull` もしておく。

**うまくいかないときの手動の方法**：

1. ブラウザで https://github.com/apps/claude を開き、このリポジトリに Claude GitHub App をインストールしてもらう
2. 相手自身に **別のターミナルで** `claude setup-token` を実行してもらい、表示されたトークンを、続けて `gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo <ユーザー名>/<リポジトリ名>` を実行して貼り付けてもらう（API キーを使う場合は名前を `ANTHROPIC_API_KEY` にする）。トークンはこの会話には貼らない
3. `templates/workflows/claude.yml` と `templates/workflows/claude-review.yml` を `.github/workflows/` にコピーする

## ステップ 5/7：依頼書と作業マニュアルを入れる

1. 次をコピーする（同じ名前のファイルがすでにあれば上書きせず相談する）
   - `templates/workflows/claude-label.yml` → `.github/workflows/claude-label.yml`
   - `templates/claude-task.yml` → `.github/ISSUE_TEMPLATE/claude-task.yml`
2. CLAUDE.md を作る。次の4つを1つずつ聞いて、`templates/CLAUDE.md` の `{{...}}` を埋める
   - `{{PROJECT_SUMMARY}}`：これは何のためのものか（1〜2文）
   - `{{AUDIENCE}}`：誰が使う／見るものか
   - `{{OWNER}}`：呼び名（例：「持ち主の〇〇さん」）
   - `{{DO_NOT_TOUCH}}`：触ってほしくないもの（なければ「特になし」でよい。リストの形で書く）
   - `{{CHECK_COMMANDS}}`：相手には聞かず、フォルダの中を見て決める。`package.json` に test や lint があればそのコマンドを、なければ「変更したページをブラウザで開いて、崩れていないことを確かめる」のような確認方法を書く
   既存の CLAUDE.md があるときは、「守ってほしいルール」と「触らないでほしい場所」だけを追記する案を見せて OK をもらう
3. `claude` ラベルを作る
   ```bash
   gh label create claude --color 7057ff --description "Claude に作業を任せてOK" --force
   ```
4. 変更を反映する
   - 練習用（A）なら、そのままコミットして push する
   - 既存のリポジトリ（B）なら、ブランチ `setup/issue-dev` を作ってコミット・push し、`gh pr create` で PR を作る。PR の画面の見方（「Files changed」タブで変更が見える）を教え、相手の OK をもらってから `gh pr merge --squash --delete-branch` でマージする

## ステップ 6/7：安全の設定（任意）

- 公開リポジトリ、または GitHub の有料プランなら、main ブランチの保護（直接書き換え禁止、PR 必須）をすすめる。OK なら次を実行する
  ```bash
  gh api -X PUT repos/{owner}/{repo}/branches/<メインのブランチ名>/protection \
    -F required_pull_request_reviews[required_approving_review_count]=0 \
    -F enforce_admins=false -F required_status_checks=null -F restrictions=null
  ```
  無料プランの非公開リポジトリでは使えないので、その場合は「マージは必ず自分で中身を見てから」を約束にする
- 練習用で公開リポジトリなら、GitHub Pages でページを公開できる。希望があれば
  ```bash
  gh api -X POST repos/{owner}/{repo}/pages -f build_type=legacy -f "source[branch]=main" -f "source[path]=/"
  ```
  を実行し、1〜2分後に `https://<ユーザー名>.github.io/<リポジトリ名>/` で見られると伝える

## ステップ 7/7：最初の依頼を一緒に出す

1. 「最初の依頼書を一緒に書きましょう」と言い、`/issue-dev:new-issue` スキルの手順で Issue を作る（練習用なら「自己紹介の文章を入れてほしい」などの小さな依頼をすすめる）
2. `claude` ラベルを付けたら、`gh run list --limit 3` で動き出したことを確認し、ブラウザで Issue を開いて見てもらう（`gh issue view <番号> --web`）
3. 数分で Issue に Claude の報告コメントが届く。そこにある「Create PR」のリンクから提出物（PR）を作り、中身を見てマージする流れを、実際の画面で一緒に確認する

## 締めくくり

最後に、毎日の使い方を3行でまとめて伝える。

1. Issue に依頼書を書く（`/issue-dev:new-issue` を使うと楽）
2. `claude` ラベルを付ける → 報告が届いたら PR を作って中身を見る
3. 直してほしければ PR に `@claude ここをこう直して`、よければマージ

困ったら `/issue-dev:check` で状況を確認できること、Claude が同じミスをしたら CLAUDE.md に1行足すとよいことも伝える。
