# claude-issue-dev-starter

**GitHub に「依頼書」を書くと、Claude が作業し、別の Claude が確かめ、決まったルールを満たしたものは自動でマージされる。** そんな仕組みを、開発をしたことがない人でも自分のプロジェクトに入れられるようにするスターターです。

このリポジトリは **Claude Code のスキル集（プラグイン）** です。`git clone` して Claude Code に読み込ませると、Claude があなたに話しかけながら、設定を一歩ずつ進めてくれます。

考え方の土台は、2026年に広まった **「ハーネスエンジニアリング」**（AI に、指示書・機械のチェック・関門という「手綱と安全ベルト」を付けて、安心して任せられるようにする考え方）です。くわしくは [ハーネスと自動マージのしくみ](docs/07-harness.md) へ。

---

## これで何ができるの？

会社にたとえると、こんな感じです。

| GitHub での名前 | たとえると |
|---|---|
| リポジトリ | プロジェクトの共有フォルダ |
| Issue（イシュー） | 依頼書 |
| `claude` ラベル | 「作業して。マージは自分でする」のハンコ |
| `claude-auto` ラベル | 「作業して。条件を全部満たしたら自動でマージしてよい」のハンコ |
| 作業役の Claude | 依頼書を読んで作業する担当 |
| レビュー役の Claude | 作業役とは別に、提出物を確かめる担当 |
| 関門（ゲート） | 決まったルールで「マージしてよいか」を判定する係（AI ではない） |
| PR（プルリクエスト） | 提出物と「確認お願いします」 |
| マージ | 承認して、本番に反映すること |

```mermaid
flowchart LR
    A["あなた<br>依頼書を書く"] --> B["ラベルを付ける<br>claude / claude-auto"]
    B --> C["作業役 Claude<br>作って、自分でチェック"]
    C --> D["PR ができる"]
    D --> E["機械のチェック"]
    D --> F["レビュー役 Claude"]
    E --> G{"関門<br>決まったルール"}
    F --> G
    G -->|条件をすべて満たす| H["自動マージ"]
    G -->|ひとつでも満たさない| I["あなたが確認"]
    I -->|@claude 直して| C
    I -->|OK| J["マージ"]
```

**最初は「練習モード」で始まります。** 関門は「本番なら自動マージされていました」とコメントするだけで、マージはあなたがします。判定が信頼できると思えたら、本番に切り替えます。

---

## 必要なもの

- GitHub のアカウント（無料でOK。公開リポジトリなら、main を守る設定も無料で使えます）
- Claude の有料プラン（Pro / Max / Team / Enterprise）か、Claude Console の API キー
- パソコン（Mac か Windows）と、Claude Code

まだ何も入っていない人は、[準備のしかた](docs/02-prepare.md) を先に見てください。15分くらいで終わります。

---

## はじめかた（3ステップ）

### 1. このスキル集を取り込む

ターミナル（Mac は「ターミナル」、Windows は「PowerShell」）を開いて、次の1行をコピーして貼り付け、Enter を押します。

**Mac**

```bash
git clone https://github.com/Kambara-Michiru/claude-issue-dev-starter.git ~/.claude/skills/issue-dev
```

**Windows（PowerShell）**

```powershell
git clone https://github.com/Kambara-Michiru/claude-issue-dev-starter.git "$HOME\.claude\skills\issue-dev"
```

> `~/.claude/skills/` は、Claude Code が「いつも使うスキル」を探しに行く場所です。ここに置くと、次に Claude Code を起動したときから自動で読み込まれます。

<details>
<summary>別の取り込み方（プラグインとして入れる）</summary>

Claude Code を起動して、入力欄に次の2行を1行ずつ入力します。

```
/plugin marketplace add Kambara-Michiru/claude-issue-dev-starter
/plugin install issue-dev@claude-issue-dev-starter
```

この方法だと、更新も `/plugin` の画面からできます。
</details>

### 2. Claude Code を起動して、セットアップを頼む

書類フォルダなど、練習用のプロジェクトを置きたい場所で Claude Code を起動し、次のように入力します。

```
/issue-dev:setup practice
```

`practice` を付けると、**練習用の新しいリポジトリ**を作るところから始めます。すでにあるプロジェクトに入れたいときは、そのフォルダで `/issue-dev:setup here` と入力します。

あとは Claude の質問に答えていくだけです。全部で8ステップ、40分くらいです。

### 3. 最初の依頼を出してみる

セットアップの最後に、Claude と一緒に最初の依頼書を書き、`claude-auto` ラベルを付けます。依頼書に報告が届き、PR にレビューと関門の判定（✅ と ❌ の表）が付いたら成功です。

---

## 入っているスキル

| 入力するもの | していること |
|---|---|
| `/issue-dev:setup` | 仕組み（ハーネス）をリポジトリに入れる（最初の1回） |
| `/issue-dev:new-issue` | やってほしいことを聞き取って、Claude が作業しやすい依頼書にする |
| `/issue-dev:check` | 作業中の依頼、届いた提出物、関門の判定、うまくいかなかった実行を、わかる言葉で報告する |
| `/issue-dev:automerge` | 自動マージを 練習（shadow）／本番（on）／停止（off）に切り替える。条件も相談して変えられる |

セットアップが終わると、あなたのリポジトリに次のファイルが入ります。

```
あなたのリポジトリ/
├── CLAUDE.md                       … Claude への「地図」（短く保つ）
├── docs/agent/
│   ├── product.md                  … 誰のための何か、大事にしていること
│   └── lessons.md                  … これまでに覚えたこと
├── scripts/check.sh                … 機械のチェック（失敗したら直し方を表示）
└── .github/
    ├── ISSUE_TEMPLATE/claude-task.yml  … 依頼書のひな形
    ├── harness/
    │   ├── policy.json             … 自動マージのルール（モード、条件、守るファイル）
    │   └── gate.py                 … 関門の判定役（AI ではなく決まったルール）
    └── workflows/
        ├── claude-work.yml         … ラベルで作業 → PR を作る
        ├── claude-verify.yml       … 機械のチェック ＋ レビュー役の Claude
        ├── claude-gate.yml         … 関門で判定 → 自動マージ（main の版で動く）
        ├── claude.yml              … @claude で呼ぶと返事・修正をする
        └── claude-gardener.yml     … 週1回のハーネス点検（改善の提案を Issue に）
```

---

## もっと知りたい人へ

1. [全体像と用語](docs/01-overview.md)：GitHub と Claude が何をしているのか
2. [準備のしかた](docs/02-prepare.md)：アカウント作りとインストール
3. [依頼書（Issue）の書き方](docs/03-writing-issues.md)：うまくいく依頼、いかない依頼
4. [毎日の使い方](docs/04-daily-use.md)：ラベルの使い分け、関門の表の読み方、直してもらい方
5. [安全と費用](docs/05-safety-and-cost.md)：お金と安全の話、自動マージを止める方法
6. [困ったとき](docs/06-troubleshooting.md)：動かないときのチェックリスト
7. [ハーネスと自動マージのしくみ](docs/07-harness.md)：なぜこの形なのか（2026年の考え方）

---

## 更新するとき

```bash
git -C ~/.claude/skills/issue-dev pull
```

スキル集を更新しても、すでにセットアップしたリポジトリのファイルは変わりません。新しい版を入れたいときは、そのリポジトリで `/issue-dev:setup here` を実行し、違いを見ながら更新します。

## 自分用に改造したいとき

このリポジトリを自分のアカウントにコピー（Fork または「Use this template」）して、`skills/` の中の `SKILL.md` やテンプレートを書き換えてください。関門のルールを変えたときは `python3 tests/test_gate.py` と `bash tests/test_check.sh` で確かめられます。

## 参考にした公式情報

- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions) / [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- [Claude Code のスキル](https://code.claude.com/docs/en/skills) / [プラグイン](https://code.claude.com/docs/en/plugins/create)
- [スケジュールタスク（旧 Routines）](https://code.claude.com/docs/en/routines)
- ハーネスエンジニアリングの参考記事は [docs/07-harness.md](docs/07-harness.md#もっと知りたい人へ参考にした記事) に

仕様は変わることがあります。内容は 2026年11月時点のものです。

## ライセンス

MIT
