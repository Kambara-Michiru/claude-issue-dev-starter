# 4. 毎日の使い方

## 基本の流れ

```mermaid
sequenceDiagram
    actor U as あなた
    participant Issue as Issue（依頼書）
    participant C as Claude
    participant PR as PR（提出物）
    U->>Issue: 依頼書を書く
    U->>Issue: claude ラベルを付ける
    Issue->>C: 作業開始の合図
    C->>Issue: 「作業中です」とコメント
    C->>Issue: 報告と「Create PR」リンク
    U->>PR: リンクから PR を作る
    PR->>C: 自動チェック（レビュー）
    C->>PR: 気になる点をコメント
    U->>PR: 中身を確認
    alt 直してほしい
        U->>PR: @claude ここを直して
        C->>PR: 直して追加で提出
    else OK
        U->>PR: Merge（本番に反映）
        PR->>Issue: 依頼書が自動で閉じる
    end
```

## 提出物（PR）の見方

開発の知識がなくても、次の4つを見れば判断できます。

1. **Conversation タブ**：Claude が書いた「何を変えたか」「どう確認するか」を読む
2. **Files changed タブ**：変わったところが緑（追加）と赤（削除）で表示されます。全部わからなくて大丈夫。「頼んでいないファイルが変わっていないか」だけ見ます
3. **チェックの結果**：PR の下のほうに ✓（成功）か ✗（失敗）が出ます。✗ のときはマージしないで、`@claude チェックが失敗しているので直して` とコメントします
4. **実際に動かしてみる**：Claude が書いた確認方法の通りに試します。Web ページなら、GitHub Pages や手元で開いて見てみます

## 直してもらうとき

PR のコメント欄に `@claude` を付けて書きます。

```
@claude 文章が少し硬いので、もう少しやわらかい言葉にして
@claude スマホで見ると画像がはみ出しているので直して
@claude 2つ目の完成の条件がまだできていないみたいです
```

特定の行について言いたいときは、「Files changed」タブでその行の横の **+** を押してコメントできます。

## マージのしかた

1. PR の下のほうにある緑の **Merge pull request**（または **Squash and merge**）を押す
2. **Confirm merge** を押す
3. 「Delete branch」と出たら押してOK（下書きのコピーを片付けるだけです）

PR の本文に `Closes #番号` があるので、マージすると依頼書（Issue）も自動で閉じます。

## カンバン（GitHub Projects）で管理する

依頼書が増えてきたら、GitHub Projects でカンバンボードにすると見やすくなります。

1. リポジトリの **Projects** タブ →「New project」→「Board」を選ぶ
2. 列を「Todo」「Claude 作業中」「確認待ち」「Done」にする
3. Project の右上の「…」→ **Workflows** で、次を ON にする
   - Item added to project → **Todo**
   - Pull request linked to issue → **確認待ち**（列名は自由）
   - Item closed / Pull request merged → **Done**
4. 依頼書に `claude` ラベルを付けたら「Claude 作業中」に動かす

優先順位や締め切りは人間が決め、Claude には作業だけを任せると、役割がはっきりします。

## 慣れてきたら：定期的に任せる（スケジュールタスク）

Claude の有料プランなら、**スケジュールタスク**（以前は Routines という名前でした）で、決まった時間や GitHub の出来事をきっかけに Claude を動かせます。あなたのパソコンが閉じていても、クラウドで動きます。

作り方は2つあります。

- ブラウザで https://claude.ai/code/routines を開く
- Claude Code で `/schedule` と入力し、やりたいことを話す（例：`/schedule 毎朝9時に、ready ラベルの付いた Issue を1つ選んで作業して`）

使い方の例：

- 毎朝、`ready` ラベルの依頼書を1件ずつ片付ける
- PR がマージされたら、お知らせ（CHANGELOG）を更新する
- 毎週、古くなった依頼書をまとめて報告する

注意点：

- スケジュールタスクは **あなた個人の claude.ai アカウント** に属し、チームとは共有されません
- スケジュールタスクが作るコミットや PR は **あなたの GitHub ユーザー** として記録されます
- 1時間に1回より短い間隔では動かせません

まずは、ラベルで頼む基本の流れに慣れてから試すのがおすすめです。

次は [安全と費用](05-safety-and-cost.md) へ。
