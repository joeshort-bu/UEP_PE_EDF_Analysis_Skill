# Setup — point this skill at your own orgs

The analysis logic is environment-independent, but org aliases and two field API
names are specific to each Salesforce environment. Do these once.

## 1. Authorize your orgs

This skill only ever **reads** (queries) data. Authorize your sandbox / dev orgs
with the Salesforce CLI (sf v2) and note the aliases you give them:

```
sf org login web --alias <your-eda-org>
sf org login web --alias <your-edf-org>
```

Never point it at production for exploratory analysis — use a sandbox.

## 2. Tell the scripts which org and BUID field to use

The helper scripts read org aliases and the BUID field from environment
variables (no aliases are hardcoded). Set what fits your environment:

| Variable | Purpose | Default |
| --- | --- | --- |
| `SF_EDA_ORG` | alias of your EDA (source) org | none — required |
| `SF_EDF_ORG` | alias of your EDF (target) org | none — required |
| `SF_BUID_FIELD` | Contact BUID field (EDA side) | `zBU_BUID__c` |
| `SF_EDF_BUID_FIELD` | Account BUID field (EDF side) | `zBU_BUID__pc` |

You can also just pass the org alias as the 2nd argument to any script.

```
python3 scripts/fetch_student_eda.py U12345678 <your-eda-org>
python3 scripts/fetch_student_edf.py U12345678 <your-edf-org>
```

## 3. Confirm your BUID field name

BUID is not always `zBU_BUID__c`. On a Person-Account org it is often
`zBU_BUID__pc`. Confirm the API name before relying on the SOQL in
`references/migration_soql.md`:

```
sf sobject describe --sobject Contact --target-org <your-eda-org> | grep -i buid
sf sobject describe --sobject Account --target-org <your-edf-org> | grep -i buid
```

Set `SF_BUID_FIELD` / `SF_EDF_BUID_FIELD` accordingly.

## 4. Adapt the mappings if your org differs

`references/crosswalk.csv`, `value_maps.md`, and `edf_model.md` encode Boston
University's UEP EDA↔EDF mapping. If your field API names or code values differ,
edit those files — the skill treats them as the source of truth.

## FERPA / data handling

Real (non-`TST_`) BUIDs and student records are FERPA restricted-use. Keep any
production data you pull within your institution's policy, work in sandboxes, and
**never commit real student data into this skill folder** — the bundled examples
are synthetic on purpose. Keep them that way.
