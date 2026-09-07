# 分析結果を要約・記事化する際の統計的な注意点

**作成日**: 2026-09-07
**目的**: `data/repo_checks.db`の集計結果をもとに要約・記事を書く際
(Issue #12着手時を想定)、解釈を誤らないためのチェックリスト。
`reports/mvp_data_insights_evaluation.md`のMVP品質評価で、実際に
誤りかけた事例をもとにまとめている(詳細な検証過程はそちらを参照)。
Issue #17の成果物。

## 1. 平均値だけで語らない(外れ値に弱い)

平均値は少数の外れ値に強く引っ張られる。例えば`agent_doc_char_count`の
commercial_saas平均は23,275字だったが、これはOpenHands/OpenHands
(120,034字、2位browser-useの倍以上)という突出した1件が押し上げていた
だけで、中央値は12,202字だった。

**チェックリスト**
- [ ] 平均値を報告する際は、必ず中央値(median)も併記したか
- [ ] `uv run scripts/report.py --format stats`で該当項目の
      min/median/mean/maxを確認したか
- [ ] 平均と中央値が大きく乖離している場合、外れ値1件が結論を
      左右していないか確認したか

## 2. segment間比較は選定バイアスの影響を疑う

対象リポジトリの選定基準(SPEC.md)自体が、比較対象の分布を最初から
決めてしまっている項目がある。例えば`has_agent_instructions`は、
adopterセグメントを選ぶ基準そのものが「CLAUDE.md/AGENTS.md等の
採用が公知の事例」であるため、adopterは最初からこの項目で100%に
なるよう選ばれている。この状態でtool vs adopterを比較しても、
「adopterの方が進んでいる」という結論は選定基準の反映に過ぎず、
実態の発見ではない。

**チェックリスト**
- [ ] 比較に使う軸(segment、monetization_model等)が、SPEC.mdの
      選定基準に組み込まれていない軸かを確認したか
- [ ] 選定基準に組み込まれている軸で比較する場合、その旨を
      明記したか
- [ ] 選定バイアスの影響を避けたい場合、汚染されていない軸
      (例: tool segment内部だけでmonetization_model別に見る)に
      絞れないか検討したか

## 3. 天井/床効果のある項目は比較材料にならない

ほぼ全件が同じ値になる項目(分散がほぼゼロ)は、差を語る根拠として
使えない。例えば`has_ci`はadopter 100%・tool 90%とほぼ天井に
張り付いており、「CI導入はもはや前提条件」以上のことは言えない。
`agent_doc_has_code_block`もtool 67%・adopter 70%と僅差で、
セグメント間の弁別力が低い。

**チェックリスト**
- [ ] 比較に使おうとしている項目が、`uv run scripts/report.py`の
      出力で0%/100%付近に張り付いていないか確認したか
- [ ] 分散が乏しい項目を「差がある」かのように誇張して書いていないか

## 関連

- 検証の詳細: `reports/mvp_data_insights_evaluation.md`
- 集計軸の見直し議論: Issue #16(has_observability_depの廃止)、
  Issue #18(可観測性指標の測り方の再設計)
- 本ドキュメントの反映先: Issue #12(LLMによる要約・記事生成、未着手)
