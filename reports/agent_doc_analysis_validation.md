# CLAUDE.md/AGENTS.md内容分析(構造ベース)の設計妥当性レポート

**調査日**: 2026-09-06
**調査範囲**: SPEC.md「CLAUDE.md/AGENTS.md内容分析(構造ベース)」の8項目
**調査対象**: `config/targets.yaml`記載の全20リポジトリ
**方針**: 設計(`src/agent_trend_radar/agent_doc_analysis.py`, SPEC.md)は変更せず、
現行ロジックを実データに適用した結果を検証するのみ。

## 方法論

- 各リポジトリの`CLAUDE.md` / `AGENTS.md` / `.cursorrules`を
  `raw.githubusercontent.com`経由で取得(GitHub API未認証レート制限を
  回避するため。本番の`GitHubClient`はContents APIを使うため取得経路は
  異なるが、ファイル内容そのものは同一)
- `agent_doc_analysis.py`の実装(`fetch_agent_doc_content`のシンボリック
  リンク重複除去ロジックを含む)をそのまま適用し、8項目の値を算出
- 値が意外だったリポジトリについては、実際のファイル内容を目視で確認し、
  キーワード一致の妥当性(見逃し/誤検知)を個別に検証

## 全体結果

| repo | 存在 | char数 | 見出し数 | code block | test | lint | security | commit規約 | tool利用 |
|---|---|---|---|---|---|---|---|---|---|
| langchain-ai/langchain | ✓ | 19,506 | 36 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Significant-Gravitas/AutoGPT | ✓ | 3,822 | 6 | - | ✓ | ✓ | - | ✓ | ✓ |
| microsoft/autogen | - | 0 | 0 | - | - | - | - | - | - |
| crewAIInc/crewAI | ✓ | 1,867 | 4 | ✓ | ✓ | - | - | - | - |
| Aider-AI/aider | - | 0 | 0 | - | - | - | - | - | - |
| cline/cline | ✓ | 5,263 | 6 | - | ✓ | ✓ | ✓ | - | - |
| continuedev/continue | - | 0 | 0 | - | - | - | - | - | - |
| OpenHands/OpenHands | ✓ | 120,034 | 32 | ✓ | ✓ | ✓ | ✓ | - | ✓ |
| browser-use/browser-use | ✓ | 49,587 | 129 | ✓ | ✓ | ✓ | ✓ | - | ✓ |
| yoheinakajima/babyagi | - | 0 | 0 | - | - | - | - | - | - |
| apache/airflow | ✓ | 35,685 | 31 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| getsentry/sentry | ✓ | 7,491 | 24 | ✓ | ✓ | ✓ | - | ✓ | ✓ |
| vercel/next.js | ✓ | 30,660 | 60 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| supabase/supabase | ✓ | 6,554 | 7 | ✓ | ✓ | ✓ | - | - | ✓ |
| oven-sh/bun | ✓ | 17,624 | 20 | ✓ | ✓ | - | - | - | - |
| sveltejs/svelte | ✓ | 590 | 2 | - | ✓ | - | - | - | ✓ |
| nuxt/nuxt | ✓ | 960 | 1 | - | - | - | - | - | ✓ |
| astral-sh/ruff | ✓ | 16,912 | 25 | ✓ | ✓ | ✓ | - | - | ✓ |
| colinhacks/zod | ✓ | 24,146 | 20 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| remix-run/remix | ✓ | 8,319 | 10 | - | ✓ | ✓ | - | ✓ | ✓ |

**存在率**: 20リポジトリ中14件(70%)が実際にCLAUDE.md/AGENTS.mdを保有していた。
これはSPEC.mdの選定基準で保有を確認していたadopter 10件を上回る。tool
セグメントのうちAutoGPT/crewAI/cline/OpenHands/browser-useも保有しており、
選定時には意図していなかった副次的な発見。

## 発見1: 「存在する」と「独自の内容がある」は別物

`has_agent_instructions`はCLAUDE.md/AGENTS.md/.cursorrulesのいずれかの
存在だけを見るが、実際にCLAUDE.mdとAGENTS.mdの両方が存在するケースを
内容面で分類すると、少なくとも3パターンに分かれることが分かった。

1. **gitシンボリックリンク**(内容が完全一致): apache/airflow,
   colinhacks/zod(CLAUDE.md→AGENTS.md)、oven-sh/bun(AGENTS.md→CLAUDE.md、
   向きが逆)、vercel/next.js。raw fetchすると target のファイル名
   (例: `AGENTS.md`)がそのまま9〜11バイトの内容として返る
2. **Claude Codeの`@import`構文**(`@AGENTS.md`という11バイトのテキスト
   ファイル。gitシンボリックリンクではない): Significant-Gravitas/AutoGPT,
   astral-sh/ruff, getsentry/sentry, nuxt/nuxt, supabase/supabase。
   これはGitHub側では解決されない、Claude Code実行時にのみ解決される
   参照なので、GitHub API/raw fetchのどちらで取得しても中身は
   `@AGENTS.md`という文字列のまま
3. **短い誘導文**(内容は独立しているが数百バイト程度): remix-run/remix
   のCLAUDE.md(469バイト、"Follow the repository guidance in `AGENTS.md`")
4. **真に独立した内容**: browser-use/browser-use(CLAUDE.md 11,149バイトと
   AGENTS.md 38,463バイトが別内容)、langchain-ai/langchain(CLAUDE.mdと
   AGENTS.mdが完全に同一内容・同一サイズだが、シンボリックリンクではなく
   実体コピーの可能性がある)

`agent_doc_char_count`/`agent_doc_heading_count`はこの「内容の実質量」を
測るために導入した指標であり、実際に機能していることを確認できた
(例: nuxt/nuxt=960文字/1見出し vs apache/airflow=35,685文字/31見出し)。
一方で#5実装時に修正した重複排除ロジック(パターン1のケース)がなければ、
これらの指標は簡単に水増しされていたはずで、修正の必要性が実データで
裏付けられた。

## 発見2: 項目ごとの精度評価

### 概ね機能していた項目

- `agent_doc_char_count` / `agent_doc_heading_count`: 意図通り、内容の
  分量差を素直に反映していた
- `agent_doc_mentions_test`: 誤検知・見逃しは確認されなかった
- `agent_doc_mentions_security`: getsentry/sentryとsupabase/supabaseで
  falseだったが、実際に内容を確認したところ両者ともセキュリティ/権限/
  PIIに関する実質的な記述がなく(sentryは「サンドボックス権限」の
  一行のみ)、これは見逃しではなく妥当なfalseだった

### 見逃し(false negative)を確認した項目

- **`agent_doc_has_code_block`**: remix-run/remixとcline/clineは共に
  具体的なコマンド例を豊富に含むが、いずれもインラインの単一バッククォート
  (`` `pnpm test` `` のような書式)で記載しており、3連バッククォートの
  コードブロックを使っていなかったため`false`になった。コマンド例の
  提示方法として「インラインコード」は珍しくないため、これは設計上の
  見逃しと言える
- **`agent_doc_mentions_commit_convention`**: astral-sh/ruffには
  `### PR conventions`という見出しでPRタイトルのプレフィックス規約
  (`[ty]`等)やラベル運用が明記されているが、「commit message」
  「conventional commit」という文言を使っていないため`false`になった。
  oven-sh/bunも`## Landing PRs: What Bun Reviewers Catch`という見出しで
  詳細なPRレビュー基準(ブランチ命名規則、レビューで指摘される観点等)を
  記載しているが同様に`false`。この項目は「コミットメッセージの書式」
  よりも「PR/ブランチ命名・レビュー基準」の方が実際の記述頻度が高く、
  現在のキーワードセットは実態を捉えきれていない

### 誤検知(false positive)寄りの挙動を確認した項目

- **`agent_doc_mentions_tool_usage`**: nuxt/nuxtのAGENTS.mdは
  「`SKILL.md`という別プロジェクトのファイルを読んで従うこと」という
  AI生成コンテンツ禁止方針の文書で、Claude Code的な「Skill機能の使い方」
  とは無関係だが、`skill`という文字列一致により`true`と判定された。
  意味的な誤検知だが、キーワード一致方式である以上は避けにくい

## 発見3: 現在の8項目でカバーされていない頻出テーマ

実際のファイルを見出しベースで一覧した結果、以下のテーマが複数の
リポジトリで繰り返し登場するが、現在の8項目のどれにも対応しない。

1. **リポジトリ構造/モノレポの境界説明**(最頻出): OpenHands
   "Repository Map — what belongs where"、langchain "Monorepo structure"、
   vercel/next.js "Codebase structure"、remix "Repo Shape"、supabase
   "Structure"など、確認した14件中8件以上で最初のセクションとして登場
2. **「してはいけないこと」の境界線**: OpenHands "Cross-Repository
   Boundaries" "No Magic Strings"、apache/airflow "Architecture
   Boundaries" "Security Model"、langchain "Corridor security analysis"。
   エージェントの自律性を制限する重要な情報だが、`mentions_security`は
   「セキュリティ」という言葉自体がないと拾えないため、これらの一部
   (Boundaries系)は捕捉できない
3. **PRレビュー基準・人間チェックポイント**: OpenHands "PR Description
   Human Check"、oven-sh/bun "Landing PRs: What Bun Reviewers Catch"、
   apache/airflow "Golden rule: when a fix is imminent, open the PR, not
   an issue"。エージェントがどこまで自律的に振る舞ってよいかの境界線
   であり、発見2の見逃しとも関連するテーマ
4. **リリース/デプロイ手順**: colinhacks/zod "Cutting a release"、
   astral-sh/ruff "Generated Release Workflow"、remix "Release Notes"

## 結論

- ルールベースのキーワード一致は、**単語自体が本文に出現する**項目
  (test/lint/security)では概ね機能する
- 一方で、**同じ概念でも表現のバリエーションが大きいテーマ**
  (PR/コミット規約、エージェントの自律境界)では見逃しが目立つ。
  キーワードを増やすほど今度は誤検知(nuxtのSKILL.md例)のリスクも
  上がるため、フレーズ拡充だけで根本解決するかは疑わしい
- 「リポジトリ構造の説明」「してはいけないことの境界線」「人間による
  レビュー・チェックポイント」は、今回確認した実データで最も頻出した
  にもかかわらず現行8項目でカバーされていないテーマ

本レポートでは設計変更を行っていない。次のアクションを検討する場合の
選択肢を並べる(優先順位は付けていない)。

- **A. キーワードセットの拡充**: `mentions_commit_convention`に
  "pr title" "pr convention" "branch naming" 等を追加する。決定的な
  手法のまま改善できるが、語彙の網羅性は原理的に有限
- **B. 新しいルールベース項目の追加**: 例えば`agent_doc_mentions_
  boundaries`(don't/never/boundary/scope等)や`agent_doc_mentions_pr_
  review`のような項目を増やす
- **C. `agent_doc_has_code_block`の判定方法見直し**: 3連バッククォートに
  加えて、インラインコード(単一バッククォート)の出現数もカウントする
- **D. LLMによる分類への切り替え**: 表現のバリエーションに強いが、
  CLAUDE.md/SPEC.mdが明記する「収集は決定的に行う」方針との兼ね合いを
  再検討する必要がある(以前の議論の再燃)
