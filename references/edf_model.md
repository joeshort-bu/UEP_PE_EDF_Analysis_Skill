# EDF object model (from the EDA-EDF workbook)

EDF uses the Person-Account model. The EDA Contact (the student/learner) becomes an EDF Account (person account); Contact rollups become __pc fields on that Account.

Each EDA hed__Program_Enrollment__c fans out into a LearnerProgram + LearningProgramPlan + AcademicTermEnrollment cluster. Full field list in crosswalk.csv (edf_object / edf_field_name).

## Per selected PE → object cluster

### LearnerProgram (1 per PE)

The core learner-side enrollment record.

| EDF field | From (CS source → EDA) |
| --- | --- |
| zBU_Admit_Type__c | admissionHistory admitType.description |
| zBU_Student_Type__c | degreeProgram academicCareer.code (mapped) |
| zBU_Academic_Program_Code__c | degreeProgram program.code |
| Status | degreeProgram registrationStatus.code |
| zBU_Program_Action__c | degreeProgram action.code |
| zBU_Effective_Date__c | degreeProgram effectiveDate |
| zBU_Admit_Term__c | degreeProgram admitTermDescription |
| zBU_Primary_Academic_Program__c | studentSemesterInfo academicProgramPrimary |
| zBU_Expected_Graduation_Term__c | degreeProgram expectedGradTerm.description |
| zBU_Withdrawal_Date__c | studentSemesterInfo withdrawalStatus.date |
| zBU_Degree_Conferral_Date__c | degreeProgram graduationDate |
| LearnerContactId | → Person Account (the learner) |
| LearningProgramPlanId | → LearningProgramPlan (the plan) |
| LearnerAccount | → School/College account (zBU_SchoolCollege__c) |
| zBU_Enrollment_Id__c | PE Name / external id (`{emplid}_{plancode}`) |

### LearningProgramPlan (the plan/program catalog record)

| EDF field | From |
| --- | --- |
| zBU_External_ID__c | academicPlan/plan/code |
| Name | academicPlan/transcriptDescription |
| zBU_type__c | academicPlan type.code (Major/Minor) |
| zBU_Additional_Program_of_Study__c | (additional program of study) |

### AcademicTermEnrollment (1 per PE, current term)

| EDF field | From |
| --- | --- |
| EnrollmentDate | mutual-accept / DEIN actionDate |
| EnrollmentStatus | certificationApproved.code (F/H/L/N/P) |
| StudyYearClassification | class standing (academicLevelDescription) |
| zBU_Current_Term_Credits__c | studentSemesterInfo unitsTermTotal |
| CumulativeGradePointAverage | studentSemesterInfo unitsCumulative *(per sheet mapping)* |

## Learner (shared, once per student)

### Account (Person Account) = the learner

Identity: zBU_BUID__c (personid), FirstName/MiddleName/LastName, PersonBirthdate, PersonPronouns, PersonEmail/PersonMobilePhone/PersonHomePhone.

Rollup __pc fields (from the PE set / current term):

- zBU_CareerAudience__pc
- zBU_SchoolCollegeAudience__pc
- zBU_Academic_Plan_Audience__pc
- zBU_Academic_Program_Audience__pc
- zBU_Admit_Type_Audience__pc
- zBU_EnrollmentStatusAudience__pc
- zBU_ProgramActionAudience__pc
- zBU_ProgramStatusAudience__pc
- zBU_Class_Standing__pc
- zBU_Admit_Term__pc
- zBU_Academic_Term__pc
- zBU_Billing_Career__pc
- zBU_WithdrawalStatus__pc
- zBU_Enrolled_in_Current_Term__pc
- zBU_Current_Term_Classes__pc
- zBU_Next_Term_Classes__pc
- zBU_Student_Service_Indicators__pc
- zBU_Active_User__pc

Note: Primary Academic Program, Expected Graduation Term, Withdrawal Date, and Degree Conferral Date map to LearnerProgram, not Account.

### ContactProfile

- zBU_Country_of_Citizenship__c
- zBU_US_Permanent_Resident__c
- zBU_Student_Group__c
- IsFirstGenerationStudent
- zBU_Housing_Interest__c
- zBU__Citizenship_Status__c
- zBU_Financial_Aid_Eligible__c

### ContactPointEmail / ContactPointPhone / Contactpointaddress

- Email: EmailAddress, IsPrimary
- Phone: TelephoneNumber
- Mailing address: City / State / Country

## Rules of thumb for EDF mode

- One LearnerProgram + one LearningProgramPlan + one AcademicTermEnrollment per selected PE (same PE set as EDA mode — supersession/dedup applied first).
- One shared Person Account (+ ContactProfile + ContactPoint* rows) per student, carrying all audience rollups.
- Superseded/dropped plans produce no EDF objects, same as EDA mode.
- Dedup/external-ID on the plan side: LearningProgramPlan.zBU_External_ID__c from plan code; LearnerProgram.zBU_Enrollment_Id__c = {emplid}_{plancode}.
