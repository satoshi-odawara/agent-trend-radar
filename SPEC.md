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
  (マニフェストファイル(pyproject.toml/package.json等)を用いる将来の
  分析対象を絞るため。当初は`has_observability_dep`のためだったが、
  同項目は#16で廃止した)

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
| has_tests | tests/ または test/(リポジトリ内の任意の深さ) | テストを備えているか |
| has_eval | evals/ / eval/ | エージェントの評価を行っているか |
| has_ci | .github/workflows/ | CI/CDを回しているか |
| has_security_policy | SECURITY.md | セキュリティ方針を明示しているか |
| has_skills_dir | .claude/skills/ または .agents/skills/ | 再利用可能なSkillを定義しているか |
| skills_count | 両パス直下の子要素数の和集合 | Skill定義の充実度 |
| has_custom_commands | .claude/commands/ | カスタムslash commandsを定義しているか |
| custom_commands_count | .claude/commands/配下の.mdファイル数 | カスタムcommand定義の充実度 |
| has_hooks_config | .claude/settings.jsonの`hooks`キー | エージェントの挙動を機械的に制約する仕組みがあるか |
| mcp_servers_count | .mcp.jsonの`mcpServers`の数 | 連携しているMCPサーバー数 |

※ 項目は運用しながら追加・削除してよい。
※ `has_skills_dir`〜`mcp_servers_count`の6項目は、「ルール化(CLAUDE.md等)
と対になるツール化の実態」を測るためIssue #21で追加(agent-trend-data
data-requests/pending由来の要望を具体化、2026-09-13)。

### 既知の制限

`has_security_policy` は対象リポジトリ自体のSECURITY.mdのみを見る設計の
ため、GitHub組織の`.github`特別リポジトリに置いて継承表示している
ケース(apache/airflow、langchain-ai/langchain等)を拾えない。MVPでは
CLAUDE.mdのシンプルさ優先方針に基づく意図的な割り切りとして許容する
(Issue #14でこの制限は対応せずクローズ)。

`has_tests`はモノレポ構成での検知漏れ・命名バリエーション(`tests`/`test`)
の問題が過去にあったが、Git Trees API(`recursive=1`)による全深度探索に
2026-09-07実装のIssue #14で対応済み(20リポジトリ中19件がtrueに改善、
falseはyoheinakajima/babyagiのみで実態と一致)。

`has_agent_instructions`も同様にルート直下しか見ておらず、モノレポで
サブディレクトリにのみ指示文書があるケースを検知できていなかった
(Issue #29、2026-09-14。`has_tests`の#14対応と同型のバグ)。全深度探索に
修正し、実データで`continuedev/continue`が`false`→`true`に改善したことを
確認した(実体は`extensions/cli/AGENTS.md`)。20リポジトリ中10件でルート
外にも指示文書が存在する(詳細はIssue #29参照)。

これに伴い、`agent_doc_char_count`等の内容分析系フィールドが分析する
「代表文書」の選定ルールも拡張した: ルート直下にCLAUDE.md/AGENTS.mdが
あればそれを使う(従来通り)。無ければ、見つかった文書のうち最も浅い
(同深度ならパス文字列の辞書順で先頭の)ディレクトリを代表として使う。
複数文書を合算しない方針とした理由は、(a) AutoGPTのように無関係な
複数文書(`autogpt_platform/`限定の規約と、他の21箇所の文書)を混ぜると
意味不明な合算値になる、(b) #25で判明したLLM分類(#15)の非決定性リスクを、
入力を巨大化させることでさらに悪化させたくない、の2点。

新設した`agent_doc_count`は、指示文書が見つかった**ディレクトリ数**
(重複排除、CLAUDE.md/AGENTS.mdのみ対象で`.cursorrules`は含めない)。
ファイル数ではなくディレクトリ数にしたのは、`colinhacks/zod`のように
CLAUDE.md・AGENTS.md・`.cursorrules`をルートに揃えているだけで
モノレポではないリポジトリを、ファイル数で数えると誤って複数扱いして
しまうため(実データで判明)。`agent_doc_count > 1`は「指示文書が複数箇所
に分散している」ことの決定的なシグナルであり、モノレポ構成である
可能性の代理指標として使える(ユーザー要望、Issue #29)。ただし
「1」であっても大規模なモノレポでないとは限らない(指示文書自体を
置いていないだけの可能性がある)点に注意。より正確なモノレポ判定
(package.json workspaces等のワークスペース設定検知)は将来の拡張候補
として見送った(Issue #29)。

`has_hooks_config`/`mcp_servers_count`は、ファイル存在だけでなく
`.claude/settings.json`/`.mcp.json`の中身(JSONキー)まで見て判定する。
「ファイル存在確認」中心のMVPスコープ方針からはわずかに踏み出すが、
CLAUDE.md/AGENTS.mdの内容分析(構造ベース)で既に認めている「決定的な
構造分析」の延長として扱う(Issue #21)。`.claude/skills/`/
`.claude/commands/`以外の慣習(サブエージェント`.claude/agents/`、
Cursorの`.cursor/rules/`等)は今回のスコープに含めていない(将来の拡張
候補)。

`has_skills_dir`/`skills_count`は`.claude/skills/`と`.agents/skills/`の
両方を見る(Issue #28、2026-09-14)。`.agents/skills/`はAgentSkills.io等が
推進するツール非依存の標準で、Codex/Gemini CLI/Cursor/VS Code Copilot/
Zed等が対応している(Web検索で確認)。実データでは以下のパターンが
確認できた:
- `.agents/skills`が実体、`.claude/skills`がそこへのシンボリックリンク
  (ディレクトリ単位): getsentry/sentry, supabase/supabase, vercel/next.js
- `.agents/skills`が実体、`.claude/skills`が個別スキルごとのシンボリック
  リンク(`.agents/skills`側の一部しか反映されず不完全な場合あり):
  cline/cline, apache/airflow
- `.claude/skills`が実体、`.agents/skills`がそこへのシンボリックリンク
  (逆方向): Significant-Gravitas/AutoGPT
- `.claude/skills`が存在せず`.agents/skills`のみ: OpenHands/OpenHands,
  sveltejs/svelte, astral-sh/ruff, remix-run/remix

どちらか一方だけでは検知漏れ・過小カウントが起きるため、両パスを
(自身がシンボリックリンクの場合は解決した上で)調べ、直下の子要素名の
和集合を数える(`SKILL.md`ファイル名一致では検知漏れが生じるため、
ファイル種別を問わない)。`.claude/commands/`側は`.agents/commands`と
いう対応する標準が存在しないことをWeb調査で確認済みのため対象外(将来
的に標準が現れた場合は再検討)。

### 廃止した項目とその理由

`has_observability_dep`(依存にLangSmith/Langfuse等の可観測性パッケージが
あるか)は2026-09-07、Issue #16でMVP後の項目から廃止した。

測ろうとしていたこと自体(LLM/エージェントの実行時挙動を追跡できて
いるか、というAIエージェント特有の運用実践)は今も妥当なテーマだが、
「自リポジトリのマニフェストへの依存宣言」という測り方には構造的な
限界があった。

- adopterセグメント(AI開発エージェントを使って開発しているだけで、
  自らLLMアプリを作っているわけではないプロジェクト)には概念的に
  適用対象外(10件中0件がtrue)。
- 本来の対象であるtoolセグメント(LLM/エージェントフレームワーク開発元)
  でも、フレームワークはLangSmith等との連携機能を"提供"するだけで、
  自身がそれに"依存"するとは限らないため、実質機能しなかった
  (10件中1件のみtrue)。

「実行時の観測性」という測りたい実態と、「依存マニフェストの文字列
一致」という測り方が原理的に噛み合っていなかったと判断し、いったん
廃止した。測り方の再設計はIssue #18で検討する。

## CLAUDE.md/AGENTS.md内容分析

`has_agent_instructions`とは別に、CLAUDE.md/AGENTS.mdの中身についても
分析する。分析対象は「代表文書」1箇所分: リポジトリルートに
CLAUDE.md/AGENTS.mdがあればそれを使い(両方存在する場合は内容を連結)、
無ければ見つかった文書のうち最も浅いディレクトリのものを代表とする
(Issue #29、モノレポでのルート外指示文書への対応)。どちらも見つからない
場合は`agent_doc_count`=0、`agent_doc_char_count`=0、
`agent_doc_heading_count`=0、その他の真偽値項目はすべてfalseとする。

### ルールベース分析(構造ベース)

キーワード一致・文字数・見出し数によるルールベース分析(LLMは使わない)。

| 項目キー | 何が分かるか | 判定方法 |
|---|---|---|
| agent_doc_count | 指示文書が複数箇所に分散しているか(モノレポ傾向の代理指標) | CLAUDE.md/AGENTS.mdが見つかったディレクトリ数(重複排除、数値) |
| agent_doc_char_count | 内容の充実度(代表文書1件分) | 文字数(数値) |
| agent_doc_heading_count | 構成の複雑さ | Markdown見出し(`#`で始まる行)の数(数値) |
| agent_doc_has_code_block | 具体的なコマンド例があるか | \`\`\`コードブロックの有無 |
| agent_doc_mentions_test | テスト実行方法への言及 | キーワード一致(大小文字無視): test, pytest, jest, vitest |
| agent_doc_mentions_lint | Lint/フォーマットへの言及 | キーワード一致: lint, ruff, eslint, prettier |
| agent_doc_mentions_security | セキュリティ上の注意点への言及 | キーワード一致: security, secret, credential, vulnerability |
| agent_doc_mentions_commit_convention | コミット規約への言及 | キーワード一致: commit message, conventional commit |
| agent_doc_mentions_tool_usage | Skill/MCP/サブエージェント等の拡張機能の使い方への言及 | キーワード一致: mcp, skill, subagent, slash command, hook, tool use, function calling |

### LLMベース分析(Issue #15)

`reports/agent_doc_analysis_validation.md`の発見3で指摘された、キーワード
一致では表現のバリエーションを拾いきれない4テーマをLLMで分類する。
Anthropic APIの従量課金ではなく、Claude Code CLIのヘッドレス実行
(`claude -p`、サブスクリプション認証)で完結させる
(`src/agent_trend_radar/llm_content_analysis.py`)。

| 項目キー | 何が分かるか | 判定方法 |
|---|---|---|
| agent_doc_mentions_repo_structure | リポジトリ構成・モノレポの境界説明への言及 | LLM分類 |
| agent_doc_mentions_boundaries | エージェントがしてはいけないことの境界線への言及 | LLM分類 |
| agent_doc_mentions_pr_review | PRレビュー基準・人間チェックポイントへの言及 | LLM分類 |
| agent_doc_mentions_release_process | リリース/デプロイ手順への言及 | LLM分類 |

※ このリストは運用しながら見直してよい(CLAUDE.mdの見直し方針を参照)。

### LLM分類の入力キャッシュキーと実行環境の隔離(Issue #30)

LLM分類(`claude -p`)は同一入力でも実行のたびに結果が変わりうる(非決定的、
#25の2bで実データにより確認)。この非決定性が「文書が変わった」という
偽の時系列変化として誤読されないよう、以下の2点を実装した。

| 項目キー | 何が分かるか | 判定方法 |
|---|---|---|
| agent_doc_llm_cache_key | LLM分類への入力(代表文書)が前回から変わったか | 代表文書のパス+blob SHAの組を連結した文字列。他の項目と異なり真偽値/数値ではなく文字列 |

`agent_doc_llm_cache_key`はLLM分類の結果を左右する項目ではなく、時系列
比較時に「キーが同じなのに`agent_doc_mentions_*`(LLM分類4項目)の値が
変わっている」ケースを機械的に検出するためのトレーサビリティ用フィールド
である。blob SHAはGit Trees APIのキャッシュ済みレスポンスに元々含まれて
おり、算出に新規API呼び出しは発生しない。

あわせて、`claude -p`呼び出し(`llm_content_analysis._run_claude_cli`)は
空の一時ディレクトリを`cwd`にし、`--tools ""`で全ツールを無効化する。
第三者リポジトリのCLAUDE.md/AGENTS.md(信頼できない入力)を渡す際に、
radar自身のCLAUDE.md/SPEC.mdが分類コンテキストに混入することと、
プロンプト注入によるツール実行の両方を防ぐ。

使用したclaude CLIバージョン・分類プロンプトのハッシュは、1回の収集実行
内で全リポジトリ共通の値になるため`repo_checks`(リポジトリ単位)には
含めず、hubスナップショット(`metrics.json`)のトップレベル
(`llm_classification`)に1回だけ記録する。

## データスキーマ
| 項目 | 内容 |
|---|---|
| repo | owner/repo |
| segment | tool / adopter |
| monetization_model | commercial_saas / big_corp_internal / nonprofit_foundation / individual_community |
| checked_at | チェック実行日 |
| (ファイル存在系チェック項目キー) | 真偽値(存在する=true) |
| (CLAUDE.md/AGENTS.md内容分析キー) | 数値(char_count/heading_count) または真偽値 |
| (エージェント運用ツール項目キー) | 真偽値(has_*)または数値(*_count) |
| agent_doc_llm_cache_key | 文字列(パス+blob SHAの組、Issue #30) |

## 保存形式
- SQLite、テーブル名: `repo_checks`
- 1レコード = 1リポジトリ×1回のチェック