**SMS Platform**

Database Schema - All Tables

Column · Type · Description | MySQL 8.x | v2.0

**Module 1 - Schools & Auth**

**schools_school**

| **Column**    | **Data Type**   | **Description**                  |
| ------------- | --------------- | -------------------------------- |
| id            | UUID PK         | Primary key, auto-generated UUID |
| name          | VARCHAR(200)    | Full school name                 |
| slug          | VARCHAR(100) UQ | Subdomain key e.g. stxaviers     |
| address       | TEXT            | School address, nullable         |
| phone         | VARCHAR(20)     | Contact phone, nullable          |
| email         | VARCHAR(254)    | Contact email, nullable          |
| logo          | VARCHAR(255)    | Logo image path, nullable        |
| academic_year | VARCHAR(9)      | Current year e.g. 2025-26        |
| is_active     | TINYINT(1)      | 0=inactive, 1=active             |
| created_at    | DATETIME        | Auto-set on insert               |

**accounts_schooluser**

| **Column**        | **Data Type**   | **Description**                         |
| ----------------- | --------------- | --------------------------------------- |
| id                | INT PK AI       | Auto-increment primary key              |
| school_id         | UUID FK         | FK → schools_school.id                  |
| username          | VARCHAR(150) UQ | Login username                          |
| email             | VARCHAR(254)    | User email                              |
| first_name        | VARCHAR(150)    | First name                              |
| last_name         | VARCHAR(150)    | Last name                               |
| role              | VARCHAR(20)     | management / teacher / student / parent |
| phone             | VARCHAR(20)     | Mobile number, nullable                 |
| profile_photo     | VARCHAR(255)    | Path: schools/{uuid}/profiles/{file}    |
| is_platform_admin | TINYINT(1)      | 1=ops bypass, ignores school scope      |
| is_active         | TINYINT(1)      | 0=deactivated account                   |
| password          | VARCHAR(128)    | Django hashed password                  |
| date_joined       | DATETIME        | Auto-set on create                      |
| last_login        | DATETIME        | Updated on each login                   |

**authtoken_token**

| **Column** | **Data Type**  | **Description**             |
| ---------- | -------------- | --------------------------- |
| key        | VARCHAR(40) PK | DRF auth token              |
| user_id    | INT FK         | FK → accounts_schooluser.id |
| created    | DATETIME       | Token creation time         |

**Module 2 - Students**

**students_student**

| **Column**        | **Data Type** | **Description**                      |
| ----------------- | ------------- | ------------------------------------ |
| id                | INT PK AI     | Auto-increment primary key           |
| school_id         | UUID FK       | FK → schools_school.id               |
| user_id           | INT FK UQ     | FK → accounts_schooluser.id (1-to-1) |
| student_id        | VARCHAR(20)   | School-issued ID e.g. STU-2025-001   |
| date_of_birth     | DATE          | Student DOB                          |
| gender            | VARCHAR(10)   | Male / Female / Other                |
| blood_group       | VARCHAR(5)    | A+, O-, etc. Nullable                |
| address           | TEXT          | Home address                         |
| admission_date    | DATE          | Date of school admission             |
| current_class_id  | INT FK        | FK → classes_class.id, nullable      |
| parent_id         | INT FK        | FK → parents_parent.id, nullable     |
| emergency_contact | VARCHAR(20)   | Emergency phone number               |
| is_active         | TINYINT(1)    | 0=left school                        |
| created_at        | DATETIME      | Auto-set on insert                   |

**Module 3 - Teachers**

**teachers_teacher**

| **Column**       | **Data Type** | **Description**                        |
| ---------------- | ------------- | -------------------------------------- |
| id               | INT PK AI     | Auto-increment primary key             |
| school_id        | UUID FK       | FK → schools_school.id                 |
| user_id          | INT FK UQ     | FK → accounts_schooluser.id (1-to-1)   |
| teacher_id       | VARCHAR(20)   | School-issued ID e.g. TCH-2025-001     |
| date_of_joining  | DATE          | Employment start date                  |
| qualification    | VARCHAR(200)  | Highest qualification e.g. B.Ed, M.Sc  |
| specialization   | VARCHAR(200)  | Subject specialization                 |
| experience_years | SMALLINT      | Years of teaching experience           |
| designation      | VARCHAR(100)  | Class Teacher / HOD / Vice Principal   |
| is_class_teacher | TINYINT(1)    | 1=assigned as class teacher of a class |
| salary_grade     | VARCHAR(20)   | Pay grade code e.g. PG-3, nullable     |
| is_active        | TINYINT(1)    | 0=resigned/retired                     |

**Module 4 - Classes**

**classes_subject**

| **Column**  | **Data Type** | **Description**               |
| ----------- | ------------- | ----------------------------- |
| id          | INT PK AI     | Auto-increment primary key    |
| school_id   | UUID FK       | FK → schools_school.id        |
| name        | VARCHAR(100)  | Subject name e.g. Mathematics |
| code        | VARCHAR(20)   | Subject code e.g. MATH10      |
| is_elective | TINYINT(1)    | 1=elective, 0=compulsory      |

**classes_class**

| **Column**       | **Data Type** | **Description**                    |
| ---------------- | ------------- | ---------------------------------- |
| id               | INT PK AI     | Auto-increment primary key         |
| school_id        | UUID FK       | FK → schools_school.id             |
| name             | VARCHAR(20)   | Display name e.g. 10-A             |
| grade            | SMALLINT      | Numeric grade 1-12                 |
| section          | VARCHAR(5)    | Section A / B / C                  |
| academic_year    | VARCHAR(9)    | e.g. 2025-26                       |
| class_teacher_id | INT FK        | FK → teachers_teacher.id, nullable |
| room_number      | VARCHAR(20)   | Assigned room, nullable            |
| capacity         | SMALLINT      | Max student count, default 40      |
| is_active        | TINYINT(1)    | 0=archived                         |

**classes_teachersubject**

| **Column**        | **Data Type** | **Description**                 |
| ----------------- | ------------- | ------------------------------- |
| id                | INT PK AI     | Auto-increment primary key      |
| school_id         | UUID FK       | FK → schools_school.id          |
| teacher_id        | INT FK        | FK → teachers_teacher.id        |
| subject_id        | INT FK        | FK → classes_subject.id         |
| assigned_class_id | INT FK        | FK → classes_class.id           |
| academic_year     | VARCHAR(9)    | e.g. 2025-26                    |
| periods_per_week  | SMALLINT      | Weekly periods count, default 5 |

**Module 5 - Attendance**

**attendance_attendance**

| **Column**   | **Data Type** | **Description**                              |
| ------------ | ------------- | -------------------------------------------- |
| id           | INT PK AI     | Auto-increment primary key                   |
| school_id    | UUID FK       | FK → schools_school.id                       |
| student_id   | INT FK        | FK → students_student.id                     |
| class_obj_id | INT FK        | FK → classes_class.id                        |
| subject_id   | INT FK        | FK → classes_subject.id, nullable            |
| date         | DATE          | Attendance date                              |
| status       | CHAR(1)       | P=Present, A=Absent, L=Late, E=Excused       |
| marked_by_id | INT FK        | FK → teachers_teacher.id, nullable           |
| marked_at    | DATETIME      | Auto-set when record created                 |
| is_locked    | TINYINT(1)    | 1=locked after 48h, only management can edit |
| note         | TEXT          | Optional teacher note e.g. sick leave        |

**Module 6 - Calendar & Events**

**calendar_app_calendarevent**

| **Column**    | **Data Type** | **Description**                             |
| ------------- | ------------- | ------------------------------------------- |
| id            | INT PK AI     | Auto-increment primary key                  |
| school_id     | UUID FK       | FK → schools_school.id                      |
| title         | VARCHAR(200)  | Event title                                 |
| event_type    | VARCHAR(20)   | holiday / exam / event / ptm / activity     |
| start_date    | DATE          | Event start date                            |
| end_date      | DATE          | Event end date (=start_date for single-day) |
| description   | TEXT          | Optional details, nullable                  |
| created_by_id | INT FK        | FK → accounts_schooluser.id, nullable       |
| created_at    | DATETIME      | Auto-set on insert                          |

**calendar_app_calendarevent_target_classes (M2M)**

| **Column**       | **Data Type** | **Description**                    |
| ---------------- | ------------- | ---------------------------------- |
| id               | INT PK AI     | Auto-increment primary key         |
| calendarevent_id | INT FK        | FK → calendar_app_calendarevent.id |
| class_id         | INT FK        | FK → classes_class.id              |

**Module 7 - Fees Tracking**

**fees_feestructure**

| **Column**    | **Data Type** | **Description**                                    |
| ------------- | ------------- | -------------------------------------------------- |
| id            | INT PK AI     | Auto-increment primary key                         |
| school_id     | UUID FK       | FK → schools_school.id                             |
| class_obj_id  | INT FK        | FK → classes_class.id. NULL=applies to all classes |
| academic_year | VARCHAR(9)    | e.g. 2025-26                                       |
| fee_type      | VARCHAR(50)   | Tuition / Transport / Exam / Library / Sports      |
| amount        | DECIMAL(10,2) | Fee amount in INR                                  |
| is_recurring  | TINYINT(1)    | 1=repeating, 0=one-time                            |
| frequency     | VARCHAR(20)   | monthly / quarterly / annual / one_time            |
| due_day       | SMALLINT      | Day of month fee is due e.g. 10                    |

**fees_feerecord**

| **Column**       | **Data Type** | **Description**                          |
| ---------------- | ------------- | ---------------------------------------- |
| id               | INT PK AI     | Auto-increment primary key               |
| school_id        | UUID FK       | FK → schools_school.id                   |
| student_id       | INT FK        | FK → students_student.id                 |
| fee_structure_id | INT FK        | FK → fees_feestructure.id                |
| due_date         | DATE          | Payment due date                         |
| amount_due       | DECIMAL(10,2) | Total amount expected                    |
| amount_paid      | DECIMAL(10,2) | Amount received so far, default 0        |
| status           | VARCHAR(10)   | pending / partial / paid / waived        |
| paid_date        | DATE          | Date payment was received, nullable      |
| payment_mode     | VARCHAR(30)   | cash / cheque / upi / bank_transfer / dd |
| reference_no     | VARCHAR(100)  | Cheque no / UTR / DD no, nullable        |
| recorded_by_id   | INT FK        | FK → accounts_schooluser.id, nullable    |
| waiver_reason    | TEXT          | Required if status=waived, nullable      |
| note             | TEXT          | Optional remark, nullable                |
| created_at       | DATETIME      | Auto-set on insert                       |
| updated_at       | DATETIME      | Auto-updated on save                     |

**Module 8 - Teacher Payroll Tracking**

**payroll_salarystructure**

| **Column**      | **Data Type** | **Description**                     |
| --------------- | ------------- | ----------------------------------- |
| id              | INT PK AI     | Auto-increment primary key          |
| school_id       | UUID FK       | FK → schools_school.id              |
| teacher_id      | INT FK        | FK → teachers_teacher.id            |
| effective_from  | DATE          | Date this structure takes effect    |
| basic           | DECIMAL(10,2) | Basic monthly salary                |
| hra             | DECIMAL(10,2) | House Rent Allowance, default 0     |
| ta              | DECIMAL(10,2) | Transport Allowance, default 0      |
| other_allowance | DECIMAL(10,2) | Any other allowance, default 0      |
| pf_deduction    | DECIMAL(10,2) | Provident Fund deduction, default 0 |
| tds_deduction   | DECIMAL(10,2) | Tax Deducted at Source, default 0   |
| other_deduction | DECIMAL(10,2) | Any other deduction, default 0      |

**payroll_payrollrecord**

| **Column**          | **Data Type** | **Description**                                |
| ------------------- | ------------- | ---------------------------------------------- |
| id                  | INT PK AI     | Auto-increment primary key                     |
| school_id           | UUID FK       | FK → schools_school.id                         |
| teacher_id          | INT FK        | FK → teachers_teacher.id                       |
| salary_structure_id | INT FK        | FK → payroll_salarystructure.id, nullable      |
| pay_period_year     | SMALLINT      | Year e.g. 2026                                 |
| pay_period_month    | SMALLINT      | Month 1-12                                     |
| working_days        | SMALLINT      | Total working days in the month, default 26    |
| days_present        | SMALLINT      | Actual days teacher was present                |
| gross_pay           | DECIMAL(10,2) | Gross before deductions                        |
| total_deductions    | DECIMAL(10,2) | Sum of all deductions incl. LOP                |
| lop_deduction       | DECIMAL(10,2) | Loss of Pay = (gross/working_days)\*(abs days) |
| net_pay             | DECIMAL(10,2) | gross_pay − total_deductions                   |
| status              | VARCHAR(10)   | pending / paid / held                          |
| paid_date           | DATE          | Date salary was disbursed, nullable            |
| payment_mode        | VARCHAR(30)   | bank_transfer / cheque / cash                  |
| reference_no        | VARCHAR(100)  | Bank UTR / cheque number, nullable             |
| note                | TEXT          | Optional remark, nullable                      |
| recorded_by_id      | INT FK        | FK → accounts_schooluser.id, nullable          |
| created_at          | DATETIME      | Auto-set on insert                             |

**Module 9 - Parents**

**parents_parent**

| **Column**          | **Data Type** | **Description**                      |
| ------------------- | ------------- | ------------------------------------ |
| id                  | INT PK AI     | Auto-increment primary key           |
| school_id           | UUID FK       | FK → schools_school.id               |
| user_id             | INT FK UQ     | FK → accounts_schooluser.id (1-to-1) |
| occupation          | VARCHAR(100)  | Parent occupation, nullable          |
| relation_to_student | VARCHAR(20)   | Father / Mother / Guardian           |
| annual_income       | DECIMAL(12,2) | Annual income, nullable              |

**Unique Constraints Summary**

| **Table**              | **Unique Together**                                      |
| ---------------------- | -------------------------------------------------------- |
| schools_school         | slug                                                     |
| accounts_schooluser    | username                                                 |
| students_student       | school_id, student_id                                    |
| teachers_teacher       | school_id, teacher_id                                    |
| classes_subject        | school_id, code                                          |
| classes_class          | school_id, grade, section, academic_year                 |
| classes_teachersubject | school_id, teacher_id, subject_id, assigned_class_id     |
| attendance_attendance  | school_id, student_id, date, subject_id                  |
| fees_feestructure      | school_id, class_obj_id, academic_year, fee_type         |
| payroll_payrollrecord  | school_id, teacher_id, pay_period_year, pay_period_month |

**Index Recommendations**

| **Table**                  | **Index on**                                         |
| -------------------------- | ---------------------------------------------------- |
| All tables                 | school_id (present on every table - always index)    |
| students_student           | school_id, current_class_id                          |
| attendance_attendance      | school_id, date \| school_id, student_id             |
| fees_feerecord             | school_id, status \| school_id, student_id, due_date |
| payroll_payrollrecord      | school_id, pay_period_year, pay_period_month         |
| calendar_app_calendarevent | school_id, start_date                                |
| classes_teachersubject     | school_id, teacher_id                                |

SMS Platform - Database Schema Reference | v2.0 | MySQL 8.x