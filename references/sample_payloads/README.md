# Sample payloads

Fully **synthetic** Campus Solutions / CDM student payloads for learning the
input shape and smoke-testing the skill. No real student data — every `personid`
is a `TST_` value, and all names, emails, and IDs are invented.

- `TST_0000008.json` — dual-degree case (career# 0 QST + career# 1 CAS), one
  active major per career, plus a superseded PRGC row in career# 0 that must be
  dropped. Mirrors the "dual degree, career# 0/1" row in
  `../pe_selection_rules.md`. Expected result: **2 PEs** — Business Admin BSBA
  (QST) + Economics BA (CAS); the superseded Undeclared row is dropped.

Use it like a real input: "analyze TST_0000008" or paste the JSON and ask for
EDA / EDF / both. To add your own examples, keep them synthetic and `TST_`-keyed
— never commit real BUIDs alongside this skill (FERPA restricted-use).
