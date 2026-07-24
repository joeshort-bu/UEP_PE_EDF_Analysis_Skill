#!/usr/bin/env python3
"""Quick Contact lookup by BUID (verify a student exists / get the record Id).

Portability: same as fetch_student_eda.py — pass the org alias as arg 2 or set
SF_EDA_ORG; override the BUID field via SF_BUID_FIELD (default zBU_BUID__c).

Usage: python3 scripts/query_student_by_buid.py <BUID> [org-alias]
"""
import os, sys, subprocess, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_ORG = os.environ.get('SF_EDA_ORG')
BUID_FIELD = os.environ.get('SF_BUID_FIELD', 'zBU_BUID__c')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    buid = sys.argv[1]
    org = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_ORG
    if not org:
        print('No org alias. Pass one as the 2nd arg or set SF_EDA_ORG.')
        sys.exit(2)

    print(f'Looking up BUID {buid} in org {org} (BUID field {BUID_FIELD})...')
    soql = f"SELECT Id, Name, FirstName, LastName, Email, AccountId FROM Contact WHERE {BUID_FIELD} = '{buid}' LIMIT 20"
    f = ROOT / 'tmp_query.soql'
    f.write_text(soql)
    try:
        proc = subprocess.run(['sf', 'data', 'query', '--file', str(f), '--target-org', org, '--result-format', 'json'], cwd=ROOT, text=True, capture_output=True)
    finally:
        f.unlink(missing_ok=True)

    if proc.returncode != 0:
        print(proc.stderr)
        sys.exit(proc.returncode)

    print(json.dumps(json.loads(proc.stdout), indent=2)[:12000])


if __name__ == '__main__':
    main()
