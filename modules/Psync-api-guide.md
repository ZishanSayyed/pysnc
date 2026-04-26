# PSync API — End-to-End Testing Guide

Complete walkthrough from creating a school to adding students, parents, teachers, classes, and subjects.  
Follow the steps **in order** — each step depends on IDs from the previous one.

---

## Setup

| Item | Value |
|---|---|
| Base URL | `http://127.0.0.1:8000` |
| School Slug Header | `X-School-Slug: greenwood` *(use your slug)* |
| Auth Header | `Authorization: Bearer YOUR_TOKEN` |
| Content-Type (JSON) | `Content-Type: application/json` |

> 💡 Save the `access` token from Step 2, and IDs returned from each step — you'll need them later.

---

## PHASE 1 — Platform Setup

### Step 1 — Login as Platform Admin
> The platform admin creates schools. This user is created via Django admin or `createsuperuser`.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "platformadmin",
    "password": "admin123"
  }'
```

**Expected response:**
```json
{
  "access": "eyJ...",
  "role": "management",
  "school": null
}
```
> Save the `access` value as `PLATFORM_TOKEN`.

---

### Step 2 — Create a School
> Only platform admins (`is_platform_admin=true`) can create schools.  
> No `X-School-Slug` header needed here.

```bash
curl -X POST http://127.0.0.1:8000/api/schools/ \
  -H "Authorization: Bearer PLATFORM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Greenwood International School",
    "slug": "greenwood",
    "address": "123 MG Road, Mumbai, Maharashtra",
    "phone": "9876500000",
    "email": "admin@greenwood.edu",
    "academic_year": "2025-26"
  }'
```

**Expected response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Greenwood International School",
  "slug": "greenwood",
  "address": "123 MG Road, Mumbai, Maharashtra",
  "phone": "9876500000",
  "email": "admin@greenwood.edu",
  "academic_year": "2025-26",
  "is_active": true,
  "created_at": "2025-06-01T10:00:00Z"
}
```
> Save the `id` as `SCHOOL_UUID`.

---

### Step 3 — Create School Management Admin User
> Create the management user for this school via Django shell or admin panel,  
> then use this user to do all school-level operations below.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/users/create/ \
  -H "Authorization: Bearer PLATFORM_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "username": "greenwood.admin",
    "email": "mgmt@greenwood.edu",
    "password": "mgmt@123",
    "role": "management",
    "first_name": "Ravi",
    "last_name": "Sharma",
    "phone": "9876500001"
  }'
```

---

### Step 4 — Login as School Management
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "greenwood.admin",
    "password": "mgmt@123"
  }'
```

**Expected response:**
```json
{
  "access": "eyJ...",
  "role": "management",
  "school": "greenwood"
}
```
> Save this as `MGMT_TOKEN`. Use this for all remaining steps.

---

## PHASE 2 — School Structure

### Step 5 — Verify Who I Am
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

**Expected response:**
```json
{
  "id": 2,
  "username": "greenwood.admin",
  "email": "mgmt@greenwood.edu",
  "role": "management",
  "school": "greenwood"
}
```

---

### Step 6 — Create Subjects
> Subjects are global — shared across schools.

**Mathematics:**
```bash
curl -X POST http://127.0.0.1:8000/api/teachers/subjects/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"name": "Mathematics", "code": "MATH01"}'
```

**English:**
```bash
curl -X POST http://127.0.0.1:8000/api/teachers/subjects/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"name": "English", "code": "ENG01"}'
```

**Science:**
```bash
curl -X POST http://127.0.0.1:8000/api/teachers/subjects/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"name": "Science", "code": "SCI01"}'
```

**Expected response:**
```json
{
  "id": 1,
  "name": "Mathematics",
  "code": "MATH01"
}
```
> Save subject IDs: `MATH_ID=1`, `ENG_ID=2`, `SCI_ID=3`

---

### Step 7 — List All Subjects
```bash
curl -X GET http://127.0.0.1:8000/api/teachers/subjects/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

## PHASE 3 — Add Users (Bulk)

### Step 8 — Bulk Upload All Users via CSV

Create a file called `users.csv`:
```
username,email,password,role,first_name,last_name,phone
bob.teacher,bob@greenwood.edu,teach@123,teacher,Bob,Brown,9876543201
alice.teacher,alice@greenwood.edu,teach@123,teacher,Alice,Green,9876543202
john.student,john@greenwood.edu,stu@123,student,John,Doe,9876543203
jane.student,jane@greenwood.edu,stu@123,student,Jane,Smith,9876543204
mary.parent,mary@greenwood.edu,par@123,parent,Mary,Jones,9876543205
```

```bash
curl -X POST http://127.0.0.1:8000/api/auth/users/bulk-upload/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood" \
  -F "file=@users.csv"
```

**Expected response:**
```json
{
  "created": 5,
  "errors": 0,
  "error_details": []
}
```
> ✅ Signal auto-creates: 2 Teacher profiles, 2 Student placeholders, 1 Parent profile.

---

### Step 9 — List All Users
```bash
curl -X GET http://127.0.0.1:8000/api/auth/users/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

## PHASE 4 — Teachers

### Step 10 — List Teachers
```bash
curl -X GET http://127.0.0.1:8000/api/teachers/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

**Expected response:**
```json
[
  {
    "id": 1,
    "employee_id": null,
    "full_name": "Bob Brown",
    "email": "bob@greenwood.edu",
    "qualification": null,
    "joining_date": null,
    "is_active": true,
    "schools_count": 0
  },
  ...
]
```
> Save teacher IDs: `BOB_ID=1`, `ALICE_ID=2`

---

### Step 11 — Update Teacher Profile (Bob)
```bash
curl -X PATCH http://127.0.0.1:8000/api/teachers/1/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "employee_id": "EMP-001",
    "qualification": "M.Sc Mathematics",
    "joining_date": "2023-06-01"
  }'
```

---

### Step 12 — Assign Bob to School + Subject (Maths)
```bash
curl -X POST http://127.0.0.1:8000/api/teachers/1/assign/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "school": "550e8400-e29b-41d4-a716-446655440000",
    "subject": 1,
    "assigned_class": null
  }'
```

**Expected response:**
```json
{
  "id": 1,
  "school": "550e8400-...",
  "school_name": "Greenwood International School",
  "subject": 1,
  "subject_name": "Mathematics",
  "assigned_class": null,
  "is_active": true,
  "assigned_at": "2025-06-01T10:30:00Z"
}
```

---

### Step 13 — Assign Bob to English Too (same school, different subject)
```bash
curl -X POST http://127.0.0.1:8000/api/teachers/1/assign/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "school": "550e8400-e29b-41d4-a716-446655440000",
    "subject": 2,
    "assigned_class": null
  }'
```

---

### Step 14 — View Bob's Full Profile + All Assignments
```bash
curl -X GET http://127.0.0.1:8000/api/teachers/1/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

**Expected response:**
```json
{
  "id": 1,
  "full_name": "Bob Brown",
  "email": "bob@greenwood.edu",
  "employee_id": "EMP-001",
  "qualification": "M.Sc Mathematics",
  "joining_date": "2023-06-01",
  "is_active": true,
  "assignments": [
    { "subject_name": "Mathematics", "school_name": "Greenwood International School" },
    { "subject_name": "English",     "school_name": "Greenwood International School" }
  ]
}
```

---

### Step 15 — List All Assignments for School
```bash
curl -X GET http://127.0.0.1:8000/api/teachers/assignments/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

## PHASE 5 — Students

### Step 16 — List Students (Placeholders)
```bash
curl -X GET http://127.0.0.1:8000/api/students/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```
> You'll see John & Jane with placeholder `student_id` values like `STU-3`, `STU-4`.

---

### Step 17 — Bulk Upload Student Details via CSV

Create `students.csv`:
```
email,first_name,last_name,student_id,date_of_birth,gender,address,admission_date,emergency_contact,blood_group
john@greenwood.edu,John,Doe,STU-001,2010-05-12,Male,"123 MG Road, Mumbai",2024-01-10,9876500010,B+
jane@greenwood.edu,Jane,Smith,STU-002,2011-03-22,Female,"456 Park St, Delhi",2024-01-10,9876500011,O+
```

```bash
curl -X POST http://127.0.0.1:8000/api/students/bulk-upload/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood" \
  -F "file=@students.csv"
```

**Expected response:**
```json
{
  "created": 0,
  "updated": 2,
  "errors": 0,
  "error_rows": []
}
```

---

### Step 18 — View Student Detail
```bash
curl -X GET http://127.0.0.1:8000/api/students/1/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

### Step 19 — Search Students by Name
```bash
curl -X GET "http://127.0.0.1:8000/api/students/?search=john" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

### Step 20 — Create Single Student Manually
```bash
curl -X POST http://127.0.0.1:8000/api/auth/users/create/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "username": "raj.student",
    "email": "raj@greenwood.edu",
    "password": "stu@123",
    "role": "student",
    "first_name": "Raj",
    "last_name": "Patel",
    "phone": "9876543206"
  }'
```
> ✅ Signal fires → Student placeholder auto-created.

---

## PHASE 6 — Parents

### Step 21 — List Parents
```bash
curl -X GET http://127.0.0.1:8000/api/parents/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

**Expected response:**
```json
[
  {
    "id": 1,
    "full_name": "Mary Jones",
    "email": "mary@greenwood.edu",
    "phone": "9876543205",
    "relationship": "guardian",
    "is_active": true,
    "children_count": 0
  }
]
```

---

### Step 22 — Update Parent Profile
```bash
curl -X PUT http://127.0.0.1:8000/api/parents/1/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "phone": "9876543299",
    "occupation": "Engineer",
    "relationship": "mother"
  }'
```

---

### Step 23 — Link Parent to Student
> Update the Student record to set the `parent` FK.  
> `MARY_PARENT_ID=1`, `JOHN_STUDENT_ID=1`

```bash
curl -X PUT http://127.0.0.1:8000/api/students/1/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "parent": 1
  }'
```

---

### Step 24 — View Parent's Children
```bash
curl -X GET http://127.0.0.1:8000/api/parents/1/children/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

**Expected response:**
```json
[
  {
    "id": 1,
    "student_id": "STU-001",
    "full_name": "John Doe",
    "class_name": null,
    "gender": "Male",
    "admission_date": "2024-01-10",
    "is_active": true
  }
]
```

---

## PHASE 7 — Verify Everything

### Step 25 — Login as Teacher and List Students
```bash
# Login as Bob
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "bob.teacher", "password": "teach@123"}'
```

```bash
# Bob lists students (teachers have read access)
curl -X GET http://127.0.0.1:8000/api/students/ \
  -H "Authorization: Bearer BOB_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

### Step 26 — Login as Parent and Check Own Profile
```bash
# Login as Mary
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "mary.parent", "password": "par@123"}'
```

```bash
# Mary views herself
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer MARY_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

## Quick Reference — All Endpoints

| # | Method | URL | Auth | Description |
|---|---|---|---|---|
| 1 | POST | `/api/auth/login/` | None | Login, get JWT |
| 2 | GET | `/api/auth/me/` | Any | Current user info |
| 3 | GET | `/api/auth/users/` | Management | List all school users |
| 4 | POST | `/api/auth/users/create/` | Management | Create single user |
| 5 | PUT | `/api/auth/users/{id}/` | Management | Update user |
| 6 | POST | `/api/auth/users/bulk-upload/` | Management | Bulk create users via CSV |
| 7 | PUT | `/api/auth/users/bulk-update/` | Management | Bulk update users via JSON |
| 8 | POST | `/api/schools/` | Platform Admin | Create school |
| 9 | GET | `/api/schools/` | Platform Admin | List all schools |
| 10 | GET | `/api/schools/{uuid}/` | Authenticated | School detail |
| 11 | PUT | `/api/schools/{uuid}/` | Authenticated | Update school |
| 12 | GET | `/api/students/` | Mgmt / Teacher | List students |
| 13 | GET | `/api/students/?search=name` | Mgmt / Teacher | Search students |
| 14 | GET | `/api/students/?class_id=1` | Mgmt / Teacher | Filter by class |
| 15 | GET | `/api/students/{id}/` | Mgmt / Teacher | Student detail |
| 16 | POST | `/api/students/` | Management | Create student |
| 17 | PUT | `/api/students/{id}/` | Management | Update student |
| 18 | POST | `/api/students/bulk-upload/` | Management | Bulk fill student details |
| 19 | GET | `/api/parents/` | Mgmt / Teacher | List parents |
| 20 | GET | `/api/parents/{id}/` | Mgmt / Teacher | Parent detail |
| 21 | PUT | `/api/parents/{id}/` | Management | Update parent |
| 22 | GET | `/api/parents/{id}/children/` | Mgmt / Teacher | Parent's students |
| 23 | GET | `/api/teachers/` | Mgmt / Teacher | List teachers |
| 24 | GET | `/api/teachers/{id}/` | Mgmt / Teacher | Teacher + assignments |
| 25 | PUT | `/api/teachers/{id}/` | Management | Update teacher |
| 26 | POST | `/api/teachers/{id}/assign/` | Management | Assign to school+subject |
| 27 | GET | `/api/teachers/{id}/assignments/` | Mgmt / Teacher | Teacher's assignments |
| 28 | GET | `/api/teachers/assignments/` | Management | All school assignments |
| 29 | GET | `/api/teachers/subjects/` | Mgmt / Teacher | List subjects |
| 30 | POST | `/api/teachers/subjects/` | Management | Create subject |

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `"school": null` in token response | User has no school assigned | Assign school when creating user |
| `403 Forbidden` | Wrong role for endpoint | Use management token |
| `No file provided` | CSV not attached | Use `-F "file=@filename.csv"` |
| `no such column` | Migration not applied | Run `python manage.py migrate` or use the shell ALTER fix |
| `Invalid credentials` | Wrong username/password | Check the exact username used at creation |


## Remaining Modules 
-- MODULE 4 — Class Profiles
-- MODULE 5 — Attendance
-- MODULE 6 — Calendar & Events
-- MODULE 7 — Fees Tracking