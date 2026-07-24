#!/usr/bin/env python3
"""Fetch a student's EDA records (Contact + Program Enrollments) by BUID.

Portability:
- Org alias: pass as the 2nd arg, or set the SF_EDA_ORG environment variable.
- BUID field: defaults to the Contact field `zBU_BUID__c`. If your org stores
  BUID elsewhere (e.g. a Person-Account field `zBU_BUID__pc`), set the
  BUID_FIELD constant below or the SF_BUID_FIELD environment variable.

Usage: python3 scripts/fetch_student_eda.py <BUID> [org-alias]
"""
import os, sys, subprocess, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_ORG = os.environ.get('SF_EDA_ORG')          # no hardcoded org — set per environment
BUID_FIELD = os.environ.get('SF_BUID_FIELD', 'zBU_BUID__c')


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
        print('No org alias. Pass one as the 2nd arg or set SF_EDA_ORG.')
        sys.exit(2)

    print(f'Fetching EDA data for BUID {buid} from org {org} (BUID field {BUID_FIELD})...')

    contacts = query(org, f"SELECT Id, Name, FirstName, LastName, Email, AccountId, {BUID_FIELD} FROM Contact WHERE {BUID_FIELD} = '{buid}' LIMIT 20")
    if not contacts:
        print('No Contact found for that BUID.')
        sys.exit(0)

    contact = contacts[0]
    pes = query(org, f"SELECT Id, Name, hed__Contact__c FROM hed__Program_Enrollment__c WHERE hed__Contact__c = '{contact['Id']}'")

    print(json.dumps({'contact': contact, 'program_enrollments': pes}, indent=2))


if __name__ == '__main__':
    main()
