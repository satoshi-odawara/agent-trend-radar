# SPEC.md

agent-trend-radarが分析する対象と項目の仕様。見直し方針はCLAUDE.mdを参照。

## 何をするか
選定した公開リポジトリ群に対し、「AIエージェント開発の品質・セキュリティ・
運用に関わる特定ファイル/ディレクトリが存在するか」を機械的にチェックし、
リポジトリ×項目のマトリクスを作る。存在有無の傾向から、実プロジェクトでの
使われ方を読み取る。

## 対象リポジトリの選定基準
以下の観点で、比較が面白くなるよう手動で10〜20個を選ぶ。自動選定は作らない。
- スター数(一定以上の実績があるもの)
- プロジェクト開始日(新しい/枯れている の対比)
- **収益化モデル(monetization_model)**: 商用圧力の有無・種類による運用成熟度の
  差を見る軸。以下の4区分で分類する(企業/個人という組織形態の軸は、
  Apache財団(非営利だがOrganization)や個人発→企業化の例(Ruff/Bun)で
  実態と乖離するため廃止した)
  - `commercial_saas`(商用SaaS展開済み): OSSに加え商用の有料プラン/
    エンタープライズ版が実在する
  - `big_corp_internal`(大企業の内製・戦略的公開): 大企業が自社戦略の一環で
    公開し、単体では収益化していない
  - `nonprofit_foundation`(非営利財団運営): Apache Software Foundation等
  - `individual_community`(個人・コミュニティ非営利): 商用展開のない個人/
    コミュニティ運営
- **区分(segment)**: `tool`(AIエージェント/LLMツール自体) と
  `adopter`(AIエージェントを使って開発されている一般プロダクト。
  CLAUDE.md/AGENTS.md等の採用が公知の事例のみを選ぶ)を半々程度で混在させ、
  「ツール開発元自身の運用成熟度」と「ツールを使う側の運用成熟度」の両方が
  比較できるようにする
- 対象言語エコシステムはPython + TypeScript/JavaScriptに限定する
  (`has_observability_dep`のマニフェスト解析対象を絞るため)

## 対象リポジトリリスト(初期・手動)

owner/repoのGitHub API実データ(スター数・作成日)、および各社の資金調達・
商用プラン有無はWeb検索で裏取り済み(2026-09-06時点)。

| owner/repo | segment | 収益化モデル | stars | 開始日 | 備考 |
|---|---|---|---|---|---|
| langchain-ai/langchain | tool | commercial_saas | 145,734 | 2022-10-17 | LangSmith/LangGraph Platformを商用展開 |
| Significant-Gravitas/AutoGPT | tool | commercial_saas | 187,163 | 2023-03-16 | $12M調達・hosted Platform展開。価格詳細は非公開で確度はやや低め |
| microsoft/autogen | tool | big_corp_internal | 60,827 | 2023-08-18 | Microsoft Researchの研究成果。単体商用製品ではない |
| crewAIInc/crewAI | tool | commercial_saas | 58,133 | 2023-10-27 | $18M調達、Enterprise Agent Management Platformを課金展開 |
| Aider-AI/aider | tool | individual_community | 48,774 | 2023-05-09 | Paul Gauthier個人開発、商用プラン確認できず |
| cline/cline | tool | commercial_saas | 67,541 | 2024-07-06 | $32M調達、Cline Teams(エンタープライズ版)を展開 |
| continuedev/continue | tool | commercial_saas | 35,784 | 2023-05-24 | $5.1M調達、Continue Hub(有料ティア)を展開 |
| OpenHands/OpenHands | tool | commercial_saas | 86,292 | 2024-03-13 | All Hands AI社が$23.8M調達、OpenHands Cloudを課金展開 |
| browser-use/browser-use | tool | commercial_saas | 112,416 | 2024-10-31 | $17M調達(YC出身)、Cloud APIを従量課金展開 |
| yoheinakajima/babyagi | tool | individual_community | 22,356 | 2023-04-03 | 個人アカウント(User)所有、商用展開なし |
| apache/airflow | adopter | nonprofit_foundation | 46,749 | 2015-04-13 | Apache Software Foundation運営 |
| getsentry/sentry | adopter | commercial_saas | 44,732 | 2010-08-30 | 対象中最古(2010年〜)。商用SaaS(エラートラッキング)で著名 |
| vercel/next.js | adopter | commercial_saas | 142,129 | 2016-10-05 | Vercelの商用ホスティングプラットフォームと連動 |
| supabase/supabase | adopter | commercial_saas | 108,887 | 2019-10-12 | Supabase社の商用ホスティングDBサービス |
| oven-sh/bun | adopter | commercial_saas | 95,891 | 2021-04-14 | $7M調達(Oven社)。サーバーレスホスティング事業を計画・展開中 |
| sveltejs/svelte | adopter | individual_community | 88,060 | 2016-11-20 | コミュニティ運営、フレームワーク自体は非収益化。AGENTS.mdのみ採用 |
| nuxt/nuxt | adopter | individual_community | 60,823 | 2016-10-26 | 2025年Vercelに買収されたNuxtLabsの有料製品群は無償OSS化済み |
| astral-sh/ruff | adopter | commercial_saas | 49,511 | 2022-08-09 | Astral社が$4M調達、有料エンタープライズ版pyxを展開 |
| colinhacks/zod | adopter | individual_community | 43,847 | 2020-03-07 | 個人アカウント(User)所有、商用展開なし |
| remix-run/remix | adopter | big_corp_internal | 33,359 | 2020-10-26 | Shopifyが買収・内製。単体商用製品ではない |

## チェック項目(ファイル/ディレクトリの存在有無)

| 項目キー | 対象パス例 | 何が分かるか |
|---|---|---|
| has_agent_instructions | CLAUDE.md / AGENTS.md / .cursorrules | AIエージェントへの指示を管理しているか |
| has_tests | tests/ | テストを備えているか |
| has_eval | evals/ / eval/ | エージェントの評価を行っているか |
| has_ci | .github/workflows/ | CI/CDを回しているか |
| has_security_policy | SECURITY.md | セキュリティ方針を明示しているか |
| has_observability_dep | 依存に既知の可観測性パッケージ(下記) | トレース/可観測性を導入しているか |

※ 項目は運用しながら追加・削除してよい。

### 既知の制限(2026-09-06実データ通し実行で確認)

`has_tests` / `has_observability_dep` はリポジトリ直下(ルート)のパス・
マニフェストのみを見る設計のため、モノレポ構成のリポジトリでは実際には
サブディレクトリ配下にテストや依存が存在していても false と判定される
(20リポジトリ中16件で `has_tests=false`。例: astral-sh/ruff、
langchain-ai/langchain、apache/airflow、supabase/supabase、
crewAIInc/crewAI、continuedev/continue、microsoft/autogen。
vercel/next.jsはルート直下に`tests`ではなく`test`(単数形)ディレクトリを
持つため同様にfalseになる)。`has_security_policy`についても、GitHub組織の
`.github`特別リポジトリにSECURITY.mdを置いて継承表示しているケース
(apache/airflow、langchain-ai/langchain等)を拾えない。MVPでは
CLAUDE.mdのシンプルさ優先方針に基づく意図的な割り切りとして許容している
(Issue #14参照)が、データを解釈する際はこの制約を踏まえること。

### has_observability_depの判定対象パッケージ

`pyproject.toml` / `requirements.txt` / `package.json` のうち存在するものを
読み込み、以下のパッケージ名との文字列一致(大小文字無視)があれば true と
判定する。複雑な依存パーサは作らない(CLAUDE.mdのシンプルさ優先方針に従う)。

- `langsmith`(LangChain社、Python/npm両方に存在)
- `langfuse`(Python/npm両方に存在)
- `traceloop-sdk` / `traceloop`(OpenLLMetry)
- `arize-phoenix`(Arize Phoenix、Python)
- `helicone`(Python/npm両方に存在)
- `promptlayer`(Python)

※ このリストは運用しながら見直してよい(CLAUDE.mdの見直し方針を参照)。

## CLAUDE.md/AGENTS.md内容分析(構造ベース)

`has_agent_instructions`とは別に、CLAUDE.md/AGENTS.mdの中身についても
ルールベースで分析する(LLMは使わない)。CLAUDE.mdとAGENTS.mdの両方が
存在する場合は内容を連結した上で1回分析する。どちらも存在しない場合は
`agent_doc_char_count`=0、`agent_doc_heading_count`=0、その他の真偽値項目は
すべてfalseとする。

| 項目キー | 何が分かるか | 判定方法 |
|---|---|---|
| agent_doc_char_count | 内容の充実度 | 文字数(数値) |
| agent_doc_heading_count | 構成の複雑さ | Markdown見出し(`#`で始まる行)の数(数値) |
| agent_doc_has_code_block | 具体的なコマンド例があるか | \`\`\`コードブロックの有無 |
| agent_doc_mentions_test | テスト実行方法への言及 | キーワード一致(大小文字無視): test, pytest, jest, vitest |
| agent_doc_mentions_lint | Lint/フォーマットへの言及 | キーワード一致: lint, ruff, eslint, prettier |
| agent_doc_mentions_security | セキュリティ上の注意点への言及 | キーワード一致: security, secret, credential, vulnerability |
| agent_doc_mentions_commit_convention | コミット規約への言及 | キーワード一致: commit message, conventional commit |
| agent_doc_mentions_tool_usage | Skill/MCP/サブエージェント等の拡張機能の使い方への言及 | キーワード一致: mcp, skill, subagent, slash command, hook, tool use, function calling |

※ このリストは運用しながら見直してよい(CLAUDE.mdの見直し方針を参照)。

## データスキーマ
| 項目 | 内容 |
|---|---|
| repo | owner/repo |
| segment | tool / adopter |
| monetization_model | commercial_saas / big_corp_internal / nonprofit_foundation / individual_community |
| checked_at | チェック実行日 |
| (ファイル存在系チェック項目キー) | 真偽値(存在する=true) |
| (CLAUDE.md/AGENTS.md内容分析キー) | 数値(char_count/heading_count) または真偽値 |

## 保存形式
- SQLite、テーブル名: `repo_checks`
- 1レコード = 1リポジトリ×1回のチェック