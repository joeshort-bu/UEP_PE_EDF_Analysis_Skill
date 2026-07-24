#!/usr/bin/env python3
"""Fetch a student's EDF records (Person Account + LearnerPrograms) by BUID.

Portability:
- Org alias: pass as the 2nd arg, or set the SF_EDF_ORG environment variable.
- BUID field: EDF Person-Account orgs typically store BUID as `zBU_BUID__pc`.
  Override via the BUID_FIELD constant below or SF_EDF_BUID_FIELD. If your org
  has no queryable BUID field on Account, set SF_EDF_BUID_FIELD='' to fall back
  to a Name LIKE match.

Usage: python3 scripts/fetch_student_edf.py <BUID> [org-alias]
"""
import os, sys, subprocess, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_ORG = os.environ.get('SF_EDF_ORG')          # no hardcoded org — set per environment
BUID_FIELD = os.environ.get('SF_EDF_BUID_FIELD', 'zBU_BUID__pc')


def run(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def query(org, soql):
    f = ROOT / 'tmp_query.soql'
    f.write_text(soql)
    try:
        proc = run(['sf', 'data', 'query', '--file', str(f), '--target-org', org, '--result-format', 'json'])
    finally:
        f.unlink(missing_ok=True)
    if proc.returncode != 0:
        print(proc.stderr)
        sys.exit(proc.returncode)
    return json.loads(proc.stdout).get('result', {}).get('records', [])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    buid = sys.argv[1]
    org = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_ORG
    if not org:
        print('No org alias. Pass one as the 2nd arg or set SF_EDF_ORG.')
        sys.exit(2)

    print(f'Fetching EDF data for BUID {buid} from org {org}...')

    if BUID_FIELD:
        where = f"{BUID_FIELD} = '{buid}'"
        select = f"Id, Name, PersonEmail, {BUID_FIELD}"
    else:
        where = f"Name LIKE '%{buid}%'"
        select = "Id, Name, PersonEmail"

    accounts = query(org, f"SELECT {select} FROM Account WHERE {where} LIMIT 20")
    if not accounts:
        print('No Account found for that BUID in the EDF org.')
        sys.exit(0)

    account = accounts[0]
    learners = query(org, f"SELECT Id, Name, LearnerContactId, LearningProgramPlanId, LearnerAccountId, zBU_Enrollment_Id__c FROM LearnerProgram WHERE LearnerContactId = '{account['Id']}'")

    print(json.dumps({'account': account, 'learner_programs': learners}, indent=2))


if __name__ == '__main__':
    main()
