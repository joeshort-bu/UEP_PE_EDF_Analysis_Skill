# Value / code maps (from the EDA-EDF workbook, Program Enrollment tab)

Use these to expand Campus Solutions codes to labels in output.

## Student Type / Career — academicCareer.code

| Code | Label |
| --- | --- |
| UGRD | Undergraduate |
| GRAD | Graduate |
| MEDS | Medical |
| LAW | Law |
| DENT | Dental |
| NONC | Non-Credit |
| NOND | Non-Degree |

## Program Status — registrationStatus.code (→ EDA zBU_ProgramStatus__c, EDF LearnerProgram.Status)

| Code | Label |
| --- | --- |
| AC | Active in Program |
| AD | Admitted |
| AP | Applicant |
| CN | Cancelled |
| CM | Completed Program |
| DC | Discontinued |
| DE | Deceased |
| LA | Leave of Absence *(also seen as LV in some CDM payloads)* |
| PM | Prematriculant |
| WT | Waitlisted |
| SP | Suspended |
| DM | Dismissed |

Selection filter: only rows with status in {AC, LA/LV} are eligible as the current row.

## Program Action — action.code (→ EDA zBU_ProgramAction__c, EDF LearnerProgram.zBU_Program_Action__c)

| Code | Label | Note for selection |
| --- | --- | --- |
| ACTV | Activate | |
| MATR | Matriculation | initial program row |
| DATA | Data Change | transition within a stack |
| PRGC | Program Change | supersession within same program-career-number |
| PLNC | Plan Change | supersession within same program-career-number |
| COMP | Completion of Program | |
| DEFR | Defer Enrollment | |
| LEAV | Leave of Absence | status → LA |
| RLOA | Return from Leave of Absence | |
| RADM | Readmit | |
| REVK | Revoke Degree | |
| TRAN | Transfer to Other Career | |
| WADM | Administrative Withdrawal | status → CN; not picked up |
| DISM | Dismissal | not picked up |
| DISC | Discontinuation | not picked up |
| SPND | Suspension | not picked up |
| ADRV | Admission Revocation | not picked up |

## Enrollment Status / Academic Load (→ EDA hed__Enrollment_Status__c, EDF AcademicTermEnrollment.EnrollmentStatus)

Source: studentSemesterInfo/certificationApproved/code.

| Code | Label |
| --- | --- |
| F | Full-Time |
| H | Half-Time |
| L | Less 1/2 |
| N | No Units |
| P | Part-Time |

## Program Type — academicPlan[].type.code (→ EDA zBU_Program_Type__c, EDF LearningProgramPlan.zBU_type__c)

| Code | Label |
| --- | --- |
| MAJ | Major |
| MIN | Minor |

## Admit Type — admissionHistory[].admitType.code (→ zBU_Admit_Type__c)

| Code | Label |
| --- | --- |
| FRS | Freshman |
| TRN | Transfer |
| FYR | First Year (Law) |
| GRD | Graduate Admissions |

Comes from admissionHistory keyed to the program; a program with no admission record (e.g., an internally-activated dual-degree plan) has a blank Admit Type — that is correct, not a miss.

## Mutual Accept Date (→ EDA zBU_Mutual_Accept_Date__c, EDF AcademicTermEnrollment.EnrollmentDate)

AdmissionHistory action row where PROG_ACTION = DEIN and PROG_REASON = RPPD → its actionDate. Blank when there is no admission record for the program.
