---
name: automerge
description: 自動マージのモード（off／shadow＝練習／on＝本番）や条件（変更の大きさ、守るファイル）を、これまでの判定の記録を見せながら、開発経験のない人と相談して変える。「自動マージを本番にしたい」「自動マージを止めたい」「関門の条件を変えたい」と言われたときに使う。
argument-hint: "[off | shadow | on | status]"
---

# 自動マージの設定を変える

ルールは `.github/harness/policy.json` にあり、**main ブランチ上のものだけ**が判定に使われます。
変更は必ず PR にして、相手に中身を見てもらってから、相手の OK でマージします（このファイルの変更は、関門が自動マージしません）。

## 1. いまの状態と、これまでの記録を見せる

```bash
git fetch -q origin && git show "origin/$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name):.github/harness/policy.json"
```

最近の関門コメントを集計する（直近 30 件の PR）。

```bash
for n in $(gh pr list --state all --label claude-auto --limit 30 --json number --jq '.[].number'); do
  gh api "repos/{owner}/{repo}/issues/$n/comments" --jq '.[] | select(.body | startswith("<!-- harness-gate -->")) | .body' | head -2 | tail -1 | sed "s/^/#$n /"
done
git log --since="30 days ago" --grep='^Revert' --oneline
```

次の数字を、わかる言葉で伝える。

- 関門を通った（または練習モードで「通っていた」）PR の数と、通らなかった数
- 通らなかった理由で多いもの（例：守るファイルに触れた、レビューで指摘あり）
- 練習モードで「通っていた」のに、人が見たら直しが必要だったもの（相手に覚えがあるか聞く）
- 元に戻した（Revert した）変更の数

## 2. 相手と決める

引数があれば、それを第一案にする。

- **on（本番）にする目安**：練習モードで 10 件以上判定し、「通っていた」ものに人が直したくなる問題がほぼなかったとき。まだ少なければ、もう少し練習を続けることをすすめる（無理に止めはしない。決めるのは相手）
- **off にする**：心配なことがあったとき、すぐに止めたいとき。理由は聞かずにすぐ対応する
- **条件を変える**：`max_changed_files`、`max_changed_lines`、`protected_paths`、`allowed_risk`。ゆるめる提案は控えめにし、ゆるめるときは何が起こりうるかを1文で伝える。`allowed_risk` に `high` を入れる提案はしない

## 3. PR にする

```bash
git checkout -b harness/automerge-<mode>
# policy.json を書き換える（mode や条件だけ。ほかは変えない）
python3 -m json.tool .github/harness/policy.json >/dev/null   # 壊れていないか確認
git commit -am "自動マージの設定を変更：<内容>"
git push -u origin HEAD
gh pr create --title "自動マージの設定を変更：<内容>" --body "<変更点と理由をわかる言葉で>"
```

PR の画面で変更を見てもらい、OK ならマージしてもらう（`gh pr merge --squash --delete-branch` を相手の OK のあとに実行してもよい）。
**マージされた時点から**、新しいルールで判定されることを伝える。

## いますぐ止めたいとき

設定を変える PR を待たずに止める方法も伝える。

- 1つの PR だけ止める：その PR に `hold` ラベルを付ける（`gh pr edit <番号> --add-label hold`）
- 全部止める：上の手順で `mode` を `off` にする。急ぐときは、GitHub の Actions タブで「Claude（自動マージの関門）」を開き、右上の「…」→「Disable workflow」
