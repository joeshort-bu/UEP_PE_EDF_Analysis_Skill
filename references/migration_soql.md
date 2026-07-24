# Migration SOQL reference

Extraction queries for pulling EDA (source) and EDF (target) records for PE
analysis and migration validation.

> **BUID field name is environment-specific.** These queries assume the Contact
> BUID field is `zBU_BUID__c`. On a Person-Account org the field may be
> `zBU_BUID__pc`. Confirm the API name in your org before running (see SETUP.md)
> and substitute accordingly. Replace `{BUID}` with the actual value — never hand
> the user a query with a literal `{BUID}` placeholder still in it.

## EDA side (source)

### Contact (single, by BUID)

```sql
SELECT Id, Name, FirstName, LastName, Email, AccountId, zBU_BUID__c
FROM Contact
WHERE zBU_BUID__c = '{BUID}'
```

### Program Enrollments for a Contact

```sql
SELECT Id, Name, hed__Contact__c, hed__Account__c, zBU_SchoolCollege__c, zBU_Academic_Program_Code__c, zBU_Student_Type__c, zBU_ProgramStatus__c, zBU_ProgramAction__c, zBU_Program_Type__c, zBU_Effective_Date__c, zBU_Admit_Term__c, zBU_Admit_Type__c, zBU_Mutual_Accept_Date__c, hed__Enrollment_Status__c, hed__Class_Standing__c, zBU_Additional_Program_of_Study__c, zBU_PE_External_ID__c
FROM hed__Program_Enrollment__c
WHERE hed__Contact__r.zBU_BUID__c = '{BUID}'
```

### Bulk Program Enrollments (explicit fields, all records)

Drop the WHERE filter or scope it to a batch. Use for the bulk exception-list
flow (dupes, terminal-to-retire, unmapped fields, rollup issues).

```sql
SELECT Id, Name, hed__Contact__r.zBU_BUID__c, hed__Account__c, zBU_SchoolCollege__c, zBU_Academic_Program_Code__c, zBU_Student_Type__c, zBU_ProgramStatus__c, zBU_ProgramAction__c, zBU_Program_Type__c, zBU_Effective_Date__c, zBU_Admit_Term__c, zBU_Admit_Type__c, zBU_Mutual_Accept_Date__c, hed__Enrollment_Status__c, hed__Class_Standing__c, zBU_Additional_Program_of_Study__c, zBU_PE_External_ID__c
FROM hed__Program_Enrollment__c
WHERE hed__Contact__r.zBU_BUID__c != null
```

## EDF side (target)

### Account (Person Account, by BUID)

```sql
SELECT Id, Name, FirstName, MiddleName, LastName, PersonEmail, PersonBirthdate, PersonPronouns, zBU_BUID__pc
FROM Account
WHERE zBU_BUID__pc = '{BUID}'
```

Note: `MiddleName` and `Sync_Contact_with_SFMC__pc` are EDF-side target fields
that appear in the crosswalk workbook; they have not been confirmed present the
way the EDA-side gaps have. Validate against your org before relying on them.

### LearnerProgram for an Account

```sql
SELECT Id, Name, LearnerContactId, LearningProgramPlanId, LearnerAccountId, Status, zBU_Admit_Type__c, zBU_Student_Type__c, zBU_Academic_Program_Code__c, zBU_Program_Action__c, zBU_Effective_Date__c, zBU_Admit_Term__c, zBU_Primary_Academic_Program__c, zBU_Expected_Graduation_Term__c, zBU_Withdrawal_Date__c, zBU_Degree_Conferral_Date__c, zBU_Enrollment_Id__c
FROM LearnerProgram
WHERE LearnerContactId = '{ACCOUNT_ID}'
```

## ContactPoint detail (EDF)

### ContactPointEmail

```sql
SELECT Id, EmailAddress, IsPrimary
FROM ContactPointEmail
WHERE Id != null
```

### ContactPointPhone

```sql
SELECT Id, TelephoneNumber
FROM ContactPointPhone
WHERE Id != null
```

### Contactpointaddress

```sql
SELECT Id, City, State, Country
FROM Contactpointaddress
WHERE Id != null
```
