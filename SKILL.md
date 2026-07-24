---
name: uep-pe-edf-analyzer
description: >-
  Determine the correct Program Enrollment (PE) records and audience rollups a
  student's Campus Solutions / CDM JSON should produce for Boston University's
  MyBU Student Portal, and render them either as Salesforce EDA objects
  (hed__Program_Enrollment__c) or as EDF learner/learning objects
  (LearnerProgram / LearningProgramPlan / AcademicTermEnrollment + Person-Account
  rollups). Use whenever someone pastes or uploads a student record JSON (fields
  like studentInfo.studentSemester[].studentSemesterInfo.degreeProgram[],
  admissionHistory, personid) and asks "what PEs should be created," "what's the
  correct Program Enrollment," "show the EDA result," "show the EDF learner/learning
  objects," or asks to validate PE/audience output. Also trigger on mentions of
  BUEPx PE creation, program-enrollment dedup/supersession, or EDA-to-EDF PE mapping.
---

# UEP Program Enrollment & EDA/EDF Analyzer

Given a Campus Solutions / CDM student JSON, determine the correct set of Program
Enrollments and the Contact/Account audience rollups, then render the answer in
one of two modes:

- EDA mode: Salesforce EDA hed__Program_Enrollment__c records + Contact rollups — what BUEPx creates today.
- EDF mode: the EDF learner/learning objects those same PEs become — LearnerProgram + LearningProgramPlan + AcademicTermEnrollment per PE, plus the EDF Person-Account rollups and ContactProfile / ContactPoint* detail objects.

> **Before you start (portability):** this skill was authored against Boston
> University's UEP orgs. Org aliases and a couple of field API names are
> environment-specific — read `SETUP.md` once to point it at your own orgs and
> confirm your BUID field before running the scripts.

## Start here — guided intake

When invoked without an explicit request, ask this first (single question):

> What would you like to do — (1) Validate a BUEPx JSON, or (2) Compare EDA → EDF (via SOQL)?

- (1) Validate a BUEPx JSON → the CS-source flow: take a CS/CDM student JSON and produce the correct Program Enrollments. Then ask the output mode (EDA / EDF / both) per "Mode" below, and render.
- (2) Compare EDA → EDF → the migration flow. Ask next: single record or bulk?
  - Single record → ask for the BUID first, then hand back the Contact + Program Enrollment SOQL from references/migration_soql.md with that BUID already substituted into the WHERE clause (never a placeholder), as clean SQL code blocks with no -- comments or trailing semicolons. Ingest the export; show the EDA record → its EDF lift-and-shift equivalent → Flags. If they also provide the actual migrated EDF, diff the two.
  - Bulk → give them the bulk explicit-field SOQL; ingest; return the summary + exception list (dupes, terminal-to-retire, unmapped fields, rollup issues).

Skip a question whenever the user already answered it in their message, or the input type makes the branch obvious.

## Input

The student JSON or EDA/EDF export can arrive two ways:
- Pasted directly in chat, or
- Dropped into the connected project folder as a file (e.g., {UID}.json). When the user names a UID (e.g., "analyze U12345678"), look for the matching JSON file in the connected folder and read it. If a UID is named but no file is found, say so and ask them to drop or paste it.
- An existing-EDA export (Contact + hed__Program_Enrollment__c as CSV or JSON) — this is the migration input. Extraction queries are in references/migration_soql.md.

A structurally faithful, fully synthetic example input lives in
references/sample_payloads/ — use it to see the expected CS/CDM shape. It
contains no real student data.

Auto-detect the input: a CS/CDM student JSON (studentInfo.studentSemester[]…degreeProgram[], personid) → the CS-source flow (ask EDA/EDF/both). An EDA record export (hed__Program_Enrollment__c / Contact rows) → migration mode. An EDF export (Account person account + LearnerProgram) → treat as the target side for validation/diff.

## Mode — always confirm first

When a JSON (or UID) is provided without a stated mode, ask before producing output:

> Do you want this analyzed as EDA Program Enrollments, EDF Learner/Learning objects, or both?

Wait for the answer, then produce only what was asked. Skip the question only if the user already indicated the mode in the same request. Interpretation:
- "PE(s)", "program enrollment(s)", "EDA", "what should be created" → EDA mode
- "EDF", "Learner/Learning", "the cluster", "target org", "post-migration" → EDF mode
- "both" → EDA first, then the EDF cluster

Authoritative source: FRD UC-SR850. Mapping source: UEP Data EDA-EDF workbook, encoded in references/crosswalk.csv and references/value_maps.md.

## Step 1 — Determine the correct PE set (identical for both modes)

Work from studentInfo.studentSemester[].studentSemesterInfo. Full rules and the validated worked cases are in references/pe_selection_rules.md. Summary:

1. Pick the current term. The studentSemester whose academicTerm.termBeginDate ≤ today ≤ termEndDate; if today is between terms, use the most recently begun term. Multiple careers can each have a current-term record — process all. The degreeProgram stack is effective-dated and repeats across terms, so the current-term copy carries the latest rows.

2. Resolve term-activated programs. Partition degreeProgram[] by (academicCareer.code, programCareerNumber). Within each partition, select the current row: latest effectiveDate ≤ today, then highest effectiveSequence, among rows with registrationStatus.code ∈ {AC, LV/LA}. Confirm the pick with isCurrentAcademicProgram == "Y" (log a data-quality note and fall back to EFFDT/EFFSEQ if they disagree). Ignore future-dated rows and all rows below the selected one.

2b. Completed-program (recent graduates). If a partition's current row (highest EFFDT/EFFSEQ) is registrationStatus.code == CM (Completed Program) — i.e., there's no current AC/LV row — still select it when its grad term (expectedGradTerm / plan completionTerm) is within the last 3 terms of the current term. Emit the PE with status Completed Program and set the degree conferral date (graduationDate). Beyond the 3-term window, do not pick up. Confirm with the business whether primaryAffiliation = Inactive-Student grads should still be sent, and which term drives class standing / enrollment status for a completed program.

2c. Evaluate each partition independently — mixed / do-not-pickup statuses. Decide PE creation per partition by that partition's own current-row status, not by the student overall. Only partitions whose current row is pickup-eligible — AC, LA/LV, CM within the 3-term window, or a future matriculated program — produce PEs. A partition whose current row is a do-not-pickup status produces no PE, and any existing PE for it must be retired/deactivated: CN Cancelled, DC Discontinued, DM Dismissed, SP Suspended, DE Deceased. A student can legitimately be AC/LA/CM in one program and terminated in another — emit PEs only for the eligible partitions. An eligible partition never authorizes creating a PE for a do-not-pickup partition. Do-not-pickup partitions also contribute nothing to the audience rollups.

3. Add matriculated future-term programs. From admissionHistory[].applicationPrograms[], include any program with action == MATR / status == AC for a future admit term that isn't already a term-activated partition. Past-term or superseded admissions add nothing.

4. Emit one PE per academicPlan[] entry on each selected row — every major AND minor. Two majors → 2 PEs; major+minor → 2; distinct programs (different program-career-number, or a matriculated program) → the full set for each.

5. Never emit a PE from a superseded, historical, or future-dated row. The decisive key is programCareerNumber: multiple programs under the same number chained by PRGC = a supersession chain (keep only the current row); different numbers = concurrent dual degree (keep each).

### Rollups (drive the audience fields in both modes)

Derive only from the selected active rows + current-term record:
- Career audience = distinct academicCareer labels across PEs. School/College audience = distinct academicGroup codes. Academic-plan / academic-program / admit-type / enrollment-status / program-action / program-status audiences = distinct values across PEs.
- Single-value Contact fields: Admit Term, Expected Graduation Term (latest across active careers), Primary Academic Program (academicProgramPrimary), Class Standing (current term).

## Step 2 — Render output

### EDA mode

One hed__Program_Enrollment__c per PE. Map with references/crosswalk.csv (rows where tab = EDA Program Enrollment). Core fields: hed__Contact__c, hed_Account__c (Academic Plan), zBU_SchoolCollege__c, zBU_Academic_Program_Code__c, zBU_Student_Type__c, zBU_ProgramStatus__c, zBU_ProgramAction__c, zBU_Program_Type__c (Major/Minor), zBU_Effective_Date__c, zBU_Admit_Term__c, zBU_Admit_Type__c, zBU_Mutual_Accept_Date__c, hed__Enrollment_Status__c, hed__Class_Standing__c, zBU_Additional_Program_of_Study__c, Name / zBU_PE_External_ID__c. Then the Contact rollups.

Dedup/external-ID convention: zBU_PE_External_ID__c = {emplid}_{plancode} (plan-code level).

### EDF mode

Each selected PE fans out into a cluster (crosswalk rows carry the EDF target in edf_object/edf_field_name; see references/edf_model.md):

- LearnerProgram (1 per PE) — admit type, student type, academic program code, Status (registrationStatus), program action, effective date, admit term, primary academic program, expected graduation term, withdrawal date, degree conferral date, LearnerContactId → Person Account, LearningProgramPlanId → LearningProgramPlan, LearnerAccount → School/College, zBU_Enrollment_Id__c.
- LearningProgramPlan (the plan/program) — zBU_External_ID__c (academicPlan/plan/code), Name (transcriptDescription), zBU_type__c (Major/Minor), zBU_Additional_Program_of_Study__c.
- AcademicTermEnrollment (1 per PE, current term) — EnrollmentDate, EnrollmentStatus, StudyYearClassification, zBU_Current_Term_Credits__c, CumulativeGradePointAverage.
- Account (Person Account) = the learner — name/BUID/birthdate/pronouns + the audience rollups as __pc fields.
- ContactProfile — citizenship, US-permanent-resident, student group, first-gen, housing interest, citizenship status, financial-aid eligible.
- ContactPointEmail / ContactPointPhone / Contactpointaddress — email / phone / mailing address detail.

EDF structural notes: EDF uses the Person-Account model — the EDA Contact becomes an EDF Account (person account), and Contact rollups become __pc fields on it. Some rollups live on LearnerProgram not Account (Primary Academic Program, Expected Graduation Term, Withdrawal Date, Degree Conferral Date). Generate exactly one AcademicTermEnrollment per selected PE (current term).

## EDA → EDF migration mode (lift & shift)

Use when the input is existing EDA records (a Contact + hed__Program_Enrollment__c export) rather than a CS CDM JSON — i.e., previewing/validating what current data becomes in EDF. Extraction queries: references/migration_soql.md.

- Transform (lift & shift): map each existing EDA record to its EDF objects via crosswalk.csv — Contact → Person Account (+ ContactProfile / ContactPoint*), each hed__Program_Enrollment__c → LearnerProgram + LearningProgramPlan + AcademicTermEnrollment. Preserve values as-is; do not re-derive from CS.
- Known schema gaps: references/migration_soql.md documents fields present in the original crosswalk workbook that don't exist in the live org; treat their absence as expected, not a new finding.
- Flag, don't silently fix: duplicate PEs for the same plan code, terminal-status PEs that shouldn't carry forward, superseded rows, stuck/single-value audience rollups on the Contact, unmapped EDA fields with no EDF target.
- Scale:
  - Single record → the per-object landing view (see below). This is the primary single-UID deliverable.
  - Bulk file → a summary: counts + an exception list (dupes, terminal-to-retire, unmapped-field hits, rollup issues) — not per-record tables.
- Validation / diff: given a source (CS-expected or the EDA export) and an EDF target export, report matches vs mismatches per object/field.

### Single-UID landing view — where the data landed (required format)

The point of the single-record view is to show, at a glance, **where each EDA value landed in EDF, and whether migration got it right.** This is a true diff and needs both the EDA export and the actual migrated EDF export for the UID. If only one side is present, say so at the top and fall back: EDA-only → render expected EDF values with Status = *not yet migrated*; EDF-only → render actual values with Status = *source not available to verify*. Do not fabricate the missing side.

Organize **by EDF object, then one row per EDF field**, with the EDA source in an adjacent column. Lead with the shared Person Account, then each enrollment's cluster (LearnerProgram → LearningProgramPlan → AcademicTermEnrollment), then ContactProfile / ContactPoint*. Every object is its own labeled block with this five-column table:

| EDF Field | EDF Value | ← EDA Source Field | EDA Value | Status |
| --- | --- | --- | --- | --- |

- **EDF Field** — the target API name (from crosswalk `edf_field_name`).
- **EDF Value** — the actual migrated value from the EDF export. Blank → *(blank)*.
- **← EDA Source Field** — the source, `object.field` form (from crosswalk `eda_object` / `eda_field_name`); for CS-derived rollups use the CS path. No source → *(no EDA source)*.
- **EDA Value** — the value in the EDA export. Blank → *(blank)*.
- **Status** — one of:
  - ✅ — EDF value matches the expected value derived from the EDA source via the crosswalk (apply the row's `transform`/value map before comparing; a code→label expansion that lands the right label is a ✅, not a mismatch).
  - 🚩 **mismatch** — both sides have values but they disagree after transform.
  - 🚩 **empty target** — EDA has a value but the EDF field is blank (data dropped in migration).
  - 🚩 **unmapped** — EDF field populated with no EDA source, or an EDA field with no EDF target that carried a value.
  - ⬜ **both blank** — nothing on either side; low-signal, keep but don't flag.

Make flags impossible to miss: after each object's table, if it has any 🚩 rows, add a bold line — **🚩 N flag(s) in LearnerProgram: …** naming the fields. Open the whole view with a one-line scoreboard: **✅ M matched · 🚩 K flagged · ⬜ B blank** across all objects, and if K > 0 list the flagged `object.field`s there too so the reader sees every problem before scrolling. Never let a 🚩 hide inside a table without also being surfaced in a callout.

## Step 3 — Present

Open with one line: the count and identity of the correct PEs (plan, type, program, academic group, career-number) and the current term. Then a short dropped line (what was excluded and why — supersession / future-dated / past-admission). Then the objects. Close with a Flags callout for any ambiguity (class standing in a summer term, isCurrentAcademicProgram disagreeing with EFFDT/EFFSEQ, CM-but-not-yet-conferred graduating seniors). Use references/value_maps.md to expand codes to labels.

### Formatting rules (readability — required)

Do not cram many fields into a single table cell. Instead:
- Give each object its own labeled block, grouped under a per-enrollment heading.
- Render each object's fields as a two-column Field | Value table with one field per row, or as short bold Field — value lines.
- Keep values short; put the external ID in bold; show blanks as *(blank — reason)*.
- Lead with the shared Person Account block, then each enrollment's cluster (LearnerProgram → LearningProgramPlan → AcademicTermEnrollment).
- ContactProfile and ContactPoint* detail can be condensed to one short italic line unless the user asks for every field.
- If the user prefers, offer a raw JSON rendering of the objects instead of tables.

Apply the same one-field-per-row discipline in EDA mode (one hed__Program_Enrollment__c block per PE + a rollups block).

In EDA → EDF migration mode, single record, use the five-column landing view instead (EDF Field | EDF Value | ← EDA Source Field | EDA Value | Status) — see "Single-UID landing view" above. It supersedes the two-column Field | Value table for that mode, because the whole purpose is to show where each value landed and whether it's a ✅ or a 🚩. The Flags callout at the end still applies and should tie back to the 🚩 rows.

## For colleagues — how to use (plain language)

A user does not need to know the FRD rules — they give data and say what they want; the skill does the rest and shows its reasoning.

1. Get the data. Either paste/drop a CS student JSON, or run a query from references/migration_soql.md and drop the export in the connected folder.
2. Say what you want — examples:
   - "What PEs should BUEPx create for U#######?" → EDA result.
   - "Show U####### in EDF." → EDF cluster.
   - "Does this migrate cleanly?" + an EDA export → migration mode with exception flags.
   - "Validate what BUEPx wrote" + the CS JSON and the Salesforce record → diff.
3. Answer the one mode question if asked (EDA / EDF / both / migration).
4. Read the Flags at the end — that's where judgment calls and data issues surface.

Guarantees to state to a first-time user: the skill applies the FRD selection rules, always shows what it dropped and why, expands codes via value_maps.md, and never invents field values. Reminder: real (non-TST_) BUIDs are FERPA restricted-use — keep production data handling within your institution's policy, and never commit real student data alongside this skill.
