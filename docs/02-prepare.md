# 2. 準備のしかた

ここでは、まだ何も入っていないパソコンを、スキル集を使える状態にします。上から順に進めてください。

## 2-1. アカウントを用意する

| もの | どこで | メモ |
|---|---|---|
| GitHub アカウント | https://github.com/signup | 無料プランでOK |
| Claude のアカウント | https://claude.ai | Pro / Max / Team / Enterprise のどれか。または https://platform.claude.com で API キーを使う |

> 有料プランを使っている人は、GitHub 上の Claude もそのプランの範囲で動かせます（「サブスクリプションのトークン」を使う方法）。API キーの場合は、使った分だけ料金がかかります。

## 2-2. ターミナルを開く

- **Mac**：`command` + `スペース` で Spotlight を開き、「ターミナル」と入力して Enter
- **Windows**：スタートボタンを右クリック →「ターミナル」または「Windows PowerShell」

黒（または白）い画面に文字が打てる状態になれば OK です。このあとのコマンドは、**コピーして貼り付けて Enter** を押せば動きます。

## 2-3. Git を入れる

まず、入っているか確かめます。

```bash
git --version
```

`git version 2.xx` のように表示されれば入っています。表示されなければ：

- **Mac**：`xcode-select --install` を実行し、出てきた画面で「インストール」を押す
- **Windows**：https://git-scm.com/downloads/win からダウンロードしてインストール（設定はすべて初期値のままでOK）

## 2-4. GitHub CLI（gh）を入れて、ログインする

GitHub をターミナルから操作する道具です。Claude が依頼書を作ったりするのに使います。

- **Mac**：[Homebrew](https://brew.sh) がある人は `brew install gh`。ない人は https://cli.github.com からダウンロード
- **Windows**：`winget install --id GitHub.cli`

入れたら、ターミナルを一度閉じて開き直し、ログインします。

```bash
gh auth login
```

質問には次のように答えます。

1. Where do you use GitHub? → **GitHub.com**
2. What is your preferred protocol? → **HTTPS**
3. Authenticate Git with your GitHub credentials? → **Yes**
4. How would you like to authenticate? → **Login with a web browser**

画面に出た8文字のコードをメモし、Enter を押すとブラウザが開くので、そのコードを入力します。

## 2-5. Claude Code を入れる

- **Mac**

  ```bash
  curl -fsSL https://claude.ai/install.sh | bash
  ```

- **Windows（PowerShell）**

  ```powershell
  irm https://claude.ai/install.ps1 | iex
  ```

終わったらターミナルを開き直して、確認します。

```bash
claude --version
```

数字が表示されれば OK。`claude` と入力して起動すると、最初にログインを求められるので、ブラウザで Claude のアカウントにログインします。

> うまくいかないときは、公式の [インストールのトラブル対応](https://code.claude.com/docs/en/troubleshoot-install) を見てください。

## 2-6. スキル集を取り込む

[README の「はじめかた」](../README.md#はじめかた3ステップ) に戻って、`git clone` から進めてください。

## チェックリスト

- [ ] `git --version` で数字が出る
- [ ] `gh auth status` で「Logged in to github.com」と出る
- [ ] `claude --version` で数字が出る
- [ ] `claude` を起動して、ログインできた

全部そろったら準備完了です。
