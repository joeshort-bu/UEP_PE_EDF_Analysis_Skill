# UEP PE / EDA / EDF Analyzer — shareable skill

A Claude Code skill that takes a Campus Solutions / CDM student JSON (or existing
Salesforce records) and works out the **correct Program Enrollments** and audience
rollups a student should produce, rendered as EDA (`hed__Program_Enrollment__c`)
objects, EDF Learner/Learning objects, or a migration diff between them. Built for
validating BUEPx PE creation and EDA→EDF migration runs in sandboxes.

## What's in here

```
uep-pe-edf-analyzer/
├── SKILL.md                       the skill instructions (loaded by Claude Code)
├── SETUP.md                       one-time setup for your orgs (read this first)
├── README.md                      this file
├── references/
│   ├── crosswalk.csv              EDA↔EDF field mapping (source of truth)
│   ├── value_maps.md              CS code → label maps
│   ├── edf_model.md               EDF object-model notes
│   ├── migration_soql.md          extraction queries (EDA + EDF)
│   ├── pe_selection_rules.md      validated case matrix (synthetic IDs)
│   └── sample_payloads/           fully synthetic TST_ example input
└── scripts/                       BUID lookup helpers (sf CLI)
```

No real student data ships with this package. The worked examples and the sample
payload use synthetic `TST_` identities.

## Install

Copy the whole `uep-pe-edf-analyzer/` folder into a Salesforce DX project under
`.claude/skills/`. It becomes available the next time Claude Code starts in that
project. To share, zip this folder and send it — the recipient drops it in the
same place.

## Use

1. Do the one-time **SETUP.md** steps (org aliases + BUID field).
2. Ask in plain language, e.g.:
   - "What PEs should BUEPx create for U#######?" → EDA result
   - "Show U####### in EDF." → EDF cluster
   - "Does this migrate cleanly?" + an EDA export → migration mode with flags
   - "Analyze TST_0000008" → runs against the bundled synthetic sample
3. Answer the one mode question if asked (EDA / EDF / both / migration), then read
   the **Flags** at the end — that's where judgment calls and data issues surface.

Full behavior is documented in `SKILL.md`.
